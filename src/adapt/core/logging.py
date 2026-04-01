from __future__ import annotations
import json
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Optional
from pathlib import Path
import datetime


def _jsonable(x: Any) -> Any:
    if is_dataclass(x):
        return asdict(x)
    if isinstance(x, Path):
        return str(x)
    return x


class EventLogger:
    def __init__(self, path_jsonl: Path):
        self.path = path_jsonl
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.f = self.path.open("w", encoding="utf-8")

    def log(self, event: Dict[str, Any]) -> None:
        event_out = {k: _jsonable(v) for k, v in event.items()}
        self.f.write(json.dumps(event_out) + "\n")

    def close(self) -> None:
        try:
            self.f.flush()
        finally:
            self.f.close()


def now_tag() -> str:
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
