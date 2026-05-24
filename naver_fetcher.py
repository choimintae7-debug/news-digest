"""naver_fetcher.py — 네이버 검색 API를 통한 뉴스 수집"""
import re
import datetime
import requests
from config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET, MAX_ARTICLES


def fetch_articles(topic: str) -> list[dict]:
    """
    네이버 뉴스 검색 API로 최신 기사를 수집합니다.
    반환: [{"title", "source", "url", "description", "published_at"}, ...]
    """
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        return []

    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id":     NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {
        "query":  topic,
        "display": MAX_ARTICLES,
        "sort":   "date",   # 최신순
    }

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        items = resp.json().get("items", [])
    except Exception as e:
        print(f"  ⚠️  네이버 API 오류 [{topic}]: {e}")
        return []

    result = []
    for item in items:
        result.append({
            "title":        _strip_tags(item.get("title", "")),
            "source":       _extract_source(item.get("originallink", "")),
            "url":          item.get("originallink") or item.get("link", ""),
            "description":  _strip_tags(item.get("description", "요약 없음")),
            "published_at": _fmt_date(item.get("pubDate", "")),
            "_from":        "naver",
        })
    return result


# ── 유틸 ──────────────────────────────────────────────────────

def _strip_tags(text: str) -> str:
    """HTML 태그 및 엔티티 제거"""
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&quot;", '"').replace("&amp;", "&") \
               .replace("&lt;", "<").replace("&gt;", ">") \
               .replace("&#39;", "'")
    return text.strip()


def _extract_source(url: str) -> str:
    """URL에서 도메인만 추출해 출처로 사용"""
    try:
        host = url.split("//")[-1].split("/")[0]
        return host.replace("www.", "")
    except Exception:
        return "네이버 뉴스"


def _fmt_date(rfc: str) -> str:
    """RFC 2822 → 'YYYY-MM-DD HH:MM' 변환 (예: Mon, 01 Jan 2025 09:00:00 +0900)"""
    try:
        dt = datetime.datetime.strptime(rfc, "%a, %d %b %Y %H:%M:%S %z")
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return rfc
