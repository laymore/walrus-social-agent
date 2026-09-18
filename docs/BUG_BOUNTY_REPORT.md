# 🐛 Walrus Memory (MemWal) Bug Report & Feature Request

**Target Repo:** `https://github.com/MystenLabs/MemWal`  
**Author / Submitter Wallet:** `0xfbf73b2f72858a4dbbcb4b942985bd46f410e7210fe01f8340f91946faec115f`  
**Environment:** 
- OS: Windows 11 / Linux Ubuntu 22.04
- Node.js: v20.12+ / Python 3.11.9
- Package: `@mysten-incubation/memwal-mcp` (v0.0.13) / `@mysten-incubation/memwal` (v0.0.1)
- Relayer: `https://relayer.memory.walrus.xyz` (Mainnet)
- Model: Google Gemini 1.5 Flash / DeepSeek-V3

---

## 1. Reproducible Bug: SEAL Encryption Race Condition during Rapid Async `memwal_remember`

### Summary
When multiple `memwal_remember` jobs are initiated concurrently or in quick succession through the MCP stdio interface, the relayer intermittently fails during the SEAL symmetric session key handshake, throwing an internal error:
```
remember job failed: Internal Error: seal encrypt failed: seal/encrypt ...
```

### Steps to Reproduce
1. Start `@mysten-incubation/memwal-mcp` connected to `https://relayer.memory.walrus.xyz`.
2. Send 2 to 3 `memwal_remember` tool call requests within < 500ms of each other.
3. Observe the response stream. One of the jobs will return a successful job ID, while subsequent jobs fail with `Internal Error: seal encrypt failed`.

### Expected Behavior
The relayer should either maintain a concurrent session pool for the delegate key or queue async encryption jobs with exponential backoff rather than terminating the job with an unrecoverable 500 internal error.

### Impact
In high-throughput agent environments (e.g. social media bots receiving dozens of comments per minute), this requires building complex application-level queueing to prevent dropping memories.

---

## 2. Improvement Proposal: Native Python SDK (`memwal-python`) or Direct Signed REST API

### The Problem
The majority of production AI agents, automation pipelines (Playwright/Selenium), and multi-agent frameworks (LangChain, CrewAI, AutoGen) are written in **Python**. Currently, integrating MemWal from Python requires running `@mysten-incubation/memwal-mcp` as a subprocess via stdio or spawning Node.js scripts. This introduces:
1. Subprocess management overhead and potential stream blocking.
2. Dependency on a full Node.js runtime alongside Python environments.

### Proposed Solution
1. **Official Python SDK (`memwal-py`):** Provide a lightweight Python package implementing Ed25519 request signing and SEAL session handling natively.
2. **Direct HTTP REST Specification:** Document the HTTP headers (`x-seal-session`, nonce generation, Ed25519 signature payload) so developers in any language (Python, Go, Rust) can directly invoke `https://relayer.memory.walrus.xyz/api/v1/remember` without requiring Node wrappers.
