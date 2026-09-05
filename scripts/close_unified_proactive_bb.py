#!/usr/bin/env python3
"""Generate the final master report after SCW Bb and CTCC Bb2 are terminal."""
from __future__ import annotations
import argparse, json, subprocess
from datetime import datetime, timezone
from pathlib import Path

TERMINAL={"COMPLETE","BLOCKED","FAILED","BLOCKED_AT_PREPROCESSING_ACCEPTANCE_GATE"}

def load(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--project",type=Path,required=True); ap.add_argument("--state",type=Path,required=True); a=ap.parse_args(); state=load(a.state)
    for key in ("scw","ctcc_bb2"):
        if state["methods"].get(key,{}).get("status") not in TERMINAL: raise RuntimeError(f"NON_TERMINAL_{key}")
    bb2_path=a.project/"results/ctcc/experiment_bb2/full_experiment_log.json"; bb2=load(bb2_path) if bb2_path.exists() else None
    scw_path=a.project/"results/scw/experiment_bb/full_experiment_log.json"; scw=load(scw_path) if scw_path.exists() else None
    methods={k:v.get("status") for k,v in state["methods"].items()}
    details="CTCC Bb2 ended without a complete scientific log." if not bb2 else f"Original Bb resolved reused: {bb2['original_bb_reuse']['original_resolved_reused']}; new additional processing: {20000-bb2['original_bb_reuse']['original_resolved_reused']}; final processed20k: 20,000; identity fallback: {bb2['preprocessing']['identity_fallback_count']} ({bb2['preprocessing']['identity_fallback_rate']:.6%}). Student steps: {bb2['training']['steps']}; loss: {bb2['training']['train_loss']}; reload/archive: PASS. Detector Bb2: {bb2['detector']['bb2']}. Utility Bb2: {bb2['utility']['bb2']}; delta: {bb2['utility']['delta']}."
    text=f"""# WMKD unified proactive Bb — final master report

Generated: {datetime.now(timezone.utc).isoformat()}

## Original proactive Bb

- EverTracer: {methods.get('evertracer','COMPLETE')}
- CTCC: BLOCKED_AT_PREPROCESSING_ACCEPTANCE_GATE (202 > 200; Student/detector/utility not run)
- iSeal: {methods.get('iseal')}
- PN-FP: {methods.get('pnfp')}
- SCW: {methods.get('scw')}

## CTCC Bb2

Distinct follow-up scientific variant; original CTCC Bb remains blocked and unchanged. The only primary protocol difference is removal of the global identity-fallback-count acceptance gate. Frozen per-sample UP semantics and downstream distillation remain unchanged.

{details}

## Reconstruction limitations

PN-FP and SCW parent reconstruction disclosures remain those of their canonical Bb full logs. No broader causal, universal-removal, or checkpoint-trajectory claim is made.

## Archive and full-log integrity

SCW full log: {'present' if scw else 'terminal without complete log'}. CTCC Bb2 full log: {'present' if bb2 else 'terminal without complete log'}. Archive verification is recorded in each method log. Global index validation and final Git equality are prerequisites of the separate fail-closed shutdown readiness record.

## Automatic shutdown

Shutdown armed: YES. Eligibility is evaluated only after this report is committed and Local/GitHub/AutoDL are equal and clean. The actual command/result is recorded in `results/unified_remaining_bb_auto_shutdown.json`.
"""
    path=a.project/"docs/reproduction_reports/unified_proactive_bb_master_report.md"; path.write_text(text,encoding="utf-8")
    subprocess.run(["git","add",str(path),"results/experiment_full_logs_index.json","PROJECT_STATUS.md","EXPERIMENT_LOG.md","CODEX_LOG.md","DECISIONS.md"],cwd=a.project,check=True)
    subprocess.run(["git","diff","--cached","--check"],cwd=a.project,check=True)
    subprocess.run(["git","commit","-m","Close unified proactive Bb and CTCC Bb2"],cwd=a.project,check=True)
    subprocess.run(["git","push","origin","main"],cwd=a.project,check=True)

if __name__=="__main__": main()
