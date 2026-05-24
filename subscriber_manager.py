"""subscriber_manager.py — PostgreSQL 기반 구독자 관리"""
import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor


def _connect():
    return psycopg2.connect(os.environ["DATABASE_URL"], sslmode="require")


def init_db():
    """테이블 초기화 (최초 1회 실행)"""
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS subscribers (
                    email   TEXT PRIMARY KEY,
                    name    TEXT NOT NULL,
                    topics  TEXT NOT NULL,
                    active  BOOLEAN DEFAULT TRUE
                )
            """)
        conn.commit()


def add_subscriber(email: str, name: str, topics: list) -> str:
    email = email.strip().lower()
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO subscribers (email, name, topics, active)
                VALUES (%s, %s, %s, TRUE)
                ON CONFLICT (email) DO UPDATE
                SET name = EXCLUDED.name,
                    topics = EXCLUDED.topics,
                    active = TRUE
            """, (email, name.strip(), json.dumps(topics, ensure_ascii=False)))
        conn.commit()
    return f"✅ [{email}] 구독 등록 완료!"


def remove_subscriber(email: str) -> str:
    email = email.strip().lower()
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE subscribers SET active = FALSE WHERE email = %s", (email,))
            updated = cur.rowcount
        conn.commit()
    if updated:
        return f"✅ [{email}] 구독 취소 완료."
    return f"❌ [{email}] 등록된 구독자가 아닙니다."


def list_subscribers() -> list:
    with _connect() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT email, name, topics FROM subscribers WHERE active = TRUE")
            rows = cur.fetchall()
    result = []
    for row in rows:
        result.append({
            "email":  row["email"],
            "name":   row["name"],
            "topics": json.loads(row["topics"]),
        })
    return result
