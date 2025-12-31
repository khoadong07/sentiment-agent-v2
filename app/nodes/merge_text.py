import logging
from app.constants import COMMENT_TYPES

logger = logging.getLogger(__name__)

def merge_text(state):
    """
    Gộp title, content, description thành một văn bản để phân tích
    
    Logic mới:
    - Comment types + có content: analyze_with_llm sẽ check mention trong content trước
    - Các type khác: analyze_with_llm sẽ check mention trong merged_text
    - Merged_text vẫn được tạo để cung cấp context đầy đủ cho LLM
    """
    try:
        input_data = state["input_data"]
        post_type = input_data.get("type", "")
        
        # Lấy các trường text và loại bỏ khoảng trắng thừa
        title = (input_data.get("title") or "").strip()
        content = (input_data.get("content") or "").strip()
        description = (input_data.get("description") or "").strip()
        
        # Định nghĩa comment types
        comment_types = COMMENT_TYPES
        
        # Xử lý khác nhau dựa trên type
        if post_type in comment_types:
            # Với comment: ưu tiên content, title chỉ là context
            if content:
                # Content là chính, title và description là context bổ sung
                text_parts = [content]
                if title:
                    text_parts.append(f"(Context: {title})")
                if description:
                    text_parts.append(description)
            else:
                # Nếu không có content, dùng title và description
                text_parts = [part for part in [title, description] if part]
        else:
            # Với các type khác: gộp bình thường
            text_parts = [part for part in [title, content, description] if part]
        
        merged_text = " ".join(text_parts)
        
        logger.info(f"Đã gộp text (type={post_type}): {len(merged_text)} ký tự")
        
        return {**state, "merged_text": merged_text}
        
    except Exception as e:
        logger.error(f"Lỗi khi merge text: {str(e)}")
        raise