import json
import logging
import re
from app.llm import llm
from app.prompts import SENTIMENT_ANALYSIS_PROMPT, GENERAL_SENTIMENT_PROMPT

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
    Optimized LLM analysis với text preprocessing và error handling
    """
    try:
        input_data = state["input_data"]
        merged_text = state["merged_text"]
        main_keywords = input_data.get("main_keywords", [])
        
        # Early exit nếu text quá ngắn
        if len(merged_text.strip()) < 5:
            logger.info("Text too short, returning neutral sentiment")
            return {
                **state, 
                "llm_analysis": {
                    "sentiment": "neutral",
                    "confidence": 0.1,
                    "keywords": {"positive": [], "negative": [], "neutral": []},
                    "explanation": "Nội dung quá ngắn để phân tích"
                }
            }
        
        # Preprocessing text để tối ưu LLM
        processed_text = preprocess_text(merged_text)
        
        # Sử dụng main_keywords trực tiếp
        all_keywords = main_keywords
        topic_name = main_keywords[0] if main_keywords else "Unknown"
        
        # Check if keywords are mentioned
        keywords_mentioned = main_keywords and any(keyword.lower() in processed_text.lower() for keyword in all_keywords)
        
        if not keywords_mentioned:
            logger.info("No keywords mentioned, analyzing general sentiment")
            # Analyze general sentiment when keywords are not mentioned
            general_analysis = analyze_general_sentiment(processed_text)
            general_analysis["explanation"] = f"Nội dung không đề cập đến main keywords. {general_analysis['explanation']}"
            return {**state, "llm_analysis": general_analysis}
        
        logger.debug(f"Analyzing keywords: {main_keywords}, text length: {len(processed_text)}")
        
        # Tạo prompt tối ưu
        prompt = SENTIMENT_ANALYSIS_PROMPT.format(
            topic_name=topic_name,
            keywords=all_keywords[:10],  # Limit keywords để giảm token
            text=processed_text[:1000]   # Limit text length
        )
        
        # Gọi LLM với retry logic
        response = llm.invoke(prompt, config=get_invoke_config())
        
        # Parse và validate JSON response
        analysis_result = parse_llm_response(response.content)
        
        logger.debug(f"LLM analysis: sentiment={analysis_result.get('sentiment')}")
        
        return {**state, "llm_analysis": analysis_result}
        
    except Exception as e:
        logger.error(f"LLM analysis error: {str(e)}")
        # Fallback response
        return {
            **state,
            "llm_analysis": {
                "sentiment": "neutral",
                "confidence": 0.0,
                "keywords": {"positive": [], "negative": [], "neutral": []},
                "explanation": "Lỗi xử lý, không thể phân tích"
            }
        }

def preprocess_text(text: str) -> str:
    """Preprocessing text để tối ưu cho LLM"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters but keep Vietnamese
    text = re.sub(r'[^\w\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', ' ', text)
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text.strip())
    
    return text

def parse_llm_response(response_content: str) -> dict:
    """Parse và validate LLM response với fallback"""
    try:
        # Clean response content
        cleaned_content = response_content.strip()
        
        # Try to extract JSON from response if it's wrapped in text
        json_match = re.search(r'\{.*\}', cleaned_content, re.DOTALL)
        if json_match:
            cleaned_content = json_match.group(0)
        
        # Try direct JSON parse
        result = json.loads(cleaned_content)
        
        # Validate required fields
        required_fields = ["sentiment", "confidence", "keywords", "explanation"]
        for field in required_fields:
            if field not in result:
                raise ValueError(f"Missing field: {field}")
        
        # Validate sentiment values
        if result["sentiment"] not in ["positive", "negative", "neutral"]:
            result["sentiment"] = "neutral"
        
        # Validate confidence range
        confidence = float(result.get("confidence", 0))
        result["confidence"] = max(0.0, min(1.0, confidence))
        
        # Validate keywords structure
        keywords = result.get("keywords", {})
        if not isinstance(keywords, dict):
            keywords = {"positive": [], "negative": [], "neutral": []}
        
        for key in ["positive", "negative", "neutral"]:
            if key not in keywords or not isinstance(keywords[key], list):
                keywords[key] = []
        
        result["keywords"] = keywords
        
        # Limit explanation length
        explanation = str(result.get("explanation", ""))
        result["explanation"] = explanation
        
        logger.info(f"Successfully parsed LLM response: {result['sentiment']}")
        return result
        
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        logger.error(f"JSON parse error: {str(e)}")
        logger.error(f"Raw response: {response_content[:300]}...")
        
        # Try to extract basic info from text if JSON fails
        fallback_result = extract_fallback_analysis(response_content)
        return fallback_result

def analyze_general_sentiment(text: str) -> dict:
    """Analyze general sentiment when keywords are not mentioned"""
    try:
        logger.debug(f"Analyzing general sentiment for text length: {len(text)}")
        
        # Create general sentiment prompt
        prompt = GENERAL_SENTIMENT_PROMPT.format(text=text[:800])  # Limit text length
        
        # Call LLM
        response = llm.invoke(prompt, config=get_invoke_config())
        
        # Parse response
        analysis_result = parse_llm_response(response.content)
        
        # Lower confidence since keywords are not mentioned
        analysis_result["confidence"] = min(analysis_result.get("confidence", 0.0), 0.6)
        
        logger.debug(f"General sentiment analysis: {analysis_result.get('sentiment')}")
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"General sentiment analysis error: {str(e)}")
        return {
            "sentiment": "neutral",
            "confidence": 0.1,
            "keywords": {"positive": [], "negative": [], "neutral": []},
            "explanation": "Sentiment tổng quan trung tính"
        }

def extract_fallback_analysis(response_content: str) -> dict:
    """Extract basic sentiment info from non-JSON response"""
    try:
        content_lower = response_content.lower()
        
        # Try to detect sentiment from text
        sentiment = "neutral"
        confidence = 0.1
        
        if any(word in content_lower for word in ["positive", "tích cực", "tốt", "hay"]):
            sentiment = "positive"
            confidence = 0.3
        elif any(word in content_lower for word in ["negative", "tiêu cực", "xấu", "tệ"]):
            sentiment = "negative"
            confidence = 0.3
        
        logger.warning(f"Using fallback analysis: {sentiment}")
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "keywords": {"positive": [], "negative": [], "neutral": []},
            "explanation": "Phân tích dự phòng do lỗi parse"
        }
        
    except Exception as e:
        logger.error(f"Fallback analysis error: {str(e)}")
        return {
            "sentiment": "neutral",
            "confidence": 0.0,
            "keywords": {"positive": [], "negative": [], "neutral": []},
            "explanation": "Không thể phân tích"
        }