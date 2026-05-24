"""main.py — Flask 앱 + 스케줄러 동시 실행"""
import threading
from app import app
from scheduler import start_scheduler_background

# Railway/gunicorn이 import할 때 스케줄러 자동 시작
_scheduler_started = False

def _start_once():
    global _scheduler_started
    if not _scheduler_started:
        _scheduler_started = True
        t = threading.Thread(target=start_scheduler_background, daemon=True)
        t.start()

_start_once()

if __name__ == "__main__":
    print("🌐 웹서버 시작: http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
