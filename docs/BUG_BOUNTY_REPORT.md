# 🐛 Walrus Memory (MemWal) Comprehensive Bug Bounty Report

> **Target Upstream Repo:** `https://github.com/MystenLabs/MemWal`  
> **Submitter / Dev Wallet:** `0xfbf73b2f72858a4dbbcb4b942985bd46f410e7210fe01f8340f91946faec115f`  
> **Event:** Walrus Sessions 8 Hackathon — Bug Bounty Track ($100 × 5)  
> **Production Environment:** Windows 11 / Linux Ubuntu 22.04, Python 3.11, Node.js v20.18+, `@mysten-incubation/memwal-mcp` (v0.0.14)  
> **Target Relayer:** `https://relayer.memory.walrus.xyz` (Mainnet)  

---

## 📑 Executive Summary of Identified Bugs

| Bug ID | Subsystem | Severity | Title |
| :---: | :--- | :---: | :--- |
| **BUG-01** | Relayer SSE Stream | **CRITICAL** | Dangling SSE / Streamable HTTP sessions lock IP under HTTP 429 `ip_active_cap` |
| **BUG-02** | Relayer HTTP Headers | **MEDIUM** | Missing standard `Retry-After` header breaks client exponential backoff |
| **BUG-03** | SEAL Crypto Layer | **HIGH** | Race condition during concurrent `memwal_remember` throws `Internal Error: seal encrypt failed` |
| **BUG-04** | MCP Bridge Client | **CRITICAL** | Hardcoded 120-second orphan deadline (`call_orphaned`) freezes stdio callers |
| **BUG-05** | Python / Windows stdio | **HIGH** | Synchronous stdout `readline()` blocks indefinitely due to persistent Node socket |

---

## 🐛 BUG-01: Persistent HTTP 429 `ip_active_cap` Caused by Dangling Relayer Sessions

### 1. Title
`[Bug] Unreleased SSE/Streamable HTTP sessions on Relayer cause persistent HTTP 429 'ip_active_cap' locks across client restarts`

### 2. Description
When an MCP client process (Node.js or subprocess) connects to `https://relayer.memory.walrus.xyz` and subsequently terminates (e.g. unhandled crash, script completion, or SIGKILL/SIGINT), the relayer does not immediately invalidate or reap the SSE session. The relayer continues enforcing its per-IP concurrency ceiling (`ip_active_cap = 1`). Any subsequent client launched from that IP address is rejected with:
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32000,
    "message": "MCP rate limit: ip_active_cap. Close another MCP session, then retry."
  },
  "id": null
}
```
This lockout persists for 10–30+ minutes until the relayer's internal TCP keepalive timer expires.

### 3. Steps to Reproduce
1. Start an MCP session: `node @mysten-incubation/memwal-mcp/dist/bin/memwal-mcp.js --namespace test`
2. Abruptly kill the process: `taskkill /F /IM node.exe` (or `kill -9 <PID>`) without sending an MCP shutdown handshake.
3. Immediately launch a second session from the same IP:
   `node @mysten-incubation/memwal-mcp/dist/bin/memwal-mcp.js --namespace test`
4. **Observed Result:** Relayer rejects the handshake with HTTP 429 `ip_active_cap`.

### 4. Real Production Logs
```json
{"ts":"2026-09-23T13:50:32.125Z","level":"warn","scope":"memwal-mcp","event":"bridge.relayer_throttled","retryAfterMs":5000,"serverAdvised":false,"err":"Walrus Memory relayer SSE handshake rate-limited (HTTP 429). {\"jsonrpc\":\"2.0\",\"error\":{\"code\":-32000,\"message\":\"MCP rate limit: ip_active_cap. Close another MCP session, then retry.\"},\"id\":null}"}
{"ts":"2026-09-23T13:50:32.125Z","level":"error","scope":"memwal-mcp","event":"bridge.initial_connect_failed","err":"Walrus Memory relayer SSE handshake rate-limited (HTTP 429). {\"jsonrpc\":\"2.0\",\"error\":{\"code\":-32000,\"message\":\"MCP rate limit: ip_active_cap. Close another MCP session, then retry.\"},\"id\":null}","attempt":1}
```

### 5. Proposed Fix
- Implement an explicit session-closing endpoint: `DELETE /api/mcp/session/{sessionId}`.
- Shorten relayer-side idle TCP keepalive from several minutes to 15 seconds.

---

## 🐛 BUG-02: Relayer HTTP 429 Responses Omit Standard `Retry-After` Header

### 1. Title
`[Bug] Relayer HTTP 429 responses omit standard 'Retry-After' header, breaking exponential backoff in MCP clients`

### 2. Description
In `src/bridge.ts` of `@mysten-incubation/memwal-mcp`:
```typescript
function parseRetryAfterMs(raw: string | null): number | null {
    if (!raw) return null;
    // ...
}
```
When HTTP 429 occurs, `bridge.ts` inspects the HTTP headers for `retry-after`. Because the Relayer server does not supply this header, `serverAdvised` is always `false` and the client defaults to `DEFAULT_THROTTLE_FLOOR_MS = 5000`. If the relayer needs 60 seconds to release the session, clients hammer the relayer every 5 seconds, exacerbating server load.

### 3. Proposed Fix
Add standard HTTP response header `Retry-After: <seconds>` to all 429 responses from `relayer.memory.walrus.xyz`.

---

## 🐛 BUG-03: SEAL Symmetric Key Handshake Race Condition Under Concurrent Requests

### 1. Title
`[Bug] SEAL symmetric session key handshake fails with 'Internal Error: seal encrypt failed' during concurrent async memwal_remember jobs`

### 2. Description
When two or more `memwal_remember` calls are dispatched within < 500ms over the same delegate identity, the relayer hits a race condition during ephemeral SEAL key negotiation. Instead of queueing the cryptographic operation, it throws an unrecoverable 500 error:
```text
remember job failed: Internal Error: seal encrypt failed: seal/encrypt ...
```

### 3. Steps to Reproduce
1. Connect to MemWal MCP.
2. Send two consecutive `tools/call` requests with `memwal_remember` simultaneously without awaiting the first response.
3. The second call terminates with `seal encrypt failed`.

### 4. Proposed Fix
Add an asynchronous mutex lock or request queue on the Relayer's SEAL encryption handler per account/delegate to serialize encryption jobs.

---

## 🐛 BUG-04: Hardcoded 120-Second Orphan Deadline Freezes stdio Callers

### 1. Title
`[Bug] Hardcoded 120-second orphan deadline causes stdio clients to hang indefinitely on rate-limited calls`

### 2. Description
In `src/bridge.ts`:
```typescript
const TOOL_DEADLINE_MS = {
    memwal_recall: 90_000,
    memwal_remember: 90_000,
};
const ORPHAN_HEADROOM_MS = 30_000;
// Total wait = 90s + 30s = 120s
```
When a call is rejected by the relayer due to rate limiting or networking faults, the MCP bridge does not reject the tool call promise immediately. Instead, it holds the caller waiting for 120,474 ms until `bridge.call_orphaned` fires:
```json
{"ts":"2026-09-23T10:06:49.533Z","level":"warn","scope":"memwal-mcp","event":"bridge.call_orphaned","id":2,"method":"tools/call","elapsedMs":120474,"deadlineMs":120000,"reason":"no response","health":"ok","healthMs":321}
```

### 3. Proposed Fix
When a 429 error is detected, immediately return a JSON-RPC error response to the client (`code: -32000`) rather than waiting for the 120s timeout.

---

## 🐛 BUG-05: Windows Blocking I/O Deadlock on Child Process stdout `readline()`

### 1. Title
`[Bug] Synchronous stdout readline() hangs indefinitely on Windows when node stdio child process keeps socket alive`

### 2. Description
In Python wrappers on Windows, `proc.stdout.readline()` is blocking. Because Node.js keeps stdio open waiting for further JSON-RPC input while holding an active HTTPS socket, Python scripts hang indefinitely on `readline()`.
Even with `while time.time() < deadline:`, control never returns to Python to evaluate the condition. This caused automated background sync workers to remain stuck for 2+ hours.

### 3. Proposed Fix & Workaround
- **Workaround:** Implemented non-blocking threaded queue reader (`queue.Queue` + daemon thread) with strict timeout.
- **Upstream Feature Request:** Add `--single-shot` or `--exit-on-idle` flag to `memwal-mcp` so it terminates immediately after executing a single request if desired.

---

## 🌟 Feature Proposal: Native Python SDK (`memwal-py`)

A pure Python SDK eliminating Node.js stdio subprocesses would radically accelerate Web3 AI agent adoption. Python agents could interact with Walrus Memory natively:
```python
from memwal import WalrusMemoryClient

client = WalrusMemoryClient(credentials_path="~/.memwal/credentials.json")
await client.remember("User profile data...", namespace="my_agent")
results = await client.recall("Who is user @alice?", namespace="my_agent")
```
