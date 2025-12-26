#!/usr/bin/env python3
"""
Test script để kiểm tra logic targeting mới với main_keywords
"""

import requests
import json

def test_new_targeting_logic():
    """Test các scenario khác nhau cho targeting logic mới"""
    
    base_url = "http://localhost:4880/analyze"
    
    # Test case 1: Có mention main_keywords -> targeted = True
    test_case_1 = {
        "id": "test_1",
        "index": "test_index_1",
        "title": "Máy lọc không khí Dyson rất tốt",
        "content": "Tôi đã mua máy dyson và rất hài lòng với chất lượng",
        "description": "Review sản phẩm dyson",
        "type": "fbGroupTopic",
        "main_keywords": ["dyson", "máy lọc không khí"]
    }
    
    # Test case 2: Không mention main_keywords -> targeted = False
    test_case_2 = {
        "id": "test_2", 
        "index": "test_index_2",
        "title": "Hôm nay trời đẹp quá",
        "content": "Thời tiết hôm nay rất đẹp, tôi đi chơi với bạn bè",
        "description": "Chia sẻ về thời tiết",
        "type": "fbGroupTopic",
        "main_keywords": ["dyson", "máy lọc không khí"]
    }
    
    # Test case 3: Mention keywords khác -> targeted = False
    test_case_3 = {
        "id": "test_3",
        "index": "test_index_3", 
        "title": "Máy lọc Sharp rất tốt",
        "content": "Tôi đã mua máy Sharp và rất hài lòng",
        "description": "Review máy lọc Sharp",
        "type": "fbGroupTopic",
        "main_keywords": ["dyson", "máy lọc không khí"]
    }
    
    # Test case 4: Mention biến thể của main_keywords -> targeted = True
    test_case_4 = {
        "id": "test_4",
        "index": "test_index_4",
        "title": "Dýon máy lọc không khí tuyệt vời",
        "content": "Máy lọc ko khí dýon rất tốt, tôi recommend",
        "description": "Review dýon",
        "type": "fbGroupTopic", 
        "main_keywords": ["dyson", "máy lọc không khí"]
    }
    
    # Test case 5: Không có main_keywords -> targeted = False
    test_case_5 = {
        "id": "test_5",
        "index": "test_index_5",
        "title": "Sản phẩm này rất tốt",
        "content": "Tôi rất hài lòng với sản phẩm",
        "description": "Review tích cực",
        "type": "fbGroupTopic",
        "main_keywords": []
    }
    
    test_cases = [
        ("Có mention main_keywords", test_case_1, True),
        ("Không mention main_keywords", test_case_2, False),
        ("Mention keywords khác", test_case_3, False),
        ("Mention biến thể main_keywords", test_case_4, True),
        ("Không có main_keywords", test_case_5, False)
    ]
    
    print("=== Testing New Targeting Logic với Main Keywords ===\n")
    
    for description, test_data, expected_targeted in test_cases:
        print(f"=== {description} ===")
        print(f"Main keywords: {test_data.get('main_keywords', [])}")
        print(f"Text: {test_data.get('title', '')} {test_data.get('content', '')}")
        
        try:
            response = requests.post(base_url, json=test_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                actual_targeted = result.get("targeted", False)
                
                print(f"Expected targeted: {expected_targeted}")
                print(f"Actual targeted: {actual_targeted}")
                
                if actual_targeted == expected_targeted:
                    print("✅ PASS")
                else:
                    print("❌ FAIL")
                    
                print(f"Sentiment: {result.get('sentiment', 'unknown')}")
                print(f"Confidence: {result.get('confidence', 0.0)}")
                print(f"Keywords: {result.get('keywords', {})}")
                print(f"Explanation: {result.get('explanation', '')}")
                
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to API. Make sure server is running on localhost:4880")
            break
        except Exception as e:
            print(f"❌ Test error: {str(e)}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_new_targeting_logic()