"""Structured JSON-Lines request logging with PII-safe request text."""

import json
import time
import uuid
from pathlib import Path
from typing import Any

from guardrails import mask_pii


DEFAULT_LOG_PATH = Path(__file__).parent / "requests.jsonl"


def write_request_log(
    method: str,
    path: str,
    request_text: str,
    status_code: int,
    started_at: float,
    log_path: Path = DEFAULT_LOG_PATH,
) -> dict[str, Any]:
    """Append one structured request entry and return the entry."""
    entry = {
        "trace_id": str(uuid.uuid4()),
        "method": method,
        "path": path,
        "request_text": mask_pii(request_text),
        "status_code": status_code,
        "elapsed_ms": round((time.perf_counter() - started_at) * 1000, 3),
    }
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")
    return entry
