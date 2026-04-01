from __future__ import annotations

import copy
import os
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any, Dict

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
UI_DIR = ROOT / "simulator_web" / "ui"
JOBS_DIR = ROOT / "simulator_web" / "_jobs"
GEN_DIR = ROOT / "simulator_web" / "_generated"

app = FastAPI(title="ADAPT Figure Generator")
app.mount("/ui", StaticFiles(directory=str(UI_DIR)), name="ui")


def load_yaml(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def save_yaml(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def deep_set(d: Dict[str, Any], dotted_key: str, value: Any) -> None:
    cur = d
    parts = dotted_key.split(".")
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value


def coerce_value(v: Any) -> Any:
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v
    if not isinstance(v, str):
        return v
    s = v.strip()
    if s.lower() in {"true", "false"}:
        return s.lower() == "true"
    try:
        if "." in s:
            return float(s)
        return int(s)
    except Exception:
        return s


def run_cmd(cmd: list[str], cwd: Path) -> str:
    env = os.environ.copy()
    src_path = str(ROOT / "src")
    env["PYTHONPATH"] = src_path + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed:\n{' '.join(cmd)}\n\n{proc.stdout}")
    return proc.stdout


def extract_run_dir(stdout: str) -> Path | None:
    patterns = [
        r"\[OK\] Baseline run complete: (.+)",
        r"\[OK\] Submission surge recovery run complete: (.+)",
        r"\[OK\] Quality drift run complete: (.+)",
        r"\[OK\] Figure 6 run complete: (.+)",
        r"\[OK\] Finished\. Outputs in: (.+)",
        r"\[OK\] Figure 8 run complete: (.+?)/metrics\.csv",
        r"\[OK\] Post-publication credit run complete: (.+)",
    ]
    for pat in patterns:
        m = re.search(pat, stdout)
        if m:
            p = m.group(1).strip()
            return (ROOT / p).resolve() if not Path(p).is_absolute() else Path(p).resolve()
    return None


FIGURES: Dict[str, Dict[str, Any]] = {
    "fig2_baseline": {
        "label": "Baseline stability",
        "config": ROOT / "configs" / "base.yaml",
        "overview": "Nominal operation with bounded backlog and stable policy.",
    },
    "fig3_submission_surge": {
        "label": "Submission surge recovery",
        "config": ROOT / "configs" / "submission_surge_recovery.yaml",
        "overview": "Backlog shock and bounded governance response under overload.",
    },
    "fig4_quality_drift": {
        "label": "Quality drift",
        "config": ROOT / "configs" / "quality_drift.yaml",
        "overview": "Declining input quality raises disagreement and triage selectivity.",
    },
    "fig5_disagreement_spike": {
        "label": "Disagreement spike",
        "config": ROOT / "configs" / "scenarios" / "disagreement_spike.yaml",
        "overview": "Higher reviewer noise produces an epistemic-stress spike in disagreement and escalation activity.",
    },
    "fig6_disagreement": {
        "label": "Disagreement-driven response",
        "config": ROOT / "configs" / "fig6_disagreement.yaml",
        "overview": "Spike in reviewer variance triggers bounded escalation-sensitive adaptation.",
    },
    "fig7_postpub_credit": {
        "label": "Post-publication credit dynamics",
        "config": ROOT / "configs" / "fig7_postpub_credit.yaml",
        "overview": "Author and reviewer credit evolve over delayed post-publication outcomes.",
    },
    "fig8_longterm": {
        "label": "Long-term governance adaptation",
        "config": ROOT / "configs" / "fig8_longterm.yaml",
        "overview": "Delayed post-publication signals produce slower structural policy drift.",
    },
    "collusion_enabled": {
        "label": "Collusion mitigation enabled",
        "config": ROOT / "configs" / "scenarios" / "collusion_attack.yaml",
        "overview": "Cluster capture is detected through concentration growth and then mitigated.",
    },
    "collusion_disabled": {
        "label": "Collusion mitigation disabled",
        "config": ROOT / "configs" / "scenarios" / "collusion_attack_no_mitigation.yaml",
        "overview": "Same attack path with mitigation disabled, leaving concentration elevated.",
    },
}

MODEL_OVERVIEW = {
    "agents": ["Authors", "Human reviewers", "AI reviewers", "Rotating editors"],
    "paper_variables": ["quality q_i", "complexity x_i", "keywords K_i"],
    "observed_signals": ["backlog B(t)", "mean disagreement D̄(t)", "reviewer load", "concentration κ(t)"],
    "policy_controls": ["triage threshold τ(t)", "AI reviewer fraction ρ_AI(t)", "escalation enablement"],
    "assumptions": [
        "arrivals: count process with Poisson/Binomial-style behavior",
        "review uncertainty: Gaussian-style noise around latent quality",
        "review effort: positive-skew workload proxy",
        "collusion detection: smoothed concentration metric",
        "post-publication impact: delayed noisy proxy signal",
    ],
}


class GenerateRequest(BaseModel):
    figure_id: str
    params: Dict[str, Any] = {}


@app.get("/")
def root() -> FileResponse:
    return FileResponse(UI_DIR / "index.html")


@app.get("/api/meta")
def meta() -> Dict[str, Any]:
    return {
        "figures": [{"id": k, "label": v["label"], "overview": v["overview"]} for k, v in FIGURES.items()],
        "model_overview": MODEL_OVERVIEW,
    }


@app.get("/api/image")
def image(path: str):
    p = (ROOT / path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
    if ROOT.resolve() not in p.parents and p != ROOT.resolve():
        raise HTTPException(status_code=400, detail="Invalid path")
    if not p.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(p)


@app.post("/api/generate")
def generate(req: GenerateRequest):
    if req.figure_id not in FIGURES:
        raise HTTPException(status_code=404, detail="Unknown figure")

    job_id = uuid.uuid4().hex[:10]
    job_dir = GEN_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    base_cfg = load_yaml(FIGURES[req.figure_id]["config"])
    cfg = copy.deepcopy(base_cfg)

    web_out_root = ROOT / "simulator_web" / "_generated" / job_id / "runs"
    cfg.setdefault("run", {})
    cfg["run"]["out_dir"] = str(web_out_root.as_posix())
    cfg["run"]["seed"] = int(coerce_value(req.params.get("run.seed", cfg["run"].get("seed", 123))))

    run_name_map = {
        "fig2_baseline": f"web_fig2_{job_id}",
        "fig3_submission_surge": f"web_fig3_{job_id}",
        "fig4_quality_drift": f"web_fig4_{job_id}",
        "fig5_disagreement_spike": f"web_fig5_{job_id}",
        "fig6_disagreement": f"web_fig6_{job_id}",
        "fig7_postpub_credit": f"web_fig7_{job_id}",
        "fig8_longterm": f"web_fig8_{job_id}",
        "collusion_enabled": f"web_collusion_on_{job_id}",
        "collusion_disabled": f"web_collusion_off_{job_id}",
    }
    cfg["run"]["run_name"] = run_name_map[req.figure_id]

    for k, v in req.params.items():
        if k == "run.seed":
            continue
        deep_set(cfg, k, coerce_value(v))

    cfg_path = JOBS_DIR / f"{job_id}_{req.figure_id}.yaml"
    save_yaml(cfg_path, cfg)

    python = sys.executable
    logs = []

    try:
        if req.figure_id == "fig2_baseline":
            out1 = run_cmd([python, "scripts/fig2_baseline_run.py", "--config", str(cfg_path)], ROOT)
            logs.append(out1)
            run_dir = extract_run_dir(out1)
            out2 = run_cmd([python, "scripts/make_fig2.py", "--run_dir", str(run_dir)], ROOT)
            logs.append(out2)
            src_img = ROOT / "paper_assets" / "figures" / "fig2_baseline_stability.png"
            final_img = job_dir / "fig2_baseline_stability.png"
            shutil.copy2(src_img, final_img)

        elif req.figure_id == "fig3_submission_surge":
            out1 = run_cmd([python, "scripts/fig3_submission_surge_run.py", "--config", str(cfg_path)], ROOT)
            logs.append(out1)
            run_dir = extract_run_dir(out1) or (web_out_root / cfg["run"]["run_name"])
            out2 = run_cmd([python, "scripts/make_fig3.py", "--run_dir", str(run_dir), "--out_dir", str(job_dir)], ROOT)
            logs.append(out2)
            final_img = job_dir / "fig3_submission_surge_recovery.png"

        elif req.figure_id == "fig4_quality_drift":
            out1 = run_cmd([python, "scripts/fig4_quality_drift_run.py", "--config", str(cfg_path)], ROOT)
            logs.append(out1)
            run_dir = extract_run_dir(out1) or (web_out_root / "quality_drift_run")
            out2 = run_cmd([python, "scripts/make_fig4_quality_drift.py", "--run_dir", str(run_dir), "--out_dir", str(job_dir)], ROOT)
            logs.append(out2)
            final_img = job_dir / "fig4_quality_drift.png"

        elif req.figure_id == "fig5_disagreement_spike":
            out1 = run_cmd([python, "-m", "adapt.sim.scenario_runner", "--config", str(cfg_path)], ROOT)
            logs.append(out1)
            run_dir = extract_run_dir(out1)
            out2 = run_cmd([python, "scripts/make_fig5_disagreement_spike.py", "--run_dir", str(run_dir), "--out_dir", str(job_dir)], ROOT)
            logs.append(out2)
            final_img = job_dir / "fig5_disagreement_spike.png"

        elif req.figure_id == "fig6_disagreement":
            out1 = run_cmd([python, "scripts/fig6_disagreement_run.py", "--config", str(cfg_path)], ROOT)
            logs.append(out1)
            run_dir = extract_run_dir(out1)
            out2 = run_cmd([python, "scripts/make_fig6.py", "--run_dir", str(run_dir), "--out_dir", str(job_dir)], ROOT)
            logs.append(out2)
            final_img = job_dir / "fig6_disagreement_response.png"

        elif req.figure_id == "fig7_postpub_credit":
            out1 = run_cmd([python, "scripts/fig7_postpub_credit_run.py", "--config", str(cfg_path)], ROOT)
            logs.append(out1)
            run_dir = extract_run_dir(out1)
            out2 = run_cmd([python, "scripts/make_fig7_postpub_credit.py", "--run_dir", str(run_dir), "--out_dir", str(job_dir)], ROOT)
            logs.append(out2)
            final_img = job_dir / "fig7_postpub_credit_dynamics.png"

        elif req.figure_id == "fig8_longterm":
            out1 = run_cmd([python, "scripts/fig8_longterm_run.py", "--config", str(cfg_path)], ROOT)
            logs.append(out1)
            run_dir = extract_run_dir(out1) or (web_out_root / "fig8_longterm")
            csv_path = run_dir / "metrics.csv"
            final_img = job_dir / "fig8_longterm_governance.png"
            out2 = run_cmd([python, "scripts/make_fig8.py", "--csv", str(csv_path), "--out", str(final_img)], ROOT)
            logs.append(out2)

        elif req.figure_id in {"collusion_enabled", "collusion_disabled"}:
            out1 = run_cmd([python, "-m", "adapt.sim.scenario_runner", "--config", str(cfg_path)], ROOT)
            logs.append(out1)
            run_dir = extract_run_dir(out1)
            final_img = job_dir / f"{req.figure_id}.png"
            out2 = run_cmd([python, "scripts/make_fig8_from_run.py", "--run_dir", str(run_dir), "--out", str(final_img)], ROOT)
            logs.append(out2)

        rel_img = final_img.resolve().relative_to(ROOT.resolve()).as_posix()
        return JSONResponse({
            "ok": True,
            "figure_id": req.figure_id,
            "figure_label": FIGURES[req.figure_id]["label"],
            "image_path": rel_img,
            "used_config": cfg,
            "log": "\n\n".join(logs),
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(e), "partial_log": "\n\n".join(logs)},
        )
