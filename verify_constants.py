#!/usr/bin/env python3
"""
Verify constants được định nghĩa đúng
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.constants import COMMENT_TYPES, TOPIC_TYPES, NEWS_TOPIC_TYPE
    
    print("✅ Import constants thành công!")
    print(f"📝 COMMENT_TYPES ({len(COMMENT_TYPES)} items):")
    for i, comment_type in enumerate(COMMENT_TYPES, 1):
        print(f"  {i:2d}. {comment_type}")
    
    print(f"\n📝 TOPIC_TYPES ({len(TOPIC_TYPES)} items):")
    for i, topic_type in enumerate(TOPIC_TYPES, 1):
        print(f"  {i:2d}. {topic_type}")
    
    print(f"\n📝 NEWS_TOPIC_TYPE: {NEWS_TOPIC_TYPE}")
    
    # Verify danh sách comment types theo yêu cầu
    expected_comment_types = [
        "fbPageComment", "fbGroupComment", "fbUserComment", "forumComment",
        "newsComment", "youtubeComment", "tiktokComment", "snsComment",
        "linkedinComment", "ecommerceComment", "threadsComment", "comment"
    ]
    
    print(f"\n🔍 Kiểm tra danh sách comment types:")
    print(f"Expected: {len(expected_comment_types)} items")
    print(f"Actual: {len(COMMENT_TYPES)} items")
    
    missing = set(expected_comment_types) - set(COMMENT_TYPES)
    extra = set(COMMENT_TYPES) - set(expected_comment_types)
    
    if missing:
        print(f"❌ Thiếu: {missing}")
    if extra:
        print(f"⚠️  Thừa: {extra}")
    
    if not missing and not extra:
        print("✅ Danh sách comment types chính xác!")
    
except Exception as e:
    print(f"❌ Lỗi import: {e}")