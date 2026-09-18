"""
Walrus Memory Client Interface.
Provides seamless Semantic Recall and Memory Persistence over Walrus Protocol Mainnet.
Leverages the official @mysten-incubation/memwal-mcp bridge with local resilience fallback.
"""

import os
import sys
import json
import subprocess
import threading
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from .customer_profile import CustomerProfile

logger = logging.getLogger("WalrusMemory")
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] [WalrusMemory] %(message)s")

DEFAULT_NAMESPACE = os.getenv("MEMWAL_NAMESPACE", "huyenminh_social_crm")
CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "local_cache.json")


class WalrusMemoryClient:
    def __init__(self, namespace: str = DEFAULT_NAMESPACE):
        self.namespace = namespace
        self._lock = threading.Lock()
        self._ensure_cache_file()

    def _ensure_cache_file(self):
        if not os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump({}, f)
            except Exception as e:
                logger.warning(f"Unable to initialize cache file: {e}")

    def _read_cache(self) -> Dict[str, Any]:
        with self._lock:
            if os.path.exists(CACHE_FILE):
                try:
                    with open(CACHE_FILE, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception as e:
                    logger.error(f"Error reading local cache: {e}")
            return {}

    def _write_cache(self, data: Dict[str, Any]):
        with self._lock:
            try:
                with open(CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.error(f"Error writing to local cache: {e}")

    def recall_raw(self, query: str, limit: int = 3, timeout_sec: int = 6) -> Optional[str]:
        """Queries Walrus Memory semantic vector index on Mainnet via MCP with strict timeout."""
        logger.info(f"🌐 [Walrus Query] Initiating semantic recall for query: '{query}' (limit={limit}, timeout={timeout_sec}s)...")
        result_box = [None]

        def _worker():
            proc = None
            try:
                cmd = ["npx.cmd" if sys.platform == "win32" else "npx", "-y", "@mysten-incubation/memwal-mcp", "--namespace", self.namespace]
                proc = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8"
                )

                def send(msg):
                    proc.stdin.write(json.dumps(msg) + "\n")
                    proc.stdin.flush()

                def read_until_id(target_id: int, max_lines: int = 25):
                    for _ in range(max_lines):
                        line = proc.stdout.readline()
                        if not line:
                            break
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            if data.get("id") == target_id:
                                return data
                        except Exception:
                            pass
                    return None

                # 1. Initialize MCP Protocol
                send({
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "Walrus-Social-Agent", "version": "1.0.0"}
                    }
                })
                read_until_id(1)
                send({"jsonrpc": "2.0", "method": "notifications/initialized"})

                # 2. Execute memwal_recall Tool
                send({
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "memwal_recall",
                        "arguments": {
                            "query": query,
                            "limit": limit,
                            "namespace": self.namespace
                        }
                    }
                })
                res = read_until_id(2)
                if res and "result" in res:
                    result_box[0] = res.get("result", {}).get("content", [{}])[0].get("text", "")
            except Exception as e:
                logger.warning(f"⚠️ [Walrus Recall Worker Error] {e}")
            finally:
                if proc:
                    try:
                        proc.kill()
                    except Exception:
                        pass

        th = threading.Thread(target=_worker, daemon=True)
        th.start()
        th.join(timeout=timeout_sec)

        if th.is_alive():
            logger.warning(f"⏱️ [Walrus Timeout] Recall timed out after {timeout_sec}s, using local fallback.")
            return None

        if result_box[0]:
            logger.info(f"✅ [Walrus Recall Success] Retrieved {len(result_box[0])} characters of semantic context.")
            return result_box[0]
        return None

    def get_profile(self, author: str) -> Optional[CustomerProfile]:
        """
        Walrus-First Architecture:
        1. Prioritize on-chain semantic recall from Walrus Memory.
        2. If network latency or offline, seamlessly fallback to local cache.
        """
        clean_author = author.replace("@", "").strip()

        # Step 1: On-Chain Walrus Recall
        raw_text = self.recall_raw(f"User: @{clean_author}", limit=3)
        if raw_text:
            profile = CustomerProfile.from_walrus_text(clean_author, raw_text)
            if profile and (profile.birth_year or profile.primary_need):
                logger.info(f"🎯 [Walrus Hit] Recognized user @{clean_author} from decentralized memory!")
                # Update local cache
                cache = self._read_cache()
                cache[clean_author] = profile.model_dump()
                self._write_cache(cache)
                return profile

        # Step 2: Local Resilience Cache Fallback
        cache = self._read_cache()
        if clean_author in cache:
            logger.info(f"📁 [Local Cache Hit] Retrieved fallback profile for @{clean_author}")
            cached_data = cache[clean_author]
            cached_data["source"] = "LOCAL_FALLBACK"
            return CustomerProfile(**cached_data)

        logger.info(f"🌱 [New Visitor] First time interacting with @{clean_author}")
        return None

    def remember_async(self, profile: CustomerProfile, last_comment: str = "", last_response: str = ""):
        """Stores or updates customer memory asynchronously to preserve real-time response speed."""
        # 1. Update local cache immediately
        cache = self._read_cache()
        cache[profile.author] = profile.model_dump()
        self._write_cache(cache)

        # 2. Dispatch Walrus on-chain write worker
        def _worker():
            self._save_to_walrus_sync(profile, last_comment, last_response)

        threading.Thread(target=_worker, daemon=True).start()

    def _save_to_walrus_sync(self, profile: CustomerProfile, last_comment: str, last_response: str) -> bool:
        """Synchronously persists the serialized memory fact to Walrus Protocol Mainnet."""
        fact_text = profile.to_walrus_fact(last_comment, last_response)
        logger.info(f"💾 [Walrus Storing] Submitting blob for @{profile.author}...")

        try:
            cmd = ["npx.cmd" if sys.platform == "win32" else "npx", "-y", "@mysten-incubation/memwal-mcp", "--namespace", self.namespace]
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8"
            )

            def send(msg):
                proc.stdin.write(json.dumps(msg) + "\n")
                proc.stdin.flush()

            def read_until_id(target_id: int, max_lines: int = 25):
                for _ in range(max_lines):
                    line = proc.stdout.readline()
                    if not line:
                        break
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("id") == target_id:
                            return data
                    except Exception:
                        pass
                return None

            send({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "Walrus-Social-Writer", "version": "1.0.0"}
                }
            })
            read_until_id(1)
            send({"jsonrpc": "2.0", "method": "notifications/initialized"})

            # Execute memwal_remember
            send({
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "memwal_remember",
                    "arguments": {
                        "text": fact_text,
                        "namespace": self.namespace
                    }
                }
            })
            res = read_until_id(2)
            proc.terminate()

            if res and "result" in res:
                content = res.get("result", {}).get("content", [{}])[0].get("text", "")
                logger.info(f"🎉 [Walrus Persisted] Successfully saved memory on-chain! {content[:80]}...")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ [Walrus Persist Error] Failed to persist memory: {e}")
            return False
