"""news_fetcher.py — NewsAPI + 네이버 뉴스 통합 수집"""
import datetime
from newsapi import NewsApiClient
from config import NEWSAPI_KEY, NEWS_LANGUAGE, MAX_ARTICLES
import naver_fetcher


def fetch_articles(topic: str) -> list[dict]:
    """
    NewsAPI + 네이버 뉴스를 합산하여 중복 제거 후 반환합니다.
    반환: [{"title", "source", "url", "description", "published_at", "_from"}, ...]
    """
    newsapi_articles = _fetch_newsapi(topic)
    naver_articles   = naver_fetcher.fetch_articles(topic)

    merged = _merge_and_deduplicate(newsapi_articles, naver_articles)
    return merged[:MAX_ARTICLES * 2]   # 전체 최대 개수 = 각 소스 MAX의 2배


def fetch_for_subscriber(topics: list[str]) -> dict[str, list[dict]]:
    """구독 주제별 기사 딕셔너리를 반환합니다."""
    return {topic: fetch_articles(topic) for topic in topics}


# ── NewsAPI ───────────────────────────────────────────────────

def _fetch_newsapi(topic: str) -> list[dict]:
    if not NEWSAPI_KEY:
        return []

    client = NewsApiClient(api_key=NEWSAPI_KEY)
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

    try:
        response = client.get_everything(
            q=topic,
            language=NEWS_LANGUAGE,
            from_param=yesterday,
            sort_by="relevancy",
            page_size=MAX_ARTICLES,
        )
        articles = response.get("articles", [])
    except Exception as e:
        print(f"  ⚠️  NewsAPI 오류 [{topic}]: {e}")
        return []

    result = []
    for a in articles:
        if a.get("title") and a.get("url"):
            result.append({
                "title":        a["title"],
                "source":       a.get("source", {}).get("name", "출처 미상"),
                "url":          a["url"],
                "description":  a.get("description") or "요약 정보 없음",
                "published_at": _fmt_date(a.get("publishedAt", "")),
                "_from":        "newsapi",
            })
    return result


# ── 중복 제거 ─────────────────────────────────────────────────

def _merge_and_deduplicate(
    newsapi: list[dict],
    naver:   list[dict],
) -> list[dict]:
    """
    URL 기준으로 중복을 제거하고, 네이버 → NewsAPI 순으로 정렬합니다.
    (한국어 환경에서는 네이버 기사를 우선 노출)
    """
    seen_urls   = set()
    seen_titles = set()
    merged      = []

    for article in naver + newsapi:   # 네이버 우선
        url   = article.get("url", "").strip()
        title = article.get("title", "").strip()[:30]   # 앞 30자로 유사 제목 검사

        if url in seen_urls or title in seen_titles:
            continue

        seen_urls.add(url)
        seen_titles.add(title)
        merged.append(article)

    return merged


# ── 유틸 ──────────────────────────────────────────────────────

def _fmt_date(iso: str) -> str:
    try:
        dt = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso
