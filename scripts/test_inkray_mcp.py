import json
import urllib.request

token_data = json.load(open('scripts/.inkray_token.json'))
token = token_data['access_token']

def post_mcp(body, session_id=None):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'Authorization': f'Bearer {token}'
    }
    if session_id:
        headers['mcp-session-id'] = session_id
    req = urllib.request.Request('https://mcp.inkray.xyz/mcp', data=json.dumps(body).encode('utf-8'), headers=headers)
    with urllib.request.urlopen(req, timeout=5) as res:
        sid = res.headers.get('mcp-session-id')
        data = res.read().decode('utf-8')
        return sid, data

try:
    sid, init_res = post_mcp({
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'initialize',
        'params': {
            'protocolVersion': '2024-11-05',
            'capabilities': {},
            'clientInfo': {'name': 'WalrusSocialAgent', 'version': '1.0.0'}
        }
    })
    print('Init session:', sid)
    print('Init res:', init_res)

    sid2, tools_res = post_mcp({
        'jsonrpc': '2.0',
        'id': 2,
        'method': 'tools/list',
        'params': {}
    }, session_id=sid)
    print('Tools res:', tools_res)

except Exception as e:
    print('Error:', e)
