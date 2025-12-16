import logging

logger = logging.getLogger(__name__)

def format_output(state):
    """
    Format kết quả cuối cùng theo schema yêu cầu
    """
    try:
        llm_analysis = state["llm_analysis"]
        input_data = state["input_data"]
        main_keywords = input_data.get("main_keywords", [])
        
        # Xác định xem content có target đến keyword hay không
        sentiment = llm_analysis.get("sentiment", "neutral")
        keywords = llm_analysis.get("keywords", {})
        
        # Kiểm tra xem có keywords được tìm thấy không
        has_keywords = any([
            keywords.get("positive", []),
            keywords.get("negative", []),
            keywords.get("neutral", [])
        ])
        
        # Targeted = True nếu có sentiment khác neutral hoặc có keywords
        targeted = sentiment != "neutral" or has_keywords
        
        # Tạo kết quả cuối cùng
        result = {
            "index": input_data["index"],
            "targeted": targeted,
            "sentiment": sentiment,
            "confidence": llm_analysis.get("confidence", 0.0),
            "keywords": keywords,
            "explanation": llm_analysis.get("explanation", "")
        }
        
        logger.info(f"Formatted result: targeted={targeted}, sentiment={sentiment}")
        
        return {**state, "final_result": result}
        
    except Exception as e:
        logger.error(f"Lỗi khi format output: {str(e)}")
        raise