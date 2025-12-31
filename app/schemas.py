from pydantic import BaseModel, Field
from typing import Optional, Dict, List

class SentimentRequest(BaseModel):
    """Input schema tương thích với sentiment_analysis_fixed.py"""
    id: str
    index: Optional[str] = None
    topic: Optional[str] = None
    title: Optional[str] = ""
    content: Optional[str] = ""
    description: Optional[str] = ""
    type: str
    main_keywords: List[str] = Field(default_factory=list)

class PostInput(BaseModel):
    """Legacy schema để backward compatibility"""
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

class SentimentResponse(BaseModel):
    """Output schema tương thích với sentiment_analysis_fixed.py"""
    targeted: bool
    sentiment: str
    confidence: float
    keywords: Dict[str, List[str]]
    explanation: str

class AnalysisResult(BaseModel):
    """Extended result với metadata"""
    id: str
    index: str
    type: str
    targeted: bool
    sentiment: str
    confidence: float
    keywords: KeywordSentiment
    explanation: str
    log_level: int = 0
    processing_time: Optional[float] = None
    trace_id: Optional[str] = None