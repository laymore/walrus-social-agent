"""
Interactive CLI Chatbot for Hackathon Judges & Evaluators.
Allows immediate testing of Walrus Protocol Long-Term Memory Recall
across sessions without requiring social media credentials.

Run with: python src/cli/interactive_demo.py
"""

import os
import sys
import time

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.agent.social_reply_agent import SocialReplyAgent
from src.memory.walrus_memory import WalrusMemoryClient


def print_banner():
    print("=" * 75)
    print(" 🔮 WALRUS SESSIONS 8: CHATBOTS THAT REMEMBER")
    print(" 🌟 Project: Walrus Social Media AI Agent (Huyen Minh Master)")
    print(" ⛓️ Network: Sui Mainnet | Storage: Walrus Protocol Mainnet")
    print(" 🆔 Account ID: 0xb893be50d278de78baf71d93cc047888a0440273bffe62050c70c24a5295c4e6")
    print(" 💼 Dev Wallet: 0xfbf73b2f72858a4dbbcb4b942985bd46f410e7210fe01f8340f91946faec115f")
    print("=" * 75)
    print("💡 INSTRUCTIONS FOR JUDGES:")
    print("1. Enter any username (e.g., 'quangnguyen0301' to test pre-existing on-chain memory,")
    print("   or create a new username to watch Walrus store and recall in real time).")
    print("2. Ask a question or share birth details (e.g., 'I was born in 1995, how is my luck?').")
    print("3. Then ask a follow-up (e.g., 'What about my love life?').")
    print("4. Notice how the agent REMEMBERS across sessions without asking again!")
    print("   Type 'exit' or 'quit' to end.\n")


def run_interactive_cli():
    print_banner()
    agent = SocialReplyAgent()

    author = input("👤 Enter User Handle (default: 'test_judge'): ").strip()
    if not author:
        author = "test_judge"

    print(f"\n✨ Session started for @{author}. Walrus Memory connected!\n")

    while True:
        try:
            user_input = input(f"[{author}] > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("\n👋 Thank you for evaluating Walrus Social Agent!")
                break

            print("\n⏳ [Agent Thinking] Querying Walrus Memory vector space...")
            start_time = time.time()
            result = agent.process_comment(author, user_input)
            elapsed = time.time() - start_time

            print("\n" + "-" * 60)
            if result.get("is_returning_user"):
                print("🎯 [WALRUS MEMORY RECALLED]")
                print(f"   Context: {result.get('memory_context')}")
            else:
                print("🆕 [NEW PROFILE CREATED & ASYNC PERSISTED TO WALRUS]")

            print(f"\n🤖 [Master Huyen Minh] ({elapsed:.2f}s):")
            print(f"   \"{result.get('response')}\"")
            print("-" * 60 + "\n")

        except (KeyboardInterrupt, EOFError):
            print("\n👋 Session ended.")
            break


if __name__ == "__main__":
    run_interactive_cli()
