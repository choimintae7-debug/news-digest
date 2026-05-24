"""main.py — 로컬 실행용"""
from subscriber_manager import init_db
from app import app
import threading
from scheduler import start_scheduler_background

if __name__ == "__main__":
    init_db()
    t = threading.Thread(target=start_scheduler_background, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5000, debug=False)
