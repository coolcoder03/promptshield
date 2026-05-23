from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

chaos_state: dict[str, bool] = {
    "llm_failure": False,
    "mcp_failure": False,
    "slow_response": False,
}

logs: list[dict[str, Any]] = []


def add_log(event: str, details: dict[str, Any] | None = None) -> None:
    logs.append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "details": details or {},
        }
    )

    # Keep logs small for demo readability.
    if len(logs) > 100:
        del logs[:-100]
