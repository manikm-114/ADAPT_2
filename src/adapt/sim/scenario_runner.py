from __future__ import annotations

import argparse
from typing import Any, Dict

import yaml

from adapt.sim.engine import run as run_engine


def load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    ap = argparse.ArgumentParser(description="Run an ADAPT simulation scenario from a YAML config.")
    ap.add_argument("--config", required=True, help="Path to scenario YAML config.")
    args = ap.parse_args()

    cfg: Dict[str, Any] = load_yaml(args.config) or {}
    cfg.setdefault("run", {})
    cfg["run"]["config"] = args.config  # provenance

    run_dir = run_engine(cfg)
    print(f"[OK] Finished. Outputs in: {run_dir}")


if __name__ == "__main__":
    main()
