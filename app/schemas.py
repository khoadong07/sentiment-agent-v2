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
    neutral: List[str] = []
    negative: List[str] = []

class AnalysisResult(BaseModel):
    index: str
    targeted: bool
    sentiment: str
    confidence: float
    keywords: KeywordSentiment
    explanation: str