import os, json
import urllib.parse
import pg8000


def _connect():
    url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
    return pg8000.connect(
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port or 5432,
        database=url.path.lstrip("/"),
        ssl_context=True,
    )


def init_db():
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            email  TEXT PRIMARY KEY,
            name   TEXT NOT NULL,
            topics TEXT NOT NULL,
            active BOOLEAN DEFAULT TRUE
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


def add_subscriber(email, name, topics):
    email = email.strip().lower()
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO subscribers (email, name, topics, active)
        VALUES (%s, %s, %s, TRUE)
        ON CONFLICT (email) DO UPDATE
        SET name = EXCLUDED.name,
            topics = EXCLUDED.topics,
            active = TRUE
    """, (email, name.strip(), json.dumps(topics, ensure_ascii=False)))
    conn.commit()
    cur.close()
    conn.close()
    return f"✅ [{email}] 구독 등록 완료!"


def remove_subscriber(email):
    email = email.strip().lower()
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "UPDATE subscribers SET active = FALSE WHERE email = %s", (email,)
    )
    updated = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    if updated:
        return f"✅ [{email}] 구독 취소 완료."
    return f"❌ [{email}] 등록된 구독자가 아닙니다."


def list_subscribers():
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT email, name, topics FROM subscribers WHERE active = TRUE"
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {"email": r[0], "name": r[1], "topics": json.loads(r[2])}
        for r in rows
    ]
