#!/usr/bin/env python3
"""
Test script để kiểm tra API với main_keywords trực tiếp
Output không còn field 'topic'
"""

import requests
import json

# Test data với main_keywords - có mention keywords
test_data_with_keywords = {
    "id": "648188429745076_1253949522502296",
    "index": "6641ccbdf4901a7ae602197f", 
    "title": "dyson đi ạ.. mêeee❤️❤️❤️, tốt lắm",
    "content": "",
    "description": "T có phải nạn nhân của máy lọc không khí ko tụi bay. Hay t đã sai ở bước nào????  maylockhongkhi  sharp  xuhuong  tiktok",
    "type": "fbGroupTopic",
    "main_keywords": ["dyson", "dýon"]
}

# Test data không mention keywords - sẽ phân tích sentiment tổng quan
test_data_no_keywords = {
    "id": "648188429745076_1253949522502297",
    "index": "6641ccbdf4901a7ae602197g", 
    "title": "Hôm nay trời đẹp quá, vui lắm ạ!",
    "content": "Mọi người có khỏe không? Chúc mọi người một ngày tốt lành nhé!",
    "description": "Chia sẻ niềm vui với mọi người",
    "type": "fbGroupTopic",
    "main_keywords": ["dyson", "dýon"]
}

def test_api_with_keywords():
    """Test API với content có mention keywords"""
    try:
        url = "http://localhost:4880/analyze"
        
        print("=== Testing API với content có mention keywords ===")
        print(f"Data: {json.dumps(test_data_with_keywords, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=test_data_with_keywords)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Test failed: {str(e)}")

def test_api_no_keywords():
    """Test API với content không mention keywords"""
    try:
        url = "http://localhost:4880/analyze"
        
        print("\n=== Testing API với content KHÔNG mention keywords ===")
        print(f"Data: {json.dumps(test_data_no_keywords, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=test_data_no_keywords)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
            print(f"Explanation should note: 'Nội dung không đề cập đến main keywords'")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Test failed: {str(e)}")

def test_validation():
    """Test validation endpoint"""
    try:
        url = "http://localhost:4880/test-validation"
        
        print("\n=== Testing validation ===")
        response = requests.post(url, json=test_data_with_keywords)
        
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
    test_api_with_keywords()
    test_api_no_keywords()