"""config.py — 환경변수 로드 및 전역 설정"""
import os
from dotenv import load_dotenv

load_dotenv()

# NewsAPI
NEWSAPI_KEY          = os.getenv("NEWSAPI_KEY", "")

# Gmail SMTP
GMAIL_ADDRESS        = os.getenv("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD   = os.getenv("GMAIL_APP_PASSWORD", "")
SENDER_NAME          = os.getenv("SENDER_NAME", "뉴스 다이제스트")

# 발송 스케줄
SEND_HOUR            = int(os.getenv("SEND_HOUR", 8))
SEND_MINUTE          = int(os.getenv("SEND_MINUTE", 0))

# 뉴스 설정
NEWS_LANGUAGE        = os.getenv("NEWS_LANGUAGE", "ko")
MAX_ARTICLES         = int(os.getenv("MAX_ARTICLES_PER_TOPIC", 5))

# 네이버 검색 API
NAVER_CLIENT_ID      = os.getenv("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET  = os.getenv("NAVER_CLIENT_SECRET", "")

SUBSCRIBERS_FILE     = "subscribers.json"
