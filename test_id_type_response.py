#!/usr/bin/env python3
"""
Test script để kiểm tra API trả về id và type từ request
"""

import requests
import json

def test_api_response():
    """Test API với sample data để kiểm tra id và type trong response"""
    
    # Sample data giống như trong yêu cầu
    test_data = {
        "id": "648188429745076_1253949522502296",
        "index": "6641ccbdf4901a7ae602197f",
        "title": " ko mua nữa mêeee❤️❤️❤️, tốt lắm",
        "content": "",
        "description": "T có phải nạn nhân dcủa máy lọc không khí ko tụi bay. Hay t đã sai ở bước nào????  maylockhongkhi  sharp  xuhuong  tiktok",
        "type": "fbGroupTopic",
        "main_keywords": ["dyson","dsyon","dysom","dysson","dysonn","disson","dyxom"]
    }
    
    try:
        # Test với local server
        url = "http://localhost:8000/analyze"
        
        print("Testing API response format...")
        print(f"Request data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=test_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nResponse: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # Kiểm tra các field bắt buộc
            required_fields = ["id", "index", "type", "targeted", "sentiment", "confidence", "keywords", "explanation"]
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields:
                print(f"❌ Missing fields: {missing_fields}")
            else:
                print("✅ All required fields present")
                
            # Kiểm tra id và type có khớp với request không
            if result.get("id") == test_data["id"]:
                print("✅ ID matches request")
            else:
                print(f"❌ ID mismatch: expected {test_data['id']}, got {result.get('id')}")
                
            if result.get("type") == test_data["type"]:
                print("✅ Type matches request")
            else:
                print(f"❌ Type mismatch: expected {test_data['type']}, got {result.get('type')}")
                
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Test error: {str(e)}")

if __name__ == "__main__":
    test_api_response()