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
        
        # Chuyển main_keywords về lowercase để so sánh không phân biệt hoa thường
        main_keywords_lower = [kw.lower() for kw in main_keywords]
        
        # Kiểm tra xem có keywords nào trùng với main_keywords không
        found_keywords = []
        for category in ["positive", "negative", "neutral"]:
            category_keywords = keywords.get(category, [])
            for kw in category_keywords:
                if kw.lower() in main_keywords_lower:
                    found_keywords.append(kw)
        
        # Targeted = True chỉ khi có keywords trùng với main_keywords
        targeted = len(found_keywords) > 0
        
        # Tạo kết quả cuối cùng
        result = {
            "id": input_data.get("id", ""),
            "index": input_data["index"],
            "type": input_data.get("type", ""),
            "targeted": targeted,
            "sentiment": sentiment,
            "confidence": llm_analysis.get("confidence", 0.0),
            "keywords": keywords,
            "explanation": llm_analysis.get("explanation", "")
        }
        
        logger.info(f"Formatted result: targeted={targeted}, sentiment={sentiment}, found_keywords={found_keywords}")
        
        return {**state, "final_result": result}
        
    except Exception as e:
        logger.error(f"Lỗi khi format output: {str(e)}")
        raise