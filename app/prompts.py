TARGETED_ANALYSIS_PROMPT = """
Bạn là chuyên gia phân tích nội dung tiếng Việt. Hãy phân tích văn bản sau và xác định:

1. TARGETED: Văn bản có đề cập/nhắc đến các main_keywords không?
2. SENTIMENT: Cảm xúc tổng thể của văn bản
3. KEYWORDS: Các từ khóa cảm xúc được tìm thấy
4. CONFIDENCE: Độ tin cậy của phân tích

MAIN KEYWORDS CẦN KIỂM TRA: {main_keywords}

VĂN BẢN CẦN PHÂN TÍCH:
"{text}"

QUY TẮC PHÂN TÍCH:

1. TARGETED (true/false):
   - true: Văn bản có đề cập/nhắc đến ít nhất 1 trong các main_keywords
   - false: Văn bản không đề cập đến bất kỳ main_keywords nào
   - Kiểm tra cả từ chính xác và các biến thể gần giống

2. SENTIMENT (positive/negative/neutral):
   - positive: Cảm xúc tích cực, hài lòng, khen ngợi
   - negative: Cảm xúc tiêu cực, không hài lòng, phản đối
   - neutral: Trung tính hoặc không rõ cảm xúc

3. KEYWORDS:
   - Trích xuất các từ/cụm từ thể hiện cảm xúc từ văn bản
   - Phân loại theo sentiment: positive, negative, neutral

4. CONFIDENCE (0.0-1.0):
   - 0.8-1.0: Rất rõ ràng
   - 0.5-0.7: Khá rõ ràng  
   - 0.0-0.4: Không rõ ràng

5. EXPLANATION:
   - Giải thích ngắn gọn bằng tiếng Việt (tối đa 20 từ)
   - Nêu rõ có đề cập main_keywords hay không

QUAN TRỌNG: Chỉ trả về JSON thuần túy, không có text thêm.

FORMAT OUTPUT (JSON):
{{
  "targeted": true|false,
  "sentiment": "positive|negative|neutral",
  "confidence": 0.0,
  "keywords": {{
    "positive": [],
    "negative": [],
    "neutral": []
  }},
  "explanation": "Giải thích ngắn gọn"
}}
"""

SENTIMENT_ANALYSIS_PROMPT = """
Analyze Vietnamese text and return sentiment JSON only.

INPUT
Topic: "{topic_name}"
Keywords: {keywords}
Text: "{text}"

RULES
1. Use ONLY user experience content (complaints, praise, opinions). Ignore ads, promotions, news, announcements.
2. If no user experience → sentiment="neutral", confidence ≤ 0.4
3. User experience TARGETS topic if:
   - topic or keywords mentioned, OR
   - delivery, app, shipper, or service process belongs to topic
4. If not targeted → sentiment="neutral", confidence ≤ 0.4
5. If targeted:
   - positive = praise / satisfaction
   - negative = complaint / bad experience
   - neutral = no clear evaluation
6. Extract ONLY Vietnamese sentiment keywords from user experience.
7. Confidence:
   - 0.8–1.0 clear
   - 0.5–0.7 weak/mixed
   - ≤0.4 not targeted
8. Explanation:
   - Vietnamese only
   - Max 15 words
   - Clearly state: existence of user experience, targeting, reason for sentiment

OUTPUT JSON ONLY
{{
  "sentiment": "positive|negative|neutral",
  "confidence": 0.0,
  "keywords": {{
    "positive": [],
    "negative": [],
    "neutral": []
  }},
  "explanation": ""
}}

Return ONLY valid JSON, no extra text, no markdown.
"""

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