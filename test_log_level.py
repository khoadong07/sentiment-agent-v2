#!/usr/bin/env python3
"""
Test script để kiểm tra logic log_level
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.nodes.format_output import calculate_log_level

def test_log_level_logic():
    """Test các trường hợp log_level"""
    
    print("=== Testing log_level logic ===\n")
    
    # Test case 1: neutral/positive sentiment -> log_level = 0
    test_cases = [
        # (sentiment, type, targeted, expected_log_level, description)
        ("neutral", "fbPageComment", True, 0, "Neutral sentiment should return 0"),
        ("positive", "fbPageComment", True, 0, "Positive sentiment should return 0"),
        
        # Test case 2: negative sentiment + comment types -> log_level = 1
        ("negative", "fbPageComment", False, 1, "Negative + fbPageComment -> 1"),
        ("negative", "fbGroupComment", True, 1, "Negative + fbGroupComment -> 1"),
        ("negative", "youtubeComment", False, 1, "Negative + youtubeComment -> 1"),
        ("negative", "tiktokComment", True, 1, "Negative + tiktokComment -> 1"),
        
        # Test case 3: negative sentiment + topic types + targeted -> log_level = 2
        ("negative", "fbPageTopic", True, 2, "Negative + fbPageTopic + targeted -> 2"),
        ("negative", "fbGroupTopic", True, 2, "Negative + fbGroupTopic + targeted -> 2"),
        ("negative", "youtubeTopic", True, 2, "Negative + youtubeTopic + targeted -> 2"),
        
        # Test case 4: negative sentiment + topic types + not targeted -> log_level = 0
        ("negative", "fbPageTopic", False, 0, "Negative + fbPageTopic + not targeted -> 0"),
        ("negative", "youtubeTopic", False, 0, "Negative + youtubeTopic + not targeted -> 0"),
        
        # Test case 5: negative sentiment + newsTopic + targeted -> log_level = 3
        ("negative", "newsTopic", True, 3, "Negative + newsTopic + targeted -> 3"),
        
        # Test case 6: negative sentiment + newsTopic + not targeted -> log_level = 0
        ("negative", "newsTopic", False, 0, "Negative + newsTopic + not targeted -> 0"),
        
        # Test case 7: unknown types
        ("negative", "unknownType", True, 0, "Negative + unknown type -> 0"),
    ]
    
    all_passed = True
    
    for sentiment, content_type, targeted, expected, description in test_cases:
        result = calculate_log_level(sentiment, content_type, targeted)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        
        if result != expected:
            all_passed = False
            
        print(f"{status} | {description}")
        print(f"      Input: sentiment='{sentiment}', type='{content_type}', targeted={targeted}")
        print(f"      Expected: {expected}, Got: {result}")
        print()
    
    print("=" * 50)
    if all_passed:
        print("🎉 All tests PASSED!")
    else:
        print("💥 Some tests FAILED!")
    
    return all_passed

if __name__ == "__main__":
    test_log_level_logic()