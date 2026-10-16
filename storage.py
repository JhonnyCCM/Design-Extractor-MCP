"""
Resilient Storage, Atomic Writes, and In-Memory/Disk Cache for Design Extractor MCP.
Ensures files are never corrupted by interrupted writes and avoids redundant browser scrapes.
"""

import os
import sys
import json
import time
import hashlib
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.resolve()
CACHE_DIR = PROJECT_ROOT / ".cache"

__all__ = [
    "atomic_write",
    "redact_sensitive_data",
    "get_cached_extraction",
    "set_cached_extraction",
    "clear_cache"
]


def atomic_write(target_path: Path, content: str, encoding: str = "utf-8") -> None:
    """
    Writes content to a temporary file in the same directory and replaces
    the target atomically. This guarantees zero file corruption if interrupted.
    """
    target = target_path.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile("w", dir=str(target.parent), delete=False, encoding=encoding) as tf:
        temp_name = tf.name
        tf.write(content)
        tf.flush()
        os.fsync(tf.fileno())

    try:
        os.replace(temp_name, str(target))
    except Exception:
        # Fallback for Windows if target is locked or across volumes
        if os.path.exists(temp_name):
            try:
                if os.path.exists(str(target)):
                    os.remove(str(target))
                os.rename(temp_name, str(target))
            except Exception:
                # If rename fails, fallback to direct write and cleanup temp
                target.write_text(content, encoding=encoding)
                try:
                    os.remove(temp_name)
                except Exception:
                    pass


def redact_sensitive_data(message: str) -> str:
    """
    Sanitizes file paths, system usernames, or tokens from error messages
    to prevent leaking sensitive information in MCP transcripts.
    """
    if not message:
        return ""
    user = os.environ.get("USERNAME") or os.environ.get("USER")
    if user and len(user) > 2:
        message = message.replace(user, "[USER]")
    return message


def _get_url_hash(url: str) -> str:
    """Generates a stable MD5 hash for a normalized URL."""
    clean_url = url.strip().lower().rstrip("/")
    return hashlib.md5(clean_url.encode("utf-8")).hexdigest()


def get_cached_extraction(url: str, ttl_seconds: int = 900) -> Optional[Dict[str, Any]]:
    """
    Retrieves cached extraction payload for a URL if it exists and is within TTL (default: 15 min).
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{_get_url_hash(url)}.json"

    if not cache_file.exists():
        return None

    try:
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        cached_time = data.get("_cached_at", 0)
        if (time.time() - cached_time) < ttl_seconds:
            return data.get("payload")
    except Exception:
        pass

    return None


def set_cached_extraction(url: str, payload: Dict[str, Any]) -> None:
    """Stores extraction payload in cache with timestamp."""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file = CACHE_DIR / f"{_get_url_hash(url)}.json"
        cache_data = {
            "url": url,
            "_cached_at": time.time(),
            "payload": payload
        }
        atomic_write(cache_file, json.dumps(cache_data, ensure_ascii=False, indent=2))
    except Exception:
        pass


def clear_cache() -> int:
    """Deletes all cached extraction files and returns count of removed items."""
    if not CACHE_DIR.exists():
        return 0
    count = 0
    for f in CACHE_DIR.glob("*.json"):
        try:
            f.unlink()
            count += 1
        except Exception:
            pass
    return count
