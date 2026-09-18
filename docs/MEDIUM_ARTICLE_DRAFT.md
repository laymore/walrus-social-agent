# 📝 Medium / Inkray Article Draft

**Title:** Chatbots That Remember: How We Built an Autonomous Social AI Agent Powered by Walrus Protocol  
**Subtitle:** A real-world production case study of migrating an amnesiac TikTok AI counselor to decentralized, SEAL-encrypted long-term memory on Sui & Walrus Mainnet.  
**Tags:** #WalrusMemory #Sui #AIAgents #Web3 #DecentralizedStorage #MachineLearning  

---

## The Amnesiac Agent Dilemma

If you have ever built an AI chatbot for customer support, gaming, or social media, you know the heartbreak of the **"amnesiac agent."**

The moment a session closes or the conversation moves to another thread, the agent suffers total cognitive wipeout. On social platforms like TikTok or Instagram, this problem is catastrophic.

Consider our project: **Master Huyen Minh (`@aihuyenminh`)**, an autonomous AI counselor providing daily guidance on Eastern metaphysics (BaZi, Zi Wei Dou Shu) and psychological mindfulness to thousands of viewers. Metaphysics is deeply personal. A user might comment on a morning video:

> *"Master, I was born on August 15, 1995 (Wood Pig / Ất Hợi). My career has been extremely stressful lately. Any advice?"*

Our agent delivers an empathetic, accurate reading based on their birth chart. Two days later, that same user watches an evening video about relationships and comments:

> *"What about my marriage luck this year?"*

In the traditional world, what does the bot say?

> *"Hello! To read your chart, please tell me your birth date and birth hour!"*

The illusion vanishes. The user is frustrated. The connection is severed.

Why? Because traditional chatbots are **stateless prompt wrappers**. Storing sensitive user data in centralized databases creates privacy nightmares, vendor lock-in, and cross-platform fragmentation.

Enter **Walrus Protocol** and **Walrus Memory (MemWal)**.

---

## Why Walrus Memory?

When Mysten Labs introduced Walrus Memory, we realized it offered three fundamental properties unavailable in centralized memory stores:

1. **Decentralized Permanence:** Memories are stored as blobs across the Walrus decentralized network, remaining available across servers, devices, and platforms.
2. **SEAL Encryption & User Ownership:** Memories are cryptographically encrypted using the SEAL framework. The agent accesses them under strict programmable permissions anchored on Sui smart contracts.
3. **Semantic Recall via Vector Spaces:** You don't query memories with brittle exact-match SQL keys; you recall them by **meaning** (cosine distance across high-dimensional embeddings).

---

## The Architecture: Walrus-First Social CRM

Here is how we architected the system:

```
[TikTok Viewer Comment]
         │
         ▼
[Autonomous Playwright Crawler]
         │
         ▼
[Memory Manager (Python)] ───► [Walrus Memory MCP] ───► [Walrus Relayer (Mainnet)]
         │                                                        │
         │  (Semantic Recall via Vector Embedding)                │
         ◄────────────────────────────────────────────────────────┘
         │
         ▼
[Augmented Context Prompt]
         │
         ▼
[Alternative LLM: Google Gemini 1.5 Flash / DeepSeek-V3]
         │
         ▼
[Empathetic, Memory-Aware Reply Published to TikTok]
         │
         ▼
[Async Worker: Serialize New Interaction & Persist to Walrus Blob]
```

### The Setup

We set up our official account on Sui Mainnet:
- **Account ID:** `0xb893be50d278de78baf71d93cc047888a0440273bffe62050c70c24a5295c4e6`
- **Wallet Address:** `0xfbf73b2f72858a4dbbcb4b942985bd46f410e7210fe01f8340f91946faec115f`
- **Relayer:** `https://relayer.memory.walrus.xyz`
- **Namespace:** `huyenminh_social_crm`

To connect our Python social crawler to the `@mysten-incubation/memwal-mcp` service, we developed a clean stdio bridge that speaks JSON-RPC 2.0 directly to the relayer.

Each customer profile is serialized into a high-density semantic fact:
```text
[SOCIAL_CRM_PROFILE] User: @quangnguyen0301. Interactions: 2 sessions. Born: 1995 (Ất Hợi - Sơn Đầu Hỏa). Focus: CAREER_AND_WEALTH. Latest: "Cho e cái link truy cập với nào" -> "nè". LastActive: 2026-09-16 10:38:00.
```

---

## Before vs. After: The Transformation

On **September 16, 2026** (two days before Walrus Sessions 8 officially launched), we deployed Walrus Memory to our live production pipeline.

### Case #1: User `@quangnguyen0301`
- **Before:** Repeatedly asked for birth details across multiple video uploads.
- **After:** When the user returned on September 16, the agent executed `memwal_recall` on their username:
  ```json
  {
    "score": 0.548,
    "distance": 0.452,
    "text": "Khách hàng @quangnguyen0301 sinh năm 1995 (Ất Hợi - Sơn Đầu Hỏa), quan tâm đến tài lộc..."
  }
  ```
  The agent seamlessly replied with full recognition of their astrological chart, without a single repeated question!
  - **Verified On-Chain Blob:** [`PEzXmHsOMC9vyL79Z5y245i80SJETg2x22T6wFZYMRE`](https://walruscan.com/mainnet/blob/PEzXmHsOMC9vyL79Z5y245i80SJETg2x22T6wFZYMRE)

### Case #2: User `@nhamnhamnhoainhoai`
- On September 18, 2026, user `@nhamnhamnhoainhoai` left prayer emojis on our daily incense video. The agent recalled their previous interaction from 48 hours prior and delivered a personalized blessing acknowledging their spiritual consistency.
  - **Verified On-Chain Blob:** [`tr3FEEz0iIBRg5OpuFzwmB1V2I9knil8ihgo1IZon1Y`](https://walruscan.com/mainnet/blob/tr3FEEz0iIBRg5OpuFzwmB1V2I9knil8ihgo1IZon1Y)

---

## Real-World Lessons & Friction Points

Building on cutting-edge Web3 infrastructure is exhilarating, but real-world testing uncovered valuable lessons:

1. **The Need for a Native Python SDK:** Most AI agent frameworks (LangChain, CrewAI, Playwright automation) run in Python. Bridging through Node.js MCP stdio works, but an official `pip install memwal` package would unlock immense adoption across the broader AI ecosystem.
2. **SEAL Encryption Race Conditions:** Under rapid burst traffic, simultaneous async `memwal_remember` calls can occasionally trigger session key handshake timeouts (`Internal Error: seal encrypt failed`). We mitigated this by introducing an asynchronous queue and local fallback cache.

---

## Conclusion: The Era of Persistent Agents

Walrus Memory is not just another vector database; it represents a paradigm shift toward **user-owned, portable artificial intelligence**.

Our agent no longer forgets. It remembers who you are, what you care about, and where your journey started — not because it is stored on a Silicon Valley server, but because it is cryptographically preserved on decentralized Walrus blobs.

The code is fully open source. Clone it, run the CLI demo, and experience the future of AI memory for yourself:

👉 **GitHub Repository:** `https://github.com/laymore/walrus-social-agent`  
👉 **Walruscan Explorer:** [Inspect our Mainnet Blobs](https://walruscan.com/mainnet/blob/PEzXmHsOMC9vyL79Z5y245i80SJETg2x22T6wFZYMRE)
