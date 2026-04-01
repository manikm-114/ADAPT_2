import yaml
from pathlib import Path

KEYS = [
    ("review_process", "ai_fraction_target"),
    ("review_process", "ai_target"),
    ("reviewers", "n_ai"),
    ("reviewers", "n_humans"),
    ("governance", "ai_min"),
    ("governance", "ai_max"),
    ("governance", "ai_step"),
]

def get_nested(d, path):
    cur = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur

def main():
    root = Path("configs")
    yamls = sorted(root.rglob("*.yaml"))
    rows = []
    for p in yamls:
        cfg = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        row = {"file": str(p).replace("\\", "/")}
        for sect, key in KEYS:
            row[f"{sect}.{key}"] = get_nested(cfg, [sect, key])
        rows.append(row)

    # Print as aligned text
    cols = ["file"] + [f"{s}.{k}" for s,k in KEYS]
    widths = {c: max(len(c), max((len(str(r.get(c,""))) for r in rows), default=0)) for c in cols}

    header = " | ".join(c.ljust(widths[c]) for c in cols)
    print(header)
    print("-" * len(header))
    for r in rows:
        print(" | ".join(str(r.get(c,"")).ljust(widths[c]) for c in cols))

if __name__ == "__main__":
    main()
