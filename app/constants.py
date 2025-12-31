"""
Constants cho sentiment analysis system
"""

# Định nghĩa các loại comment types
COMMENT_TYPES = [
    "fbPageComment", "fbGroupComment", "fbUserComment", "forumComment",
    "newsComment", "youtubeComment", "tiktokComment", "snsComment",
    "linkedinComment", "ecommerceComment", "threadsComment", "comment"
]

# Định nghĩa các loại topic types
TOPIC_TYPES = [
    "fbPageTopic", "fbGroupTopic", "fbUserTopic", "forumTopic",
    "youtubeTopic", "tiktokTopic", "snsTopic", "linkedinTopic",
    "ecommerceTopic", "threadsTopic"
]

# News topic type (có log_level riêng)
NEWS_TOPIC_TYPE = "newsTopic"