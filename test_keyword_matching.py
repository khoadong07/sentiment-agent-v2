#!/usr/bin/env python3
"""
Test cụ thể cho keyword matching logic
"""

import requests
import json

def test_keyword_matching():
    """Test các trường hợp keyword matching"""
    
    base_url = "http://localhost:4880/analyze"
    
    test_cases = [
        {
            "name": "Có keyword trùng chính xác",
            "data": {
                "id": "test_exact_match",
                "index": "test_1",
                "title": "Máy lọc không khí Dyson V15 rất tốt",
                "content": "",
                "description": "Tôi vừa mua máy dyson và rất hài lòng với chất lượng",
                "type": "fbGroupTopic",
                "main_keywords": ["dyson", "dsyon", "máy lọc không khí"]
            },
            "expected_targeted": True,
            "expected_keywords_found": True
        },
        {
            "name": "Có keyword với typo trong main_keywords",
            "data": {
                "id": "test_typo_match", 
                "index": "test_2",
                "title": "Máy dsyon rất tốt",
                "content": "",
                "description": "Tôi vừa mua máy dsyon và rất hài lòng",
                "type": "fbGroupTopic",
                "main_keywords": ["dyson", "dsyon", "máy lọc không khí"]
            },
            "expected_targeted": True,
            "expected_keywords_found": True
        },
        {
            "name": "Có từ khóa liên quan nhưng không trong main_keywords",
            "data": {
                "id": "test_related_but_not_main",
                "index": "test_3", 
                "title": "Máy lọc Sharp rất tốt",
                "content": "",
                "description": "Tôi vừa mua máy Sharp và rất hài lòng với máy lọc không khí này",
                "type": "fbGroupTopic",
                "main_keywords": ["dyson", "dsyon", "disson"]
            },
            "expected_targeted": False,
            "expected_keywords_found": False
        },
        {
            "name": "Không có keyword nào được đề cập",
            "data": {
                "id": "test_no_keywords",
                "index": "test_4",
                "title": "Hôm nay trời đẹp quá",
                "content": "",
                "description": "Thời tiết hôm nay rất đẹp, tôi đi chơi với bạn bè",
                "type": "fbGroupTopic", 
                "main_keywords": ["dyson", "dsyon", "máy lọc không khí"]
            },
            "expected_targeted": False,
            "expected_keywords_found": False
        },
        {
            "name": "Có cả keyword chính và từ liên quan",
            "data": {
                "id": "test_mixed",
                "index": "test_5",
                "title": "So sánh máy lọc không khí Dyson vs Sharp",
                "content": "",
                "description": "Tôi đang phân vân giữa máy dyson và sharp, cả hai đều là máy lọc không khí tốt",
                "type": "fbGroupTopic",
                "main_keywords": ["dyson", "dsyon", "máy lọc không khí"]
            },
            "expected_targeted": True,
            "expected_keywords_found": True
        }
    ]
    
    print("=== Test Keyword Matching Logic ===\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        print(f"   Main keywords: {test_case['data']['main_keywords']}")
        print(f"   Text: {test_case['data']['title']} {test_case['data']['description']}")
        
        try:
            response = requests.post(base_url, json=test_case['data'], timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                actual_targeted = result.get("targeted", False)
                keywords = result.get("keywords", {})
                
                # Kiểm tra xem có keywords nào được tìm thấy không
                found_any_keywords = any([
                    keywords.get("positive", []),
                    keywords.get("negative", []),
                    keywords.get("neutral", [])
                ])
                
                print(f"   Expected targeted: {test_case['expected_targeted']}")
                print(f"   Actual targeted: {actual_targeted}")
                print(f"   Keywords found: {keywords}")
                print(f"   Sentiment: {result.get('sentiment', 'unknown')}")
                
                # Kiểm tra kết quả
                targeted_correct = actual_targeted == test_case['expected_targeted']
                keywords_correct = found_any_keywords == test_case['expected_keywords_found']
                
                if targeted_correct and keywords_correct:
                    print("   ✅ PASS")
                else:
                    print("   ❌ FAIL")
                    if not targeted_correct:
                        print(f"      - Targeted mismatch")
                    if not keywords_correct:
                        print(f"      - Keywords mismatch")
                        
            else:
                print(f"   ❌ API Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Cannot connect to API. Make sure server is running on localhost:8000")
            break
        except Exception as e:
            print(f"   ❌ Test error: {str(e)}")
            
        print()

if __name__ == "__main__":
    test_keyword_matching()