import json
import re
import time
import uuid
from typing import Dict, List, Optional

# Try to import Langfuse with proper error handling
try:
    from langfuse import Langfuse
    from langfuse.decorators import observe, langfuse_context
    LANGFUSE_AVAILABLE = True
except ImportError:
    print("Warning: Langfuse not available. Continuing without tracing.")
    LANGFUSE_AVAILABLE = False
    # Create dummy decorators
    def observe(name=None):
        def decorator(func):
            return func
        return decorator
    
    class DummyLangfuseContext:
        def update_current_trace(self, **kwargs):
            pass
    
    langfuse_context = DummyLangfuseContext()

from app.config import (
    LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_HOST,
    COMMENT_TYPES, LLM_MODEL, OPENAI_API_KEY, OPENAI_URI
)
from app.schemas import SentimentRequest, SentimentResponse
from app.llm import llm

# Initialize Langfuse if available
if LANGFUSE_AVAILABLE and LANGFUSE_SECRET_KEY and LANGFUSE_PUBLIC_KEY:
    try:
        langfuse = Langfuse(
            secret_key=LANGFUSE_SECRET_KEY,
            public_key=LANGFUSE_PUBLIC_KEY,
            host=LANGFUSE_HOST
        )
        print("Langfuse initialized successfully")
    except Exception as e:
        print(f"Warning: Failed to initialize Langfuse: {e}")
        LANGFUSE_AVAILABLE = False
else:
    print("Langfuse not configured or not available")
    LANGFUSE_AVAILABLE = False

class SentimentAnalysisService:
    """Production-ready sentiment analysis service với optional Langfuse tracing"""
    
    def __init__(self):
        self.comment_types = COMMENT_TYPES
        self.sentiment_prompt = self._get_sentiment_prompt()
    
    def _get_sentiment_prompt(self) -> str:
        """Simplified and robust prompt for all cases"""
        return """You are a Vietnamese sentiment analysis expert. Analyze the text and determine if it directly targets the mentioned keywords with an opinion.

TEXT: "{text}"
KEYWORDS: {keywords}
TYPE: {post_type}

RULES:
1. TARGETING CHECK:
   - targeted = true: Text expresses DIRECT OPINION about the keywords
   - targeted = false: Text only mentions keywords without direct opinion

2. SENTIMENT (only if targeted = true):
   - positive: Praise, satisfaction, positive experience
   - negative: Criticism, complaints, negative experience  
   - neutral: Mentions with no clear positive/negative opinion

3. If targeted = false → always return sentiment = neutral, confidence ≤ 0.4

4. EXPLANATION: Vietnamese only, maximum 15 words

EXAMPLES:
✅ TARGETED:
- "Vinfast xe tốt lắm" → targeted=true, sentiment=positive
- "iPhone tệ quá" → targeted=true, sentiment=negative
- "Samsung dùng bình thường" → targeted=true, sentiment=neutral

❌ NOT TARGETED:
- "Bạn tôi dùng Vinfast" → targeted=false, sentiment=neutral
- "Nghe nói iPhone mới" → targeted=false, sentiment=neutral
- "cái gì cũng đổ cho Apple" → targeted=false, sentiment=neutral

Return JSON only:
{{
  "targeted": true,
  "sentiment": "positive",
  "confidence": 0.8,
  "keywords": {{
    "positive": ["tốt"],
    "negative": []
  }},
  "explanation": "Đánh giá tích cực về sản phẩm"
}}"""
    
    @staticmethod
    def normalize(text: str) -> str:
        """Normalize text for keyword matching"""
        return re.sub(r"\s+", " ", text.lower()).strip()
    
    @staticmethod
    def mentions_keyword(text: str, keywords: List[str]) -> bool:
        """Enhanced keyword matching với fuzzy logic"""
        text = SentimentAnalysisService.normalize(text)
        
        for keyword in keywords:
            keyword_lower = keyword.lower().strip()
            
            # 1. Exact match (như cũ)
            if keyword_lower in text:
                return True
            
            # 2. Word boundary match (tránh false positive)
            import re
            if re.search(r'\b' + re.escape(keyword_lower) + r'\b', text):
                return True
            
            # 3. Fuzzy matching cho các trường hợp đặc biệt
            if SentimentAnalysisService._fuzzy_keyword_match(text, keyword_lower):
                return True
        
        return False
    
    @staticmethod
    def _fuzzy_keyword_match(text: str, keyword: str) -> bool:
        """Fuzzy matching logic cho các trường hợp đặc biệt"""
        import re
        
        # Split keyword thành các parts
        keyword_parts = keyword.split()
        
        # Case 1: Multi-word keyword → check for abbreviated forms
        if len(keyword_parts) > 1:
            # Ví dụ: "be app" → check for "be" trong context phù hợp
            main_word = keyword_parts[0]  # "be"
            
            # Check if main word exists with app-related context
            if main_word in text:
                # Context patterns cho app names
                app_contexts = [
                    r'\b' + re.escape(main_word) + r'\s+(đi|về|gọi|đặt|dùng|app|ứng dụng)',
                    r'(đặt|gọi|dùng|mở)\s+' + re.escape(main_word) + r'\b',
                    r'\b' + re.escape(main_word) + r'\s+(taxi|xe|grab)',
                ]
                
                for pattern in app_contexts:
                    if re.search(pattern, text, re.IGNORECASE):
                        return True
        
        # Case 2: Keyword variations
        keyword_variations = SentimentAnalysisService._get_keyword_variations(keyword)
        for variation in keyword_variations:
            if variation in text:
                return True
        
        # Case 3: Partial matching cho compound words
        if len(keyword) > 4:  # Chỉ áp dụng cho keyword dài
            # Remove spaces and check
            keyword_nospace = keyword.replace(' ', '')
            if keyword_nospace in text.replace(' ', ''):
                return True
        
        return False
    
    @staticmethod
    def _get_keyword_variations(keyword: str) -> List[str]:
        """Tạo các biến thể của keyword"""
        variations = []
        
        # Common app name variations
        app_mappings = {
            'be app': ['be', 'beapp', 'bee app', 'beeapp'],
            'grab': ['grab', 'grabcar', 'grab car'],
            'gojek': ['gojek', 'go-jek', 'go jek'],
            'shopee': ['shopee', 'shoppee', 'shop ee'],
            'lazada': ['lazada', 'laz', 'lazada app'],
            'tiki': ['tiki', 'tiki app'],
            'vinfast': ['vinfast', 'vin fast', 'vf'],
            'iphone': ['iphone', 'ip', 'điện thoại iphone'],
            'samsung': ['samsung', 'ss', 'sam sung'],
        }
        
        keyword_lower = keyword.lower()
        
        # Check if keyword has predefined variations
        for main_key, vars_list in app_mappings.items():
            if keyword_lower == main_key or keyword_lower in vars_list:
                variations.extend(vars_list)
                break
        
        # Generate automatic variations
        if ' ' in keyword:
            # Remove spaces
            variations.append(keyword.replace(' ', ''))
            # Add with different separators
            variations.append(keyword.replace(' ', '-'))
            variations.append(keyword.replace(' ', '_'))
        
        # Remove duplicates and original keyword
        variations = list(set(variations))
        if keyword.lower() in variations:
            variations.remove(keyword.lower())
        
        return variations
    
    @staticmethod
    def dedup_merge_text(*parts: str) -> str:
        """Merge text parts with deduplication"""
        seen = set()
        merged = []
        for part in parts:
            if not part:
                continue
            sentences = re.split(r"[.!?]", part)
            for s in sentences:
                s_clean = SentimentAnalysisService.normalize(s)
                if s_clean and s_clean not in seen:
                    seen.add(s_clean)
                    merged.append(s.strip())
        return ". ".join(merged)
    
    def extract_json(self, text: str) -> dict:
        """Extract JSON from LLM response với error handling"""
        try:
            # Try to find JSON in the text
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end > start:
                json_str = text[start:end]
                result = json.loads(json_str)
                
                # Validate and clean result
                result.setdefault("targeted", False)
                result.setdefault("sentiment", "neutral")
                result.setdefault("confidence", 0.3)
                result.setdefault("keywords", {"positive": [], "negative": []})
                result.setdefault("explanation", "")
                
                # Ensure confidence is in valid range
                result["confidence"] = float(min(max(result["confidence"], 0.0), 1.0))
                
                # If not targeted or neutral, clear keywords and set neutral
                if not result["targeted"] or result["sentiment"] == "neutral":
                    result["keywords"] = {"positive": [], "negative": []}
                    result["sentiment"] = "neutral"
                    if not result["targeted"]:
                        result["confidence"] = min(result["confidence"], 0.4)
                
                return result
            else:
                return self._get_default_result("Không tìm thấy JSON trong response")
        except json.JSONDecodeError:
            return self._get_default_result("Lỗi phân tích JSON")
        except Exception as e:
            return self._get_default_result(f"Lỗi xử lý: {str(e)}")
    
    def _get_default_result(self, explanation: str = "Không thể phân tích") -> dict:
        """Default result for error cases"""
        return {
            "targeted": False,
            "sentiment": "neutral",
            "confidence": 0.3,
            "keywords": {"positive": [], "negative": []},
            "explanation": explanation
        }
    
    def call_llm(self, prompt: str, text: str, keywords: List[str], post_type: str) -> dict:
        """Call LLM với optional Langfuse tracing"""
        try:
            # Add trace metadata if Langfuse is available
            if LANGFUSE_AVAILABLE:
                try:
                    langfuse_context.update_current_trace(
                        name="sentiment_analysis_llm_call",
                        metadata={
                            "model": LLM_MODEL,
                            "prompt_length": len(prompt),
                            "keywords": keywords,
                            "post_type": post_type
                        }
                    )
                except Exception as e:
                    print(f"Langfuse trace update failed: {e}")
            
            # Format prompt with all parameters - using named placeholders
            try:
                formatted_prompt = prompt.format(
                    text=text,
                    keywords=", ".join(keywords),
                    post_type=post_type
                )
            except KeyError as e:
                print(f"Prompt formatting error: {e}")
                # Fallback to simple format
                formatted_prompt = f"""
Analyze sentiment for: {text}
Keywords: {', '.join(keywords)}
Type: {post_type}
Return JSON with targeted, sentiment, confidence, keywords, explanation.
"""
            
            response = llm.invoke(formatted_prompt)
            content = response.content
            
            # Extract and validate JSON
            result = self.extract_json(content)
            
            # Update trace with result if Langfuse is available
            if LANGFUSE_AVAILABLE:
                try:
                    langfuse_context.update_current_trace(
                        output=result,
                        metadata={
                            "raw_response_length": len(content),
                            "targeted": result.get("targeted"),
                            "sentiment": result.get("sentiment"),
                            "confidence": result.get("confidence")
                        }
                    )
                except Exception as e:
                    print(f"Langfuse trace update failed: {e}")
            
            return result
            
        except Exception as e:
            # Log error to Langfuse if available
            if LANGFUSE_AVAILABLE:
                try:
                    langfuse_context.update_current_trace(
                        metadata={
                            "error": True,
                            "error_message": f"LLM call failed: {str(e)}"
                        }
                    )
                except Exception as trace_error:
                    print(f"Langfuse trace update failed: {trace_error}")
            return self._get_default_result(f"Lỗi LLM: {str(e)}")
    
    def analyze(self, request: SentimentRequest) -> SentimentResponse:
        """Main analysis method với enhanced targeting logic"""
        start_time = time.time()
        trace_id = str(uuid.uuid4())
        
        try:
            # Update trace with input metadata if Langfuse is available
            if LANGFUSE_AVAILABLE:
                try:
                    langfuse_context.update_current_trace(
                        name="sentiment_analysis",
                        user_id=request.id,
                        session_id=request.index,
                        input={
                            "id": request.id,
                            "type": request.type,
                            "has_keywords": len(request.main_keywords) > 0,
                            "text_length": len((request.title or "") + (request.content or "") + (request.description or ""))
                        },
                        metadata={
                            "trace_id": trace_id,
                            "model": LLM_MODEL
                        }
                    )
                except Exception as e:
                    print(f"Langfuse trace update failed: {e}")
            
            # 1. Select appropriate text based on type
            if request.type in self.comment_types:
                # For COMMENT types: Only analyze the comment content
                # Ignore title and description as they are usually context/original post
                text = request.content or ""
                analysis_scope = "comment_content_only"
            else:
                # For NON-COMMENT types: Analyze all content (title + content + description)
                # This includes news articles, reviews, posts, etc.
                text = self.dedup_merge_text(
                    request.title or "", 
                    request.content or "", 
                    request.description or ""
                )
                analysis_scope = "full_content"
            
            # 2. Check if text mentions target keywords
            if not self.mentions_keyword(text, request.main_keywords):
                result = SentimentResponse(
                    targeted=False,
                    sentiment="neutral",
                    confidence=0.3,
                    keywords={"positive": [], "negative": []},
                    explanation="Không nhắc đến chủ thể"
                )
                
                # Update trace for non-targeted result if Langfuse is available
                if LANGFUSE_AVAILABLE:
                    try:
                        langfuse_context.update_current_trace(
                            output=result.dict(),
                            metadata={
                                "processing_time": time.time() - start_time,
                                "targeted": False,
                                "reason": "no_keyword_match",
                                "analysis_scope": analysis_scope
                            }
                        )
                    except Exception as e:
                        print(f"Langfuse trace update failed: {e}")
                
                return result
            
            # 3. Call LLM to analyze sentiment and targeting
            llm_result = self.call_llm(
                self.sentiment_prompt, 
                text, 
                request.main_keywords, 
                request.type
            )
            
            # 4. Create response based on LLM result
            result = SentimentResponse(
                targeted=llm_result.get("targeted", False),
                sentiment=llm_result["sentiment"],
                confidence=llm_result["confidence"],
                keywords=llm_result["keywords"],
                explanation=llm_result["explanation"]
            )
            
            # Update final trace if Langfuse is available
            if LANGFUSE_AVAILABLE:
                try:
                    processing_time = time.time() - start_time
                    langfuse_context.update_current_trace(
                        output=result.dict(),
                        metadata={
                            "processing_time": processing_time,
                            "targeted": result.targeted,
                            "final_sentiment": result.sentiment,
                            "final_confidence": result.confidence,
                            "is_comment_type": request.type in self.comment_types,
                            "analysis_scope": analysis_scope
                        }
                    )
                except Exception as e:
                    print(f"Langfuse trace update failed: {e}")
            
            return result
            
        except Exception as e:
            # Handle any unexpected errors
            error_result = SentimentResponse(
                targeted=False,
                sentiment="neutral",
                confidence=0.0,
                keywords={"positive": [], "negative": []},
                explanation=f"Lỗi hệ thống: {str(e)}"
            )
            
            if LANGFUSE_AVAILABLE:
                try:
                    langfuse_context.update_current_trace(
                        output=error_result.dict(),
                        metadata={
                            "processing_time": time.time() - start_time,
                            "error": True,
                            "error_message": f"Analysis failed: {str(e)}"
                        }
                    )
                except Exception as trace_error:
                    print(f"Langfuse trace update failed: {trace_error}")
            
            return error_result

# Global service instance
sentiment_service = SentimentAnalysisService()