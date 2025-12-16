#!/usr/bin/env python3
"""
Debug script cho lỗi 422 Unprocessable Entity
"""
import requests
import json

# Test data theo đúng format yêu cầu
test_data = {
    "id": "648188429745076_1253949522502296",
    "index": "6641ccbdf4901a7ae602197f",
    "title": "Xem xong cũng làm thử, trời ơi đầu tư ngay cái máy lọc kk dyson 30 củ đi, k có tí bụi mịn nào bay luôn",
    "content": "",
    "description": "T có phải nạn nhân của máy lọc không khí ko tụi bay. Hay t đã sai ở bước nào????  maylockhongkhi  sharp  xuhuong  tiktok",
    "type": "fbGroupTopic"
}

def test_validation():
    """Test validation endpoint"""
    url = "http://localhost:8000/test-validation"
    
    print("Testing validation...")
    print(f"Data: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=test_data)
        print(f"\nValidation Response ({response.status_code}):")
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"Validation test error: {str(e)}")

def test_analyze():
    """Test analyze endpoint"""
    url = "http://localhost:8000/analyze"
    
    print("\n" + "="*50)
    print("Testing analyze endpoint...")
    
    try:
        response = requests.post(url, json=test_data)
        print(f"\nAnalyze Response ({response.status_code}):")
        
        if response.status_code == 200:
            result = response.json()
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("Error response:")
            print(response.text)
            
    except Exception as e:
        print(f"Analyze test error: {str(e)}")

def test_different_formats():
    """Test với các format khác nhau"""
    print("\n" + "="*50)
    print("Testing different data formats...")
    
    # Test 1: Missing optional fields
    test1 = {
        "id": "test1",
        "index": "6641ccbdf4901a7ae602197f"
    }
    
    # Test 2: Empty strings
    test2 = {
        "id": "test2", 
        "index": "6641ccbdf4901a7ae602197f",
        "title": "",
        "content": "",
        "description": "",
        "type": ""
    }
    
    # Test 3: None values
    test3 = {
        "id": "test3",
        "index": "6641ccbdf4901a7ae602197f", 
        "title": None,
        "content": None,
        "description": None,
        "type": None
    }
    
    tests = [("Missing fields", test1), ("Empty strings", test2), ("None values", test3)]
    
    for name, data in tests:
        print(f"\n--- {name} ---")
        try:
            response = requests.post("http://localhost:8000/test-validation", json=data)
            result = response.json()
            print(f"Status: {result.get('status')}")
            if result.get('status') == 'invalid':
                print(f"Error: {result.get('error')}")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("🔍 Debugging 422 Unprocessable Entity Error")
    
    # Test validation first
    test_validation()
    
    # Test different formats
    test_different_formats()
    
    # Test actual analyze endpoint
    test_analyze()