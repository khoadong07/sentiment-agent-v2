import json
import logging
import re
from app.llm import llm
from app.prompts import TARGETED_ANALYSIS_PROMPT
from app.constants import COMMENT_TYPES

logger = logging.getLogger(__name__)

def check_keyword_mention(text: str, main_keywords: list) -> bool:
    """
    Kiểm tra xem text có mention đến bất kỳ main keyword nào không
    """
    if not text or not main_keywords:
        return False
    
    # Normalize text để so sánh
    text_lower = text.lower()
    
    # Check từng keyword
    for keyword in main_keywords:
        if not keyword:
            continue
            
        keyword_lower = keyword.lower().strip()
        
        # Check exact match và partial match
        if keyword_lower in text_lower:
            logger.info(f"Found mention of keyword: '{keyword}' in text")
            return True
    
    return False

def get_invoke_config():
    """
    Trả về config cho llm.invoke nếu langfuse_handler khả dụng.
    Nếu không, trả về {} để tránh NameError.
    """
    try:
        from app.langfuse import langfuse_handler  # noqa: WPS433 (dynamic import)
        return {"callbacks": [langfuse_handler]}
    except Exception:
        return {}

def analyze_with_llm(state):
    """
    Sử dụng LLM để xác định targeted và phân tích sentiment với logic mới:
    - Comment types + có content: Check content có mention main keyword không
    - Các type khác: Check merged text có mention main keyword không
    - Nếu không mention → neutral (không trả keyword)
    """
    try:
        input_data = state["input_data"]
        merged_text = state["merged_text"]
        main_keywords = input_data.get("main_keywords", [])
        post_type = input_data.get("type", "")
        content = (input_data.get("content") or "").strip()
        
        # Nếu không có main_keywords, trả về targeted = False
        if not main_keywords:
            logger.info("Không có main_keywords, targeted = False")
            return {**state, "llm_analysis": {
                "sentiment": "neutral",
                "targeted": False,
                "keywords": {"positive": [], "negative": []},
                "confidence": 0.0,
                "explanation": "Không có main_keywords để kiểm tra",
                "index": input_data.get("index", "")
            }}
        
        # Định nghĩa comment types
        comment_types = COMMENT_TYPES
        
        # Xác định text để check mention keyword
        text_to_check = ""
        if post_type in comment_types and content:
            # Comment type + có content → chỉ check content
            text_to_check = content
            logger.info(f"Comment type với content, check mention trong content: {len(content)} ký tự")
        else:
            # Các type khác → check merged text
            text_to_check = merged_text
            logger.info(f"Non-comment type hoặc không có content, check mention trong merged text: {len(merged_text)} ký tự")
        
        # Check mention keyword trước khi gọi LLM
        has_mention = check_keyword_mention(text_to_check, main_keywords)
        
        if not has_mention:
            # Không mention → trả về neutral ngay, không cần gọi LLM
            logger.info(f"Không có mention main keywords trong text, trả về neutral")
            return {**state, "llm_analysis": {
                "sentiment": "neutral",
                "targeted": False,
                "keywords": {"positive": [], "negative": []},
                "confidence": 0.0,
                "explanation": "Không mention đến main keywords",
                "index": input_data.get("index", "")
            }}
        
        # Có mention → gọi LLM để đánh sentiment
        logger.info(f"Có mention main keywords, tiến hành phân tích sentiment với LLM")
        prompt = TARGETED_ANALYSIS_PROMPT.format(
            main_keywords=", ".join(main_keywords),
            text=merged_text,  # Vẫn dùng merged_text cho LLM để có context đầy đủ
            post_type=post_type
        )
        
        # Gọi LLM
        config = get_invoke_config()
        response = llm.invoke(prompt, config=config)
        analysis_result = parse_llm_response(response.content)
        
        # Đảm bảo targeted = True vì đã check mention
        analysis_result["targeted"] = True
        analysis_result["index"] = input_data.get("index", "")
        
        # Nếu sentiment là neutral, không trả về keywords
        if analysis_result.get("sentiment") == "neutral":
            analysis_result["keywords"] = {"positive": [], "negative": []}
            logger.info("Sentiment neutral, xóa keywords")
        
        logger.info(f"LLM analysis completed - targeted: True, sentiment: {analysis_result.get('sentiment')}, type: {post_type}")
        
        return {**state, "llm_analysis": analysis_result}
        
    except Exception as e:
        logger.error(f"Error in analyze_with_llm: {str(e)}")
        return {**state, "llm_analysis": {
            "sentiment": "neutral",
            "targeted": False,
            "keywords": {"positive": [], "negative": []},
            "confidence": 0.0,
            "explanation": f"Lỗi phân tích: {str(e)}",
            "index": input_data.get("index", "")
        }}


def preprocess_text(text: str) -> str:
    """Preprocessing text để tối ưu cho LLM"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters but keep Vietnamese
    text = re.sub(r'[^\w\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', ' ', text)
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text.strip())
    
    return text

def parse_llm_response(response_text: str) -> dict:
    """
    Parse LLM response JSON với format mới
    """
    try:
        # Extract JSON từ response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            result = json.loads(json_str)
            
            # Chuẩn hóa keywords format
            keywords = result.get("keywords", {})
            if isinstance(keywords, list):
                # Nếu keywords là list, chuyển thành dict format
                keywords = {"positive": [], "negative": [], "neutral": keywords}
            elif not isinstance(keywords, dict):
                keywords = {"positive": [], "negative": []}
            
            # Đảm bảo có đầy đủ keys trong keywords (bỏ neutral để tiết kiệm token)
            for key in ["positive", "negative"]:
                if key not in keywords:
                    keywords[key] = []
            
            return {
                "sentiment": result.get("sentiment", "neutral").lower(),
                "targeted": bool(result.get("targeted", False)),
                "keywords": keywords,
                "confidence": float(result.get("confidence", 0.0)),
                "explanation": result.get("explanation", "")
            }
        
        # Fallback nếu không parse được JSON
        return {
            "sentiment": "neutral",
            "targeted": False,
            "keywords": {"positive": [], "negative": []},
            "confidence": 0.0,
            "explanation": "Không thể parse response từ LLM"
        }
        
    except Exception as e:
        logger.error(f"Error parsing LLM response: {str(e)}")
        return {
            "sentiment": "neutral",
            "targeted": False,
            "keywords": {"positive": [], "negative": []},
            "confidence": 0.0,
            "explanation": f"Lỗi parse: {str(e)}"
        }