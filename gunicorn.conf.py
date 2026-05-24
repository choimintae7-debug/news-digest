"""gunicorn.conf.py — 스케줄러를 gunicorn 시작 시 한 번만 실행"""
import threading
from subscriber_manager import init_db
from scheduler import start_scheduler_background

workers = 1
bind = "0.0.0.0:8080"
timeout = 120


def on_starting(server):
    """gunicorn 마스터 프로세스 시작 시 1회 실행"""
    init_db()
    t = threading.Thread(target=start_scheduler_background, daemon=True)
    t.start()
