#!/usr/bin/env python3
"""
Script test API với dữ liệu mẫu
"""
import requests
import json

# Dữ liệu test theo yêu cầu
test_data = {
    "id": "648188429745076_1253949522502296",
    "index": "6641ccbdf4901a7ae602197f",
    "title": "Xem xong cũng làm thử, trời ơi đầu tư ngay cái máy lọc kk dyson 30 củ đi, k có tí bụi mịn nào bay luôn",
    "content": "",
    "description": "T có phải nạn nhân của máy lọc không khí ko tụi bay. Hay t đã sai ở bước nào????  maylockhongkhi  sharp  xuhuong  tiktok",
    "type": "fbGroupTopic",
    "main_keywords": ["dyson","dsyon","dysom","dysson","dysonn","disson","dyxom"]
}

def test_analyze_endpoint():
    """Test endpoint /analyze"""
    url = "http://localhost:8000/analyze"
    
    try:
        print("Đang gửi request...")
        print(f"Data: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
        
        response = requests.post(url, json=test_data)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\nKết quả phân tích:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            # Kiểm tra response format
            print("\n=== Validation ===")
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
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Lỗi: Không thể kết nối đến server. Hãy chắc chắn server đang chạy.")
    except Exception as e:
        print(f"Lỗi: {str(e)}")

def test_health_endpoint():
    """Test health check endpoint"""
    url = "http://localhost:8000/health"
    
    try:
        response = requests.get(url)
        print(f"Health check: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {str(e)}")

if __name__ == "__main__":
    print("=== Test Sentiment Analysis API ===")
    
    # Test health check
    test_health_endpoint()
    print()
    
    # Test analyze endpoint
    test_analyze_endpoint()