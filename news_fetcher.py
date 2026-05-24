"""news_fetcher.py — NewsAPI(영어+한국어) + 네이버 뉴스 통합 수집"""
import datetime
from newsapi import NewsApiClient
from config import NEWSAPI_KEY, MAX_ARTICLES
import naver_fetcher


def fetch_articles(topic: str) -> list[dict]:
    newsapi_en = _fetch_newsapi(topic, "en")
    newsapi_ko = _fetch_newsapi(topic, "ko")
    naver      = naver_fetcher.fetch_articles(topic)
    return _merge(naver + newsapi_ko + newsapi_en)[:MAX_ARTICLES * 2]


def fetch_for_subscriber(topics: list[str]) -> dict[str, list[dict]]:
    return {topic: fetch_articles(topic) for topic in topics}


def _fetch_newsapi(topic: str, language: str) -> list[dict]:
    if not NEWSAPI_KEY:
        return []
    client = NewsApiClient(api_key=NEWSAPI_KEY)
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    try:
        response = client.get_everything(
            q=topic, language=language,
            from_param=yesterday, sort_by="relevancy",
            page_size=MAX_ARTICLES,
        )
        articles = response.get("articles", [])
    except Exception as e:
        print(f"  ⚠️  NewsAPI 오류 [{topic}][{language}]: {e}")
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


def _merge(articles: list[dict]) -> list[dict]:
    seen_urls, seen_titles, merged = set(), set(), []
    for a in articles:
        url   = a.get("url", "").strip()
        title = a.get("title", "").strip()[:30]
        if url in seen_urls or title in seen_titles:
            continue
        seen_urls.add(url)
        seen_titles.add(title)
        merged.append(a)
    return merged


def _fmt_date(iso: str) -> str:
    try:
        dt = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso
