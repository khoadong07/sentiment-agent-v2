import logging
import json
from app.constants import COMMENT_TYPES, TOPIC_TYPES, NEWS_TOPIC_TYPE

logger = logging.getLogger(__name__)

def format_output(state):
    """
    Format kết quả cuối cùng - Nếu targeted=False thì sentiment=neutral
    """
    try:
        # Lấy an toàn từ state và chuẩn hoá kiểu dữ liệu
        llm_analysis = state.get("llm_analysis", {})
        input_data = state.get("input_data", {})

        # Nếu llm_analysis là list có dict ở phần tử đầu, dùng phần tử đó
        explanation = ""
        error_msg = "Lỗi xử lý: 'list' object has no attribute 'get'"

        if isinstance(llm_analysis, list):
            if len(llm_analysis) > 0 and isinstance(llm_analysis[0], dict):
                logger.warning("llm_analysis is list, using first dict element")
                llm_analysis = llm_analysis[0]
            else:
                logger.error("llm_analysis is list but contains no dict; normalizing to {}")
                llm_analysis = {}
                explanation = error_msg

        # Nếu input_data không phải dict thì log và bình thường hoá
        if not isinstance(input_data, dict):
            logger.error(f"input_data expected dict but got {type(input_data)}; normalizing to {{}}")
            input_data = {}

        # Normalize llm_analysis -> extract targeted safely
        targeted = False
        if isinstance(llm_analysis, dict):
            targeted = bool(llm_analysis.get("targeted", False))
        elif isinstance(llm_analysis, str):
            # cố parse JSON string
            try:
                parsed = json.loads(llm_analysis)
                if isinstance(parsed, dict):
                    targeted = bool(parsed.get("targeted", False))
                    explanation = explanation or parsed.get("explanation", "")
            except Exception:
                explanation = explanation or "Lỗi xử lý: không thể parse llm_analysis string"
        else:
            explanation = explanation or "Lỗi xử lý: llm_analysis có kiểu không mong đợi"

        # Lấy sentiment / confidence / keywords / explanation từ llm_analysis
        sentiment = llm_analysis.get("sentiment", "neutral") if isinstance(llm_analysis, dict) else "neutral"
        confidence = float(llm_analysis.get("confidence", 0.0)) if isinstance(llm_analysis, dict) else 0.0
        keywords = llm_analysis.get("keywords", {}) if isinstance(llm_analysis, dict) else {}
        llm_explanation = llm_analysis.get("explanation", "") if isinstance(llm_analysis, dict) else ""
        final_explanation = llm_explanation or explanation

        content_type = input_data.get("type", "")

        # ✅ NẾU TARGETED = FALSE → SENTIMENT = NEUTRAL + KHÔNG TRẢ KEYWORDS
        if not targeted:
            sentiment = "neutral"
            confidence = 0.0
            keywords = {"positive": [], "negative": []}
            final_explanation = "Nội dung không mention đến main keywords"
        
        # ✅ NẾU SENTIMENT = NEUTRAL → KHÔNG TRẢ KEYWORDS
        elif sentiment == "neutral":
            keywords = {"positive": [], "negative": []}
        
        # Đảm bảo keywords có format đúng
        if not isinstance(keywords, dict):
            keywords = {"positive": [], "negative": []}
        else:
            # Đảm bảo có đầy đủ keys
            if "positive" not in keywords:
                keywords["positive"] = []
            if "negative" not in keywords:
                keywords["negative"] = []

        result = {
            "index": llm_analysis.get("index", "") if isinstance(llm_analysis, dict) else "",
            "type": content_type,
            "targeted": targeted,
            "sentiment": sentiment,
            "confidence": confidence,
            "keywords": keywords,
            "explanation": final_explanation,
            "log_level": calculate_log_level(
                sentiment,
                content_type,
                targeted
            )
        }

        return {**state, "final_result": result}

    except Exception as e:
        logger.error(f"Error in format_output: {str(e)}")
        return {**state, "final_result": {
            "index": "",
            "type": "",
            "targeted": False,
            "sentiment": "neutral",
            "confidence": 0.0,
            "keywords": [],
            "explanation": f"Exception: {str(e)}",
            "log_level": 0
        }}


def calculate_log_level(sentiment, content_type, targeted):
    """
    Calculate log_level based on sentiment, type, and targeted status
    """
    # Neutral/Positive → log_level = 0
    if sentiment in ["neutral", "positive"]:
        return 0
    
    # Negative sentiment
    if sentiment != "negative":
        return 0
    
    # Comment types → log_level = 1 (không cần kiểm tra targeted)
    if content_type in COMMENT_TYPES:
        return 1
    
    # Topic types + targeted → log_level = 2
    if content_type in TOPIC_TYPES and targeted:
        return 2
    
    # newsTopic + targeted → log_level = 3
    if content_type == NEWS_TOPIC_TYPE and targeted:
        return 3
    
    return 0