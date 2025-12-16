#!/usr/bin/env python3
"""
Test với request gốc từ user
"""

import requests
import json

def test_original_request():
    """Test với data gốc từ user"""
    
    original_data = {
        "id": "648188429745076_1253949522502296",
        "index": "6641ccbdf4901a7ae602197f", 
        "title": " ko mua nữa mêeee❤️❤️❤️, tốt lắm",
        "content": "",
        "description": "T có phải nạn nhân dcủa máy lọc không khí ko tụi bay. Hay t đã sai ở bước nào????  maylockhongkhi  sharp  xuhuong  tiktok",
        "type": "fbGroupTopic",
        "main_keywords": ["dyson","dsyon","dysom","dysson","dysonn","disson","dyxom"]
    }
    
    url = "http://localhost:4880/analyze"
    
    print("=== Test Original Request ===")
    print(f"Request: {json.dumps(original_data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=original_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nResponse: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # Kiểm tra các field bắt buộc
            required_fields = ["id", "index", "type", "targeted", "sentiment", "confidence", "keywords", "explanation"]
            missing_fields = [field for field in required_fields if field not in result]
            
            print(f"\n=== Validation ===")
            if missing_fields:
                print(f"❌ Missing fields: {missing_fields}")
            else:
                print("✅ All required fields present")
                
            # Kiểm tra id và type
            if result.get("id") == original_data["id"]:
                print("✅ ID matches request")
            else:
                print(f"❌ ID mismatch")
                
            if result.get("type") == original_data["type"]:
                print("✅ Type matches request")
            else:
                print(f"❌ Type mismatch")
            
            # Phân tích kết quả
            print(f"\n=== Analysis Result ===")
            print(f"Targeted: {result.get('targeted')}")
            print(f"Sentiment: {result.get('sentiment')}")
            print(f"Confidence: {result.get('confidence')}")
            print(f"Keywords: {result.get('keywords')}")
            print(f"Explanation: {result.get('explanation')}")
            
            # Kiểm tra logic targeting
            keywords = result.get('keywords', {})
            found_keywords = []
            main_keywords_lower = [kw.lower() for kw in original_data['main_keywords']]
            
            for category in ["positive", "negative", "neutral"]:
                for kw in keywords.get(category, []):
                    if kw.lower() in main_keywords_lower:
                        found_keywords.append(kw)
            
            expected_targeted = len(found_keywords) > 0
            actual_targeted = result.get('targeted', False)
            
            print(f"\n=== Targeting Logic Check ===")
            print(f"Main keywords: {original_data['main_keywords']}")
            print(f"Found matching keywords: {found_keywords}")
            print(f"Expected targeted: {expected_targeted}")
            print(f"Actual targeted: {actual_targeted}")
            
            if expected_targeted == actual_targeted:
                print("✅ Targeting logic correct")
            else:
                print("❌ Targeting logic incorrect")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_original_request()