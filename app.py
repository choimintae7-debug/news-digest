"""app.py — Flask 구독 웹 서버"""
from flask import Flask, request, render_template_string, redirect, url_for
from subscriber_manager import add_subscriber, remove_subscriber

app = Flask(__name__)

# ── 미리 정의된 주제 목록 ─────────────────────────────────────
TOPIC_OPTIONS = [
    "태양광", "풍력", "ESG", "에너지전환", "탄소중립",
    "반도체", "AI", "전기차", "배터리", "우주",
    "부동산", "주식", "코인", "스타트업", "글로벌경제",
]

# ── HTML 템플릿 ───────────────────────────────────────────────
BASE_STYLE = """
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #eef2f7; font-family: 'Apple SD Gothic Neo', Arial, sans-serif; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 24px; }
  .card { background: #fff; border-radius: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.10); max-width: 520px; width: 100%; overflow: hidden; }
  .header { background: linear-gradient(135deg,#4F8EF7,#8A56F7); padding: 36px 40px; }
  .header h1 { color: #fff; font-size: 24px; font-weight: 700; }
  .header p  { color: rgba(255,255,255,0.85); font-size: 14px; margin-top: 6px; }
  .body { padding: 32px 40px; }
  label { display: block; font-size: 13px; font-weight: 600; color: #444; margin-bottom: 6px; margin-top: 18px; }
  input[type=text], input[type=email] {
    width: 100%; padding: 10px 14px; border: 1.5px solid #dde3f0;
    border-radius: 10px; font-size: 14px; outline: none; transition: border 0.2s;
  }
  input:focus { border-color: #4F8EF7; }
  .topics { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
  .topic-chip input { display: none; }
  .topic-chip label {
    display: inline-block; padding: 6px 14px; border-radius: 20px;
    border: 1.5px solid #dde3f0; font-size: 13px; color: #555;
    cursor: pointer; transition: all 0.15s; margin: 0;
  }
  .topic-chip input:checked + label { background: #4F8EF7; border-color: #4F8EF7; color: #fff; font-weight: 600; }
  .btn { display: block; width: 100%; margin-top: 28px; padding: 14px; background: linear-gradient(135deg,#4F8EF7,#8A56F7); color: #fff; border: none; border-radius: 12px; font-size: 16px; font-weight: 700; cursor: pointer; transition: opacity 0.2s; }
  .btn:hover { opacity: 0.9; }
  .msg { text-align: center; padding: 18px; border-radius: 12px; margin-bottom: 18px; font-size: 14px; font-weight: 600; }
  .msg.ok  { background: #e8f5e9; color: #2e7d32; }
  .msg.err { background: #fdecea; color: #c62828; }
  .footer { text-align: center; padding: 16px; font-size: 12px; color: #aaa; border-top: 1px solid #f0f0f0; }
  a { color: #4F8EF7; text-decoration: none; }
</style>
"""

SUBSCRIBE_HTML = """
<!DOCTYPE html><html lang="ko"><head>{style}<title>뉴스 다이제스트 구독</title></head>
<body><div class="card">
  <div class="header">
    <h1>📬 뉴스 다이제스트</h1>
    <p>관심 주제의 최신 뉴스를 매일 이메일로 받아보세요</p>
  </div>
  <div class="body">
    {msg}
    <form method="POST" action="/subscribe">
      <label>이름</label>
      <input type="text" name="name" placeholder="홍길동" required>
      <label>이메일</label>
      <input type="email" name="email" placeholder="example@gmail.com" required>
      <label>관심 주제 (복수 선택 가능)</label>
      <div class="topics">
        {chips}
      </div>
      <button class="btn" type="submit">구독하기 →</button>
    </form>
  </div>
  <div class="footer">구독 취소는 <a href="/unsubscribe">여기</a>에서</div>
</div></body></html>
"""

UNSUBSCRIBE_HTML = """
<!DOCTYPE html><html lang="ko"><head>{style}<title>구독 취소</title></head>
<body><div class="card">
  <div class="header">
    <h1>📭 구독 취소</h1>
    <p>이메일을 입력하시면 즉시 구독이 취소됩니다</p>
  </div>
  <div class="body">
    {msg}
    <form method="POST" action="/unsubscribe">
      <label>이메일</label>
      <input type="email" name="email" placeholder="example@gmail.com" required>
      <button class="btn" type="submit" style="background:#e53935;">구독 취소</button>
    </form>
  </div>
  <div class="footer"><a href="/">← 구독 페이지로</a></div>
</div></body></html>
"""


def _chips(selected=None):
    selected = selected or []
    html = ""
    for t in TOPIC_OPTIONS:
        checked = "checked" if t in selected else ""
        html += f'<span class="topic-chip"><input type="checkbox" name="topics" value="{t}" id="t_{t}" {checked}><label for="t_{t}">{t}</label></span>'
    return html


# ── 라우트 ────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(
        SUBSCRIBE_HTML.format(style=BASE_STYLE, msg="", chips=_chips())
    )


@app.route("/subscribe", methods=["POST"])
def subscribe():
    name   = request.form.get("name", "").strip()
    email  = request.form.get("email", "").strip()
    topics = request.form.getlist("topics")

    if not name or not email:
        msg = '<div class="msg err">이름과 이메일을 모두 입력해 주세요.</div>'
        return render_template_string(SUBSCRIBE_HTML.format(style=BASE_STYLE, msg=msg, chips=_chips(topics)))

    if not topics:
        msg = '<div class="msg err">관심 주제를 하나 이상 선택해 주세요.</div>'
        return render_template_string(SUBSCRIBE_HTML.format(style=BASE_STYLE, msg=msg, chips=_chips(topics)))

    add_subscriber(email, name, topics)
    msg = f'<div class="msg ok">✅ {name}님, 구독이 완료되었습니다!<br>매일 뉴스를 보내드릴게요 📬</div>'
    return render_template_string(SUBSCRIBE_HTML.format(style=BASE_STYLE, msg=msg, chips=_chips()))


@app.route("/unsubscribe", methods=["GET", "POST"])
def unsubscribe():
    msg = ""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        result = remove_subscriber(email)
        if "완료" in result:
            msg = f'<div class="msg ok">✅ 구독이 취소되었습니다.</div>'
        else:
            msg = f'<div class="msg err">❌ 등록된 이메일을 찾을 수 없습니다.</div>'
    return render_template_string(UNSUBSCRIBE_HTML.format(style=BASE_STYLE, msg=msg))
