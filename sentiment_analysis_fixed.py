import json
import re
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Optional
from app.config import LLM_MODEL, OPENAI_API_KEY, OPENAI_URI

COMMENT_TYPES = {
    "fbPageComment", "fbGroupComment", "fbUserComment", "forumComment",
    "newsComment", "youtubeComment", "tiktokComment", "snsComment",
    "linkedinComment", "ecommerceComment", "threadsComment"
}

# ================= MODEL =================
class SentimentRequest(BaseModel):
    id: str
    index: Optional[str] = None
    topic: Optional[str] = None
    title: Optional[str] = ""
    content: Optional[str] = ""
    description: Optional[str] = ""
    type: str
    main_keywords: List[str]

class SentimentResponse(BaseModel):
    targeted: bool
    sentiment: str
    confidence: float
    keywords: Dict[str, List[str]]
    explanation: str

# ================= UTILS =================
def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()

def mentions_keyword(text: str, keywords: List[str]) -> bool:
    text = normalize(text)
    return any(k.lower() in text for k in keywords)

def dedup_merge_text(*parts: str) -> str:
    seen = set()
    merged = []
    for part in parts:
        if not part:
            continue
        sentences = re.split(r"[.!?]", part)
        for s in sentences:
            s_clean = normalize(s)
            if s_clean and s_clean not in seen:
                seen.add(s_clean)
                merged.append(s.strip())
    return ". ".join(merged)

# ================= PROMPT =================
SENTIMENT_PROMPT = """
You are a Vietnamese Sentiment Analysis Expert.
Analyze sentiment toward the mentioned target.
TEXT:
"{text}"
RULES:
- Analyze ONLY user experience (opinion, praise, complaint).
- If not user experience → sentiment = neutral.
- positive = praise / satisfaction
- negative = complaint / dissatisfaction
- Extract Vietnamese emotional keywords only.
- Skip neutral keywords.
- Explanation max 15 Vietnamese words.
Return ONLY valid JSON:
{{
  "sentiment": "positive|negative|neutral",
  "confidence": 0.0,
  "keywords": {{
    "positive": [],
    "negative": []
  }},
  "explanation": ""
}}
"""

# ================= LLM CALL =================
class LLMError(Exception):
    pass

def extract_json(text: str) -> dict:
    """Extract JSON from LLM response text"""
    try:
        print(text)
        # Try to find JSON in the text
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            json_str = text[start:end]
            return json.loads(json_str)
        else:
            # If no JSON found, return default
            return {
                "sentiment": "neutral",
                "confidence": 0.3,
                "keywords": {"positive": [], "negative": []},
                "explanation": "Không thể phân tích"
            }
    except json.JSONDecodeError:
        # Return default if JSON parsing fails
        return {
            "sentiment": "neutral",
            "confidence": 0.3,
            "keywords": {"positive": [], "negative": []},
            "explanation": "Lỗi phân tích JSON"
        }

def call_llm(prompt: str) -> dict:
    """
    Call OpenAI-compatible LLM (OpenAI / vLLM / GPT-OSS)
    Expect STRICT JSON output
    """
    if not all([LLM_MODEL, OPENAI_URI, OPENAI_API_KEY]):
        raise RuntimeError("Missing LLM_MODEL / OPENAI_URI / OPENAI_API_KEY")
    url = f"{OPENAI_URI}/chat/completions"
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a strict JSON-only sentiment analysis engine."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.0,
        "max_tokens": 300,
        "response_format": {"type": "json_object"}  # Force JSON output
    }
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    print(resp.text)
    if resp.status_code != 200:
        raise LLMError(f"LLM HTTP {resp.status_code}: {resp.text}")
    data = resp.json()
    try:
        content = data["choices"][0]["message"]["content"]
        result = extract_json(content)
    except Exception as e:
        raise LLMError(f"Invalid LLM response format: {e}")
    # -------- HARD VALIDATION (anti-hallucination) --------
    result.setdefault("sentiment", "neutral")
    result.setdefault("confidence", 0.3)
    result.setdefault("keywords", {"positive": [], "negative": []})
    result.setdefault("explanation", "")
    if result["sentiment"] == "neutral":
        result["keywords"] = {"positive": [], "negative": []}
    result["confidence"] = float(
        min(max(result["confidence"], 0.0), 1.0)
    )
    return result

# ================= AGENT =================
class SentimentAgent:
    def analyze(self, req: SentimentRequest) -> SentimentResponse:
        # 1. Select text
        if req.type in COMMENT_TYPES:
            text = req.content or ""
        else:
            text = dedup_merge_text(req.title, req.content, req.description)
        # 2. Target check
        if not mentions_keyword(text, req.main_keywords):
            return SentimentResponse(
                targeted=False,
                sentiment="neutral",
                confidence=0.3,
                keywords={"positive": [], "negative": []},
                explanation="Không nhắc đến chủ thể"
            )
        # 3. Call LLM
        llm_result = call_llm(
            SENTIMENT_PROMPT.format(text=text)
        )
        return SentimentResponse(
            targeted=True,
            sentiment=llm_result["sentiment"],
            confidence=llm_result["confidence"],
            keywords=llm_result["keywords"],
            explanation=llm_result["explanation"]
        )

# ================= FASTAPI =================
app = FastAPI(title="Sentiment Analysis Agent API")
agent = SentimentAgent()

@app.post("/analyze", response_model=SentimentResponse)
def analyze_sentiment(req: SentimentRequest):
    return agent.analyze(req)

# Test the agent
if __name__ == "__main__":
    req = SentimentRequest(
        id="6531932769252491265_7588569673189444884",
        index="62d2f6d55a468d456a5b958a",
        topic="Vinfast",
        title="700tr có đắt???#vinfast #xuhuongtiktok #vinfastvn",
        content="Đúng là Vin làm cả dịch vụ dọn nhà nữa là hết nước chấm. Nhìn trên đường 60% là xanh hết sg joy",
        description="",
        type="tiktokComment",
        main_keywords=["vinfast"]
    )
   
    result = agent.analyze(req)
    print(result)