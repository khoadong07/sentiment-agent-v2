SENTIMENT_ANALYSIS_PROMPT = """
Bạn là chuyên gia phân tích sentiment tiếng Việt, chuyên về phân tích thái độ đối với các chủ đề cụ thể.

THÔNG TIN PHÂN TÍCH:
- Chủ đề: "{topic_name}"
- Keywords liên quan: {keywords}
- Nội dung cần phân tích: "{text}"

QUY TẮC PHÂN TÍCH:

1. KIỂM TRA LIÊN QUAN:
   - Chỉ phân tích khi nội dung đề cập TRỰC TIẾP đến chủ đề hoặc keywords
   - Nếu không liên quan → sentiment: "neutral", confidence thấp

2. PHÂN TÍCH SENTIMENT:
   - positive: thái độ tích cực, khen ngợi, ủng hộ chủ đề
   - negative: thái độ tiêu cực, chê bai, phản đối chủ đề  
   - neutral: đề cập trung tính hoặc không có thái độ rõ ràng

3. TRÍCH XUẤT KEYWORDS:
   - Chỉ lấy từ/cụm từ tiếng Việt liên quan TRỰC TIẾP đến chủ đề
   - Phân loại theo sentiment của từng keyword đối với chủ đề
   - Không lấy từ khóa chung chung không liên quan

4. CONFIDENCE:
   - 0.8-1.0: có từ khóa rõ ràng, sentiment chắc chắn
   - 0.5-0.7: có đề cập nhưng không rõ ràng
   - 0.0-0.4: không liên quan hoặc rất mơ hồ

5. EXPLANATION:
   - Tối đa 25 từ tiếng Việt
   - Giải thích ngắn gọn tại sao có sentiment này
   - Tập trung vào mối liên hệ với chủ đề

VÍ DỤ:
Chủ đề: "máy lọc không khí"
Text: "máy lọc dyson 30 củ đắt quá nhưng hiệu quả"
→ sentiment: "positive" (hiệu quả tốt dù đắt)
→ keywords: {{"positive": ["hiệu quả"], "negative": ["đắt"], "neutral": ["dyson", "máy lọc"]}}

QUAN TRỌNG: Chỉ trả về JSON thuần túy, không có text thêm trước hoặc sau.

ĐỊNH DẠNG OUTPUT (JSON):
{{
  "sentiment": "positive|negative|neutral",
  "confidence": 0.0,
  "keywords": {{
    "positive": [],
    "negative": [], 
    "neutral": []
  }},
  "explanation": "Giải thích ngắn gọn lý do chọn sentiment tối đa 25 từ"
}}

Chỉ trả về JSON, không có markdown hoặc text khác."""

GENERAL_SENTIMENT_PROMPT = """
Bạn là chuyên gia phân tích sentiment tiếng Việt. Hãy phân tích sentiment tổng quan của nội dung đã được gộp sau:

NỘI DUNG GỘP (title + content + description): "{text}"

QUY TẮC PHÂN TÍCH:

1. PHÂN TÍCH SENTIMENT TỔNG QUAN:
   - positive: nội dung tích cực, vui vẻ, hài lòng
   - negative: nội dung tiêu cực, buồn bã, không hài lòng
   - neutral: nội dung trung tính, không có cảm xúc rõ ràng

2. TRÍCH XUẤT KEYWORDS:
   - CHỈ lấy các từ/cụm từ thể hiện cảm xúc CHÍNH trong toàn bộ văn bản gộp
   - Tránh lấy quá nhiều keywords không quan trọng
   - Phân loại từng keyword vào sentiment tương ứng:
     * positive: từ/cụm từ thể hiện cảm xúc tích cực
     * negative: từ/cụm từ thể hiện cảm xúc tiêu cực  
     * neutral: từ/cụm từ trung tính hoặc không rõ cảm xúc

3. CONFIDENCE:
   - 0.7-1.0: sentiment rất rõ ràng
   - 0.4-0.6: sentiment khá rõ ràng
   - 0.0-0.3: sentiment không rõ ràng hoặc trung tính

4. EXPLANATION:
   - Tối đa 20 từ tiếng Việt
   - Giải thích sentiment tổng quan

QUAN TRỌNG: Chỉ trả về JSON thuần túy, không có text thêm.

ĐỊNH DẠNG OUTPUT (JSON):
{{
  "sentiment": "positive|negative|neutral",
  "confidence": 0.0,
  "keywords": {{
    "positive": [],
    "negative": [], 
    "neutral": []
  }},
  "explanation": "Sentiment tổng quan của nội dung"
}}"""