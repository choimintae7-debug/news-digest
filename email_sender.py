"""email_sender.py — Gmail SMTP (포트 587) 발송"""
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

GMAIL_ADDRESS      = os.environ.get("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
SENDER_NAME        = os.environ.get("SENDER_NAME", "뉴스 다이제스트")


def _source_badge(from_: str) -> str:
    if from_ == "naver":
        return '<span style="font-size:10px;font-weight:700;background:#03C75A;color:#fff;border-radius:4px;padding:1px 5px;margin-right:6px;">N 네이버</span>'
    return '<span style="font-size:10px;font-weight:700;background:#4F8EF7;color:#fff;border-radius:4px;padding:1px 5px;margin-right:6px;">G 글로벌</span>'


def _build_html(name: str, articles_by_topic: dict) -> str:
    today = datetime.date.today().strftime("%Y년 %m월 %d일")
    topic_blocks = ""
    for topic, articles in articles_by_topic.items():
        if not articles:
            continue
        items_html = ""
        for a in articles:
            badge = _source_badge(a.get("_from", "newsapi"))
            items_html += f"""
            <div style="border-left:3px solid #4F8EF7;padding:10px 14px;margin-bottom:14px;background:#f8faff;border-radius:0 8px 8px 0;">
              <a href="{a['url']}" style="font-size:15px;font-weight:600;color:#1a1a2e;text-decoration:none;">{a['title']}</a>
              <p style="margin:6px 0 4px;font-size:13px;color:#555;">{a['description'][:120]}...</p>
              <span style="font-size:12px;color:#888;">{badge}📰 {a['source']} &nbsp;·&nbsp; 🕐 {a['published_at']}</span>
            </div>"""
        topic_blocks += f"""
        <div style="margin-bottom:32px;">
          <h2 style="font-size:18px;font-weight:700;color:#4F8EF7;border-bottom:2px solid #e8edf5;padding-bottom:8px;margin-bottom:14px;">🔍 {topic}</h2>
          {items_html}
        </div>"""
    if not topic_blocks:
        topic_blocks = "<p style='color:#888;'>오늘은 수집된 기사가 없습니다.</p>"
    return f"""<!DOCTYPE html><html lang="ko">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#eef2f7;font-family:'Apple SD Gothic Neo',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#eef2f7;padding:32px 0;">
    <tr><td align="center">
      <table width="620" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">
        <tr><td style="background:linear-gradient(135deg,#4F8EF7,#8A56F7);padding:32px 40px;">
          <h1 style="margin:0;color:#fff;font-size:26px;">📬 뉴스 다이제스트</h1>
          <p style="margin:8px 0 0;color:rgba(255,255,255,0.85);font-size:14px;">{today} | {name}님을 위한 맞춤 뉴스</p>
        </td></tr>
        <tr><td style="padding:32px 40px;">{topic_blocks}</td></tr>
        <tr><td style="background:#f4f6fb;padding:20px 40px;text-align:center;border-top:1px solid #e8edf5;">
          <p style="margin:0;font-size:12px;color:#aaa;">본 메일은 자동 발송됩니다</p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body></html>"""


def send_newsletter(to_email: str, name: str, articles_by_topic: dict) -> bool:
    today = datetime.date.today().strftime("%Y/%m/%d")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📬 [{today}] 오늘의 뉴스 다이제스트"
    msg["From"]    = f"{SENDER_NAME} <{GMAIL_ADDRESS}>"
    msg["To"]      = f"{name} <{to_email}>"
    msg.attach(MIMEText(_build_html(name, articles_by_topic), "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, to_email, msg.as_string())
        print(f"  ✅ 발송 성공 → {to_email}")
        return True
    except Exception as e:
        print(f"  ❌ 발송 오류 → {to_email}: {e}")
        return False
