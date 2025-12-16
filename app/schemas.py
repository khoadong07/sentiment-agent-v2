from pydantic import BaseModel
from typing import Optional, Dict, List

class PostInput(BaseModel):
    id: str
    index: str
    title: Optional[str] = ""
    content: Optional[str] = ""
    description: Optional[str] = ""
    type: Optional[str] = ""

class KeywordSentiment(BaseModel):
    positive: List[str] = []
    neutral: List[str] = []
    negative: List[str] = []

class AnalysisResult(BaseModel):
    index: str
    targeted: bool
    topic: str
    sentiment: str
    confidence: float
    keywords: KeywordSentiment
    explanation: str