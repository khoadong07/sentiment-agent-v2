#!/usr/bin/env python3
"""
Test script để kiểm tra API với main_keywords trực tiếp
Output không còn field 'topic'
"""

import requests
import json

# Test data với main_keywords
test_data = {
    "id": "648188429745076_1253949522502296",
    "index": "6641ccbdf4901a7ae602197f", 
    "title": "dyson đi ạ.. mêeee❤️❤️❤️, tốt lắm",
    "content": "",
    "description": "T có phải nạn nhân của máy lọc không khí ko tụi bay. Hay t đã sai ở bước nào????  maylockhongkhi  sharp  xuhuong  tiktok",
    "type": "fbGroupTopic",
    "main_keywords": ["dyson", "dýon"]
}

def test_api():
    """Test API endpoint"""
    try:
        url = "http://localhost:8000/analyze"
        
        print("Testing API với main_keywords...")
        print(f"Data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=test_data)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Test failed: {str(e)}")

def test_validation():
    """Test validation endpoint"""
    try:
        url = "http://localhost:8000/test-validation"
        
        print("\nTesting validation...")
        response = requests.post(url, json=test_data)
        
        print(f"Validation Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Validation Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"Validation Error: {response.text}")
            
    except Exception as e:
        print(f"Validation test failed: {str(e)}")

if __name__ == "__main__":
    test_validation()
    test_api()