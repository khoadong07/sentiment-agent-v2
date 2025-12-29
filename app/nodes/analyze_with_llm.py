import json
import logging
import re
from app.llm import llm
from app.prompts import TARGETED_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)

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
    Sử dụng LLM để xác định targeted và phân tích sentiment
    """
    try:
        input_data = state["input_data"]
        merged_text = state["merged_text"]
        main_keywords = input_data.get("main_keywords", [])
        post_type = input_data.get("type", "")
        
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
        
        # Tạo prompt với main_keywords và post_type
        prompt = TARGETED_ANALYSIS_PROMPT.format(
            main_keywords=", ".join(main_keywords),
            text=merged_text,
            post_type=post_type
        )
        
        # Gọi LLM
        config = get_invoke_config()
        response = llm.invoke(prompt, config=config)
        analysis_result = parse_llm_response(response.content)
        
        # Đảm bảo có đầy đủ fields
        analysis_result["index"] = input_data.get("index", "")
        
        logger.info(f"LLM analysis completed - targeted: {analysis_result.get('targeted', False)}, type: {post_type}")
        
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