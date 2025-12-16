#!/usr/bin/env python3
"""
Test script để kiểm tra logic targeting mới
"""

import requests
import json

def test_targeting_scenarios():
    """Test các scenario khác nhau cho targeting logic"""
    
    base_url = "http://localhost:4880/analyze"
    
    # Test case 1: Có keywords trùng với main_keywords -> targeted = True
    test_case_1 = {
        "id": "test_1",
        "index": "test_index_1",
        "title": "Máy lọc không khí Dyson rất tốt",
        "content": "",
        "description": "Tôi đã mua máy dyson và rất hài lòng",
        "type": "fbGroupTopic",
        "main_keywords": ["dyson", "máy lọc không khí"]
    }
    
    # Test case 2: Không có keywords trùng -> targeted = False
    test_case_2 = {
        "id": "test_2", 
        "index": "test_index_2",
        "title": "Hôm nay trời đẹp quá",
        "content": "",
        "description": "Thời tiết hôm nay rất đẹp, tôi đi chơi",
        "type": "fbGroupTopic",
        "main_keywords": ["dyson", "máy lọc không khí"]
    }
    
    # Test case 3: Có keywords khác nhưng không trùng main_keywords -> targeted = False
    test_case_3 = {
        "id": "test_3",
        "index": "test_index_3", 
        "title": "Máy lọc Sharp rất tốt",
        "content": "",
        "description": "Tôi đã mua máy Sharp và rất hài lòng",
        "type": "fbGroupTopic",
        "main_keywords": ["dyson", "máy lọc không khí"]
    }
    
    test_cases = [
        ("Keywords trùng với main_keywords", test_case_1, True),
        ("Không có keywords trùng", test_case_2, False),
        ("Có keywords khác nhưng không trùng", test_case_3, False)
    ]
    
    for description, test_data, expected_targeted in test_cases:
        print(f"\n=== {description} ===")
        print(f"Request: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
        
        try:
            response = requests.post(base_url, json=test_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                actual_targeted = result.get("targeted", False)
                
                print(f"Response targeted: {actual_targeted}")
                print(f"Expected targeted: {expected_targeted}")
                
                if actual_targeted == expected_targeted:
                    print("✅ PASS")
                else:
                    print("❌ FAIL")
                    
                print(f"Keywords found: {result.get('keywords', {})}")
                print(f"Sentiment: {result.get('sentiment', 'unknown')}")
                
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to API. Make sure server is running on localhost:8000")
            break
        except Exception as e:
            print(f"❌ Test error: {str(e)}")

if __name__ == "__main__":
    print("=== Testing Targeting Logic ===")
    test_targeting_scenarios()