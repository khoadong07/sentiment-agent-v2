from pydantic import BaseModel
from typing import Optional, Dict, List

class PostInput(BaseModel):
    id: str
    index: str
    title: Optional[str] = ""
    content: Optional[str] = ""
    description: Optional[str] = ""
    type: Optional[str] = ""
    main_keywords: List[str] = []

class KeywordSentiment(BaseModel):
    positive: List[str] = []
    negative: List[str] = []

class AnalysisResult(BaseModel):
    id: str
    index: str
    type: str
    targeted: bool
    sentiment: str
    confidence: float
    keywords: KeywordSentiment
    explanation: str
    log_level: int