import json
import urllib.request
import os

TOKEN_FILE = os.path.join(os.path.dirname(__file__), ".inkray_token.json")
ARTICLE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "MEDIUM_ARTICLE_DRAFT.md")
PUBLICATION_ID = "0x12d875fc892cdfad0d2706a1c500a15d882f178d73547592117e53f060eebc1d"

with open(TOKEN_FILE, "r", encoding="utf-8") as f:
    token_data = json.load(f)
token = token_data["access_token"]

with open(ARTICLE_FILE, "r", encoding="utf-8") as f:
    full_text = f.read()

# Bỏ qua phần header metadata đầu file (# 📝 Medium / Inkray Article Draft ...)
body_lines = []
skip_header = True
for line in full_text.splitlines():
    if line.strip() == "---":
        skip_header = False
        continue
    if not skip_header:
        body_lines.append(line)

markdown_body = "\n".join(body_lines).strip()
title = "Chatbots That Remember: How We Built an Autonomous Social AI Agent Powered by Walrus Protocol"

def post_mcp(body, session_id=None):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'Authorization': f'Bearer {token}'
    }
    if session_id:
        headers['mcp-session-id'] = session_id
    req = urllib.request.Request('https://mcp.inkray.xyz/mcp', data=json.dumps(body).encode('utf-8'), headers=headers)
    with urllib.request.urlopen(req, timeout=30) as res:
        sid = res.headers.get('mcp-session-id')
        data = res.read().decode('utf-8')
        return sid, data

print("🚀 Khởi tạo phiên MCP với Inkray...")
sid, _ = post_mcp({
    'jsonrpc': '2.0',
    'id': 1,
    'method': 'initialize',
    'params': {
        'protocolVersion': '2024-11-05',
        'capabilities': {},
        'clientInfo': {'name': 'WalrusSocialAgent', 'version': '1.0.0'}
    }
})

print(f"📡 Đang tiến hành xuất bản bài viết lên Inkray (Publication: {PUBLICATION_ID})...")
publish_payload = {
    'jsonrpc': '2.0',
    'id': 2,
    'method': 'tools/call',
    'params': {
        'name': 'publish_article',
        'arguments': {
            'publicationId': PUBLICATION_ID,
            'title': title,
            'markdown': markdown_body
        }
    }
}

sid, pub_res = post_mcp(publish_payload, session_id=sid)
print("\n" + "=" * 70)
print("🎉 KẾT QUẢ XUẤT BẢN TỪ INKRAY MCP:")
print(pub_res)
print("=" * 70)
