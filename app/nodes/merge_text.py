import logging

logger = logging.getLogger(__name__)

def merge_text(state):
    """
    Gộp title, content, description thành một văn bản để phân tích
    """
    try:
        input_data = state["input_data"]
        
        # Lấy các trường text và loại bỏ khoảng trắng thừa
        title = (input_data.get("title") or "").strip()
        content = (input_data.get("content") or "").strip()
        description = (input_data.get("description") or "").strip()
        
        # Gộp các trường text, loại bỏ chuỗi rỗng
        text_parts = [part for part in [title, content, description] if part]
        merged_text = " ".join(text_parts)
        
        logger.info(f"Đã gộp text: {len(merged_text)} ký tự")
        
        return {**state, "merged_text": merged_text}
        
    except Exception as e:
        logger.error(f"Lỗi khi merge text: {str(e)}")
        raise