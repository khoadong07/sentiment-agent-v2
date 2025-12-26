#!/usr/bin/env python3
"""
Test script để kiểm tra LLM response trực tiếp với prompt mới
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.llm import llm
from app.prompts import TARGETED_ANALYSIS_PROMPT
from app.nodes.analyze_with_llm import parse_llm_response

def test_llm_direct():
    """Test LLM response trực tiếp"""
    
    # Test cases
    test_cases = [
        {
            "name": "Có mention dyson",
            "main_keywords": ["dyson", "máy lọc không khí"],
            "text": "Máy lọc không khí Dyson rất tốt, tôi rất hài lòng",
            "expected_targeted": True
        },
        {
            "name": "Không mention keywords",
            "main_keywords": ["dyson", "máy lọc không khí"],
            "text": "Hôm nay trời đẹp quá, tôi đi chơi với bạn bè",
            "expected_targeted": False
        },
        {
            "name": "Mention keywords khác",
            "main_keywords": ["dyson", "máy lọc không khí"],
            "text": "Máy lọc Sharp rất tốt, tôi recommend",
            "expected_targeted": False
        },
        {
            "name": "Mention biến thể dyson",
            "main_keywords": ["dyson", "máy lọc không khí"],
            "text": "Dýon máy lọc ko khí tuyệt vời lắm",
            "expected_targeted": True
        }
    ]
    
    print("=== Testing LLM Direct Response ===\n")
    
    for test_case in test_cases:
        print(f"=== {test_case['name']} ===")
        print(f"Main keywords: {test_case['main_keywords']}")
        print(f"Text: {test_case['text']}")
        
        try:
            # Tạo prompt
            prompt = TARGETED_ANALYSIS_PROMPT.format(
                main_keywords=", ".join(test_case['main_keywords']),
                text=test_case['text']
            )
            
            print(f"\nPrompt:\n{prompt[:200]}...")
            
            # Gọi LLM
            response = llm.invoke(prompt)
            raw_content = response.content
            
            print(f"\nRaw LLM Response:\n{raw_content}")
            
            # Parse response
            parsed_result = parse_llm_response(raw_content)
            
            print(f"\nParsed Result:")
            print(f"- Targeted: {parsed_result.get('targeted', False)}")
            print(f"- Sentiment: {parsed_result.get('sentiment', 'unknown')}")
            print(f"- Confidence: {parsed_result.get('confidence', 0.0)}")
            print(f"- Keywords: {parsed_result.get('keywords', {})}")
            print(f"- Explanation: {parsed_result.get('explanation', '')}")
            
            # Check result
            expected = test_case['expected_targeted']
            actual = parsed_result.get('targeted', False)
            
            if actual == expected:
                print(f"✅ PASS - Expected: {expected}, Got: {actual}")
            else:
                print(f"❌ FAIL - Expected: {expected}, Got: {actual}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 60)

if __name__ == "__main__":
    test_llm_direct()