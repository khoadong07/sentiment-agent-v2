#!/usr/bin/env python3
"""
Unit test cho format_output function
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.nodes.format_output import format_output

def test_format_output_logic():
    """Test logic của format_output function trực tiếp"""
    
    print("=== Unit Test Format Output Logic ===\n")
    
    # Test case 1: Có keywords trùng với main_keywords
    state1 = {
        "input_data": {
            "id": "test_1",
            "index": "test_index_1", 
            "type": "fbGroupTopic",
            "main_keywords": ["dyson", "dsyon", "máy lọc không khí"]
        },
        "llm_analysis": {
            "sentiment": "positive",
            "confidence": 0.8,
            "keywords": {
                "positive": ["dyson"],
                "negative": [],
                "neutral": ["máy lọc không khí"]
            },
            "explanation": "Đánh giá tích cực về sản phẩm"
        }
    }
    
    result1 = format_output(state1)
    final_result1 = result1["final_result"]
    
    print("Test 1: Có keywords trùng với main_keywords")
    print(f"Main keywords: {state1['input_data']['main_keywords']}")
    print(f"LLM keywords: {state1['llm_analysis']['keywords']}")
    print(f"Targeted: {final_result1['targeted']}")
    print(f"Expected: True")
    print(f"Result: {'✅ PASS' if final_result1['targeted'] == True else '❌ FAIL'}")
    print()
    
    # Test case 2: Không có keywords trùng
    state2 = {
        "input_data": {
            "id": "test_2",
            "index": "test_index_2",
            "type": "fbGroupTopic", 
            "main_keywords": ["dyson", "dsyon", "máy lọc không khí"]
        },
        "llm_analysis": {
            "sentiment": "positive",
            "confidence": 0.7,
            "keywords": {
                "positive": ["sharp", "tốt"],
                "negative": [],
                "neutral": []
            },
            "explanation": "Đánh giá tích cực về sản phẩm khác"
        }
    }
    
    result2 = format_output(state2)
    final_result2 = result2["final_result"]
    
    print("Test 2: Không có keywords trùng với main_keywords")
    print(f"Main keywords: {state2['input_data']['main_keywords']}")
    print(f"LLM keywords: {state2['llm_analysis']['keywords']}")
    print(f"Targeted: {final_result2['targeted']}")
    print(f"Expected: False")
    print(f"Result: {'✅ PASS' if final_result2['targeted'] == False else '❌ FAIL'}")
    print()
    
    # Test case 3: Không có keywords nào
    state3 = {
        "input_data": {
            "id": "test_3",
            "index": "test_index_3",
            "type": "fbGroupTopic",
            "main_keywords": ["dyson", "dsyon", "máy lọc không khí"]
        },
        "llm_analysis": {
            "sentiment": "neutral",
            "confidence": 0.1,
            "keywords": {
                "positive": [],
                "negative": [],
                "neutral": []
            },
            "explanation": "Không có nội dung liên quan"
        }
    }
    
    result3 = format_output(state3)
    final_result3 = result3["final_result"]
    
    print("Test 3: Không có keywords nào")
    print(f"Main keywords: {state3['input_data']['main_keywords']}")
    print(f"LLM keywords: {state3['llm_analysis']['keywords']}")
    print(f"Targeted: {final_result3['targeted']}")
    print(f"Expected: False")
    print(f"Result: {'✅ PASS' if final_result3['targeted'] == False else '❌ FAIL'}")
    print()
    
    # Test case 4: Keywords trùng với case khác nhau
    state4 = {
        "input_data": {
            "id": "test_4",
            "index": "test_index_4",
            "type": "fbGroupTopic",
            "main_keywords": ["Dyson", "DSYON", "máy lọc không khí"]
        },
        "llm_analysis": {
            "sentiment": "negative",
            "confidence": 0.6,
            "keywords": {
                "positive": [],
                "negative": ["dyson"],  # lowercase
                "neutral": []
            },
            "explanation": "Đánh giá tiêu cực"
        }
    }
    
    result4 = format_output(state4)
    final_result4 = result4["final_result"]
    
    print("Test 4: Keywords trùng với case khác nhau")
    print(f"Main keywords: {state4['input_data']['main_keywords']}")
    print(f"LLM keywords: {state4['llm_analysis']['keywords']}")
    print(f"Targeted: {final_result4['targeted']}")
    print(f"Expected: True")
    print(f"Result: {'✅ PASS' if final_result4['targeted'] == True else '❌ FAIL'}")

if __name__ == "__main__":
    test_format_output_logic()