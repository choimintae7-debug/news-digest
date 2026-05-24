"""scheduler.py — 백그라운드 스케줄러"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import datetime

from config import SEND_HOUR, SEND_MINUTE
from subscriber_manager import list_subscribers
from news_fetcher import fetch_for_subscriber
from email_sender import send_newsletter


def run_digest():
    subscribers = list_subscribers()
    if not subscribers:
        print("  ℹ️  활성 구독자가 없습니다.")
        return

    print(f"\n{'─'*50}")
    print(f"  📬 발송 시작 — {datetime.datetime.now():%Y-%m-%d %H:%M}")
    print(f"  총 {len(subscribers)}명")
    print(f"{'─'*50}")

    for sub in subscribers:
        print(f"  → {sub['name']} ({sub['email']})")
        articles = fetch_for_subscriber(sub["topics"])
        send_newsletter(sub["email"], sub["name"], articles)

    print(f"{'─'*50}\n")


def start_scheduler_background():
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    trigger = CronTrigger(hour=SEND_HOUR, minute=SEND_MINUTE, timezone="Asia/Seoul")
    scheduler.add_job(run_digest, trigger)
    scheduler.start()
    print(f"⏰ 스케줄러 시작 — 매일 {SEND_HOUR:02d}:{SEND_MINUTE:02d} KST 발송")

    # 스레드가 종료되지 않도록 유지
    import time
    while True:
        time.sleep(60)
