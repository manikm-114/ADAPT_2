# ADAPT: AI-Driven Decentralized Adaptive Publishing Testbed

This repository contains the ADAPT simulation code, scenario configurations, figure-generation scripts, manuscript assets, and a local webpage for reproducing and perturbing key figures.

## Included project parts

- src/
  Core simulation code.

- configs/
  YAML configs for baseline, overload, disagreement, collusion, and long-term governance scenarios.

- scripts/
  Python scripts for running simulations and generating figures.

- simulator_web/
  Local webpage backend and frontend for selecting a figure, changing parameters, and regenerating outputs.

- paper_assets/
  Paper-ready figures and tables.

- paper/
  Supporting paper notes and assets, if present.

- top-level .tex files
  Main manuscript source files.

- references.bib
  Bibliography file, if present.

## Not intended for GitHub upload

The following are generated or temporary and should not be committed:

- outputs/
- simulator_web/_generated/
- simulator_web/_jobs/
- simulator_web/_runs/
- __pycache__/
- *.pyc
- *.bak
- scripts/Old/

## Requirements

Recommended:

- Python 3.10 or newer
- pip

Supported operating systems:

- Windows
- macOS
- Linux

## Install dependencies

Run these from the repository root.

### Windows

Using python:
python -m pip install -r requirements.txt

Using py:
py -m pip install -r requirements.txt

### macOS

Using python3:
python3 -m pip install -r requirements.txt

Using python:
python -m pip install -r requirements.txt

### Linux

Using python3:
python3 -m pip install -r requirements.txt

Using python:
python -m pip install -r requirements.txt

## Run the local webpage

Run these from the repository root.

### Windows

Using python:
python -m uvicorn simulator_web.server:app --reload --port 8008

Using py:
py -m uvicorn simulator_web.server:app --reload --port 8008

Then open:
http://127.0.0.1:8008

### macOS

Using python3:
python3 -m uvicorn simulator_web.server:app --reload --port 8008

Using python:
python -m uvicorn simulator_web.server:app --reload --port 8008

Then open:
http://127.0.0.1:8008

### Linux

Using python3:
python3 -m uvicorn simulator_web.server:app --reload --port 8008

Using python:
python -m uvicorn simulator_web.server:app --reload --port 8008

Then open:
http://127.0.0.1:8008

## How to use the webpage

1. Start the local server from the repository root.
2. Open http://127.0.0.1:8008
3. Select a figure or panel.
4. Change any exposed parameters.
5. Click Generate.
6. The webpage will run the corresponding simulation and plotting scripts.
7. The figure, resolved configuration, and run log will be shown in the browser.

## Direct command-line examples

Run these from the repository root.

### Baseline stability
python scripts/fig2_baseline_run.py --config configs/base.yaml
python scripts/make_fig2.py --run_dir outputs/runs/<your_run_dir>

### Submission surge recovery
python scripts/fig3_submission_surge_run.py --config configs/submission_surge_recovery.yaml
python scripts/make_fig3.py --run_dir outputs/runs/submission_surge_recovery --out_dir paper_assets/figures

### Quality drift
python scripts/fig4_quality_drift_run.py --config configs/quality_drift.yaml
python scripts/make_fig4_quality_drift.py --run_dir outputs/runs/quality_drift_run --out_dir paper_assets/figures

### Disagreement spike
python -m adapt.sim.scenario_runner --config configs/scenarios/disagreement_spike.yaml
python scripts/make_fig5_disagreement_spike.py --run_dir outputs/runs/<your_run_dir> --out_dir paper_assets/figures

### Disagreement-driven response
python scripts/fig6_disagreement_run.py --config configs/fig6_disagreement.yaml
python scripts/make_fig6.py --run_dir outputs/runs/<your_run_dir> --out_dir paper_assets/figures

### Post-publication credit dynamics
python scripts/fig7_postpub_credit_run.py --config configs/fig7_postpub_credit.yaml
python scripts/make_fig7_postpub_credit.py --run_dir outputs/runs/fig7_postpub_credit --out_dir paper_assets/figures

### Long-term governance adaptation
python scripts/fig8_longterm_run.py --config configs/fig8_longterm.yaml
python scripts/make_fig8.py --csv outputs/runs/fig8_longterm/metrics.csv --out figures/fig8_longterm_governance.png

### Collusion mitigation enabled
python -m adapt.sim.scenario_runner --config configs/scenarios/collusion_attack.yaml
python scripts/make_fig8_from_run.py --run_dir outputs/runs/<your_run_dir> --out figures/collusion_enabled.png

### Collusion mitigation disabled
python -m adapt.sim.scenario_runner --config configs/scenarios/collusion_attack_no_mitigation.yaml
python scripts/make_fig8_from_run.py --run_dir outputs/runs/<your_run_dir> --out figures/collusion_disabled.png

## Notes

- Generated outputs from the webpage are local and should not be committed.
- If uvicorn is missing, install dependencies again with the requirements file.
- On some systems, python may not point to the expected interpreter. In that case use python3 or py, depending on your platform.

## Suggested Git steps

After checking the contents of this folder:

git init
git add .
git commit -m "Initial clean ADAPT reproducibility repo"
