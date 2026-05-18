from __future__ import annotations

import hashlib
import json


def hash_cache_key(*args: str | None) -> str:
    raw = json.dumps(args, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()
