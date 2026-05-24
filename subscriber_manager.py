"""subscriber_manager.py — 구독자 추가/삭제/조회"""
import json
import os
from config import SUBSCRIBERS_FILE


def _load() -> dict:
    if not os.path.exists(SUBSCRIBERS_FILE):
        return {}
    with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: dict) -> None:
    with open(SUBSCRIBERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_subscriber(email: str, name: str, topics: list[str]) -> str:
    """구독자를 추가합니다. 이미 존재하면 주제만 업데이트."""
    db = _load()
    email = email.strip().lower()
    if email in db:
        db[email]["topics"] = list(set(db[email]["topics"] + topics))
        _save(db)
        return f"✅ [{email}] 구독 주제 업데이트 완료: {db[email]['topics']}"
    db[email] = {"name": name.strip(), "topics": topics, "active": True}
    _save(db)
    return f"✅ [{email}] 구독 등록 완료!"


def remove_subscriber(email: str) -> str:
    """구독자를 비활성화합니다."""
    db = _load()
    email = email.strip().lower()
    if email not in db:
        return f"❌ [{email}] 등록된 구독자가 아닙니다."
    db[email]["active"] = False
    _save(db)
    return f"✅ [{email}] 구독 취소 완료."


def list_subscribers() -> list[dict]:
    """활성 구독자 목록을 반환합니다."""
    db = _load()
    return [
        {"email": email, **info}
        for email, info in db.items()
        if info.get("active", True)
    ]


def get_all_topics() -> set[str]:
    """전체 구독자의 고유 주제 목록을 반환합니다."""
    topics = set()
    for sub in list_subscribers():
        topics.update(sub["topics"])
    return topics
