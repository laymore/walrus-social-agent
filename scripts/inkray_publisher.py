"""
Inkray Decentralized Article Publisher via OAuth 2.1 & MCP
Dành riêng cho dự án Walrus Social Agent - Walrus Sessions 8
"""
import os
import sys
import json
import time
import secrets
import hashlib
import base64
import urllib.request
import urllib.parse
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass

AUTH_SERVER = "https://mcp.inkray.xyz"
MCP_ENDPOINT = "https://mcp.inkray.xyz/mcp"
REDIRECT_URI = "http://localhost:8080/callback"
TOKEN_FILE = os.path.join(os.path.dirname(__file__), ".inkray_token.json")
ARTICLE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "MEDIUM_ARTICLE_DRAFT.md")

def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def generate_pkce():
    verifier = base64url_encode(secrets.token_bytes(32))
    digest = hashlib.sha256(verifier.encode('utf-8')).digest()
    challenge = base64url_encode(digest)
    return verifier, challenge

def register_client():
    data = json.dumps({
        "client_name": "Walrus Social Agent",
        "redirect_uris": [REDIRECT_URI],
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
        "scope": "inkray:read inkray:account inkray:drafts inkray:publish",
        "token_endpoint_auth_method": "none"
    }).encode("utf-8")
    
    req = urllib.request.Request(
        f"{AUTH_SERVER}/oauth/register",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as res:
        return json.loads(res.read().decode("utf-8"))

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    auth_code = None
    auth_state = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/callback":
            params = urllib.parse.parse_qs(parsed.query)
            OAuthCallbackHandler.auth_code = params.get("code", [None])[0]
            OAuthCallbackHandler.auth_state = params.get("state", [None])[0]

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = """
            <html>
            <body style="font-family: system-ui, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 90vh; background: #0d1117; color: #c9d1d9;">
                <div style="background: #161b22; padding: 40px; border-radius: 12px; border: 1px solid #30363d; text-align: center; max-width: 480px;">
                    <h1 style="color: #2ea043; margin-bottom: 12px;">✅ Ký Xác Thực Thành Công!</h1>
                    <p style="font-size: 16px; line-height: 1.5;">Inkray đã cấp quyền cho <b>Walrus Social Agent</b>.</p>
                    <p style="font-size: 14px; color: #8b949e;">Bạn có thể đóng tab này và quay lại màn hình làm việc. Tiến trình đang xuất bản bài viết lên Inkray...</p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

def obtain_access_token():
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                token_data = json.load(f)
            # Kiểm tra sơ bộ token còn hạn không
            if token_data.get("access_token"):
                print("🔑 Đã tìm thấy Access Token Inkray đã lưu.")
                return token_data["access_token"]
        except Exception:
            pass

    print("🚀 Khởi tạo phiên kết nối OAuth 2.1 với Inkray MCP Server...")
    client_reg = register_client()
    client_id = client_reg["client_id"]
    print(f"✅ Đăng ký Client thành công: {client_id}")

    verifier, challenge = generate_pkce()
    state = secrets.token_hex(16)

    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "inkray:read inkray:account inkray:drafts inkray:publish",
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": state
    }
    auth_url = f"{AUTH_SERVER}/oauth/authorize?{urllib.parse.urlencode(params)}"
    with open(os.path.join(os.path.dirname(__file__), "auth_url.txt"), "w", encoding="utf-8") as f:
        f.write(auth_url)

    print("\n" + "=" * 70, flush=True)
    print("🌐 VUI LÒNG MỞ TRÌNH DUYỆT ĐỂ KẾT NỐI VÍ SUI & KÝ XÁC THỰC (0 GAS)", flush=True)
    print(f"👉 Link cấp quyền: {auth_url}", flush=True)
    print("=" * 70 + "\n", flush=True)

    # Mở trình duyệt mặc định
    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    server = HTTPServer(("localhost", 8080), OAuthCallbackHandler)
    server.timeout = 180  # Chờ tối đa 3 phút

    print("⏳ Đang lắng nghe phản hồi xác thực tại http://localhost:8080/callback ...")
    while not OAuthCallbackHandler.auth_code:
        server.handle_request()

    if not OAuthCallbackHandler.auth_code:
        raise Exception("Không nhận được authorization code từ Inkray.")

    print("✅ Đã nhận Authorization Code. Đang đổi mã lấy Access Token...")
    token_payload = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "client_id": client_id,
        "code": OAuthCallbackHandler.auth_code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": verifier
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{AUTH_SERVER}/oauth/token",
        data=token_payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    with urllib.request.urlopen(req, timeout=10) as res:
        token_res = json.loads(res.read().decode("utf-8"))

    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(token_res, f, indent=2)

    print("🎉 KẾT NỐI VÍ THÀNH CÔNG! Đã lưu Token vào .inkray_token.json")
    return token_res["access_token"]

def call_mcp_tool(access_token, tool_name, arguments):
    req_body = json.dumps({
        "jsonrpc": "2.0",
        "id": int(time.time()),
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        MCP_ENDPOINT,
        data=req_body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.loads(res.read().decode("utf-8"))

def list_mcp_tools(access_token):
    req_body = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }).encode("utf-8")

    req = urllib.request.Request(
        MCP_ENDPOINT,
        data=req_body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
    )
    with urllib.request.urlopen(req, timeout=10) as res:
        return json.loads(res.read().decode("utf-8"))

def main():
    print("=" * 70)
    print("📝 INKRAY PUBLISHER — WALRUS SESSIONS 8 HACKATHON")
    print("=" * 70)

    token = obtain_access_token()

    print("\n🔍 Đang truy vấn danh sách công cụ (Tools) từ Inkray MCP...")
    tools_res = list_mcp_tools(token)
    tools = tools_res.get("result", {}).get("tools", [])
    print(f"👉 Tìm thấy {len(tools)} công cụ hỗ trợ:")
    for t in tools:
        print(f"   • {t['name']}: {t.get('description', '')[:80]}...")

    # Đọc nội dung bài viết
    if not os.path.exists(ARTICLE_FILE):
        print(f"❌ Không tìm thấy tệp bài viết: {ARTICLE_FILE}")
        return

    with open(ARTICLE_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    title = "Chatbots That Remember: How We Built an Autonomous Social AI Agent Powered by Walrus Protocol"
    subtitle = "A real-world production case study of migrating an amnesiac TikTok AI counselor to decentralized, SEAL-encrypted long-term memory on Sui & Walrus Mainnet."
    tags = ["WalrusMemory", "Sui", "AIAgents", "Web3", "DecentralizedStorage"]

    # Kiểm tra tên tool phù hợp trong tools
    publish_tool = None
    for t in tools:
        name = t["name"].lower()
        if "publish" in name or "article" in name or "draft" in name or "post" in name:
            publish_tool = t
            break

    print(f"\n🚀 Sẵn sàng xuất bản bài viết với công cụ: {publish_tool['name'] if publish_tool else 'Chưa xác định'}")

if __name__ == "__main__":
    main()
