import logging

logger = logging.getLogger(__name__)

def calculate_log_level(sentiment, content_type, targeted):
    """
    Tính toán log_level dựa trên sentiment, type và targeted status
    
    Rules:
    - neutral hoặc positive sentiment: return 0
    - negative sentiment:
        - type là comment types: return 1
        - type là topic types và có target đến main keywords: return 2
        - type là newsTopic và có target đến main keywords: return 3
    """
    # Nếu sentiment là neutral hoặc positive, return 0
    if sentiment in ["neutral", "positive"]:
        return 0
    
    # Chỉ xử lý negative sentiment
    if sentiment != "negative":
        return 0
    
    # Định nghĩa các loại comment
    comment_types = [
        "fbPageComment", "fbGroupComment", "fbUserComment", "forumComment",
        "newsComment", "youtubeComment", "tiktokComment", "snsComment",
        "linkedinComment", "ecommerceComment", "threadsComment"
    ]
    
    # Định nghĩa các loại topic (không bao gồm newsTopic)
    topic_types = [
        "fbPageTopic", "fbGroupTopic", "fbUserTopic", "forumTopic",
        "youtubeTopic", "tiktokTopic", "snsTopic", "linkedinTopic",
        "ecommerceTopic", "threadsTopic"
    ]
    
    # Log level 1: comment types
    if content_type in comment_types:
        return 1
    
    # Log level 2: topic types (không bao gồm newsTopic) và có target đến main keywords
    if content_type in topic_types and targeted:
        return 2
    
    # Log level 3: newsTopic và có target đến main keywords
    if content_type == "newsTopic" and targeted:
        return 3
    
    # Default case
    return 0

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
        
        # Tính toán log_level dựa trên sentiment, type và targeted
        log_level = calculate_log_level(sentiment, input_data.get("type", ""), targeted)
        
        # Tạo kết quả cuối cùng
        result = {
            "id": input_data.get("id", ""),
            "index": input_data["index"],
            "type": input_data.get("type", ""),
            "targeted": targeted,
            "sentiment": sentiment,
            "confidence": llm_analysis.get("confidence", 0.0),
            "keywords": keywords,
            "explanation": llm_analysis.get("explanation", ""),
            "log_level": log_level
        }
        
        logger.info(f"Formatted result: targeted={targeted}, sentiment={sentiment}, found_keywords={found_keywords}")
        
        return {**state, "final_result": result}
        
    except Exception as e:
        logger.error(f"Lỗi khi format output: {str(e)}")
        raise