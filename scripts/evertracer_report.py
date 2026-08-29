#!/usr/bin/env python3
"""Aggregate a completed EverTracer A run into JSON and Markdown."""
import argparse,json
from pathlib import Path
from evertracer_common import load_config,write_json
def load(path): return json.loads(Path(path).read_text())
def main():
 p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--run-dir",required=True);p.add_argument("--summary",required=True);p.add_argument("--report",required=True);a=p.parse_args();c=load_config(a.config);r=Path(a.run_dir)
 target=load(r/"metrics/target_train.json");reference=load(r/"metrics/reference_train.json");teacher=load(r/"metrics/teacher_verification.json");base=load(r/"metrics/base_verification.json");utility=load(r/"metrics/utility.json");sanity=load(r/"metrics/reload_sanity.json")
 gates={"member_oriented_auc":teacher["member_oriented_auc"]>=c["verification"]["auc_gate"],"member_oriented_tpr":teacher["member_oriented_tpr_at_fpr_limit"]>=c["verification"]["fsr_gate"],"above_base":teacher["member_oriented_auc"]>base["member_oriented_auc"] and teacher["member_oriented_tpr_at_fpr_limit"]>base["member_oriented_tpr_at_fpr_limit"],"utility":utility["delta"]["arc_challenge_acc_norm"]>=-0.05 and utility["delta"]["truthfulqa_mc2_acc"]>=-0.05,"ordinary_generation":sanity["passed"],"reload":sanity["fresh_process_reload"]}
 continuation=load(r/"continuation_metadata.json") if (r/"continuation_metadata.json").exists() else None
 summary={"project":"WMKD_Benchmark","method":"EverTracer","experiment":"A","root_run_id":continuation.get("root_run_id") if continuation else None,"cont1_run_id":continuation.get("parent_run_id") if continuation else None,"cont2_run_id":r.name,"official_source":c["official_source"],"model":c["model"],"dataset":load(Path(c["dataset"]["frozen_root"])/"manifest.json"),"continuation":continuation,"target_artifact_manifest":continuation.get("target_artifact_manifest") if continuation else None,"reference_artifact_manifest":continuation.get("reference_artifact_manifest") if continuation else None,"frozen_neighborhoods_sha256":continuation.get("frozen_neighborhoods_sha256") if continuation else None,"official_detector_definition":teacher["official_definition"],"member_oriented_equivalent_definition":teacher["member_oriented_definition"],"original_incorrect_metrics":{"teacher":teacher["provenance"]["original_incorrect_metrics"],"base":base["provenance"]["original_incorrect_metrics"]},"corrected_metrics":{"teacher":{k:v for k,v in teacher.items() if k not in ("scores",)},"base":{k:v for k,v in base.items() if k not in ("scores",)}},"target_training":target,"reference_training":reference,"utility":utility,"ordinary_generation":sanity,"gates":gates,"preferred_teacher":all(gates.values()),"ba_allowed":all(gates.values())};write_json(a.summary,summary)
 conclusion="EverTracer core reproduction successful on the WMKD_Benchmark canonical Llama-3.2-3B-Instruct backbone." if all(gates.values()) else "EverTracer Experiment A completed, but one or more predefined gates failed; no successful reproduction claim or Ba approval is made."
 continuation_note="The initial run completed target/reference training and merging, then failed when pinned T5 loading attempted online resolution without network access. Continuation 1 generated the canonical neighborhoods and completed teacher/base inference, then failed because ARC was not resolved from the offline cache. Audit found the calibrated score formula correct but the WMKD ROC positive class and threshold direction opposite to the fixed official implementation. Continuation 2 changed no scientific configuration, reused the same target/reference/neighborhoods and saved per-sample scores, corrected aggregation semantics without model inference, resolved pinned utility datasets locally, and completed the remaining evaluation." if continuation else "This run is not an evaluation continuation."
 md=f'''# EverTracer Experiment A Report

## Objective

Reproduce natural-language fingerprint injection and calibrated probability-variation verification on the canonical WMKD 3B backbone. Experiment Ba is out of scope.

## Provenance and environment

| Item | Value |
|---|---|
| Official repository | {c['official_source']['repository']} |
| Commit | `{c['official_source']['commit']}` |
| License | No license file at pinned commit; official code not vendored |
| Backbone | `{c['model']['id']}@{c['model']['revision']}` |
| Dataset | XSum; frozen Dtr=100, Dref=1000, Dunseen=100 |
| Precision | BF16 |

{continuation_note}

## Configuration and paper comparison

| Item | Paper/official | WMKD Experiment A |
|---|---|---|
| Backbone | Llama3-8B and other 7B/8B base models | Llama-3.2-3B-Instruct canonical revision |
| Dataset | XSum and AG News | XSum only |
| Target | LoRA, 20 epochs | LoRA r=8, 20 epochs, LR 1e-4, batch 4, packed 128 |
| Reference | Paper: 4 epochs; README example: 10 | 4 epochs, following paper |
| Verification | K=5 symmetric T5-Base pairs, 30% perturbation | Same core configuration; perturbations frozen for controls |
| Utility | Paper 16-task harmlessness suite | WMKD ARC + TruthfulQA MC2 + ordinary sanity |

## Training results

Target: {target['optimizer_steps']} steps, {target['elapsed_seconds']:.2f}s, peak VRAM {target['peak_vram_bytes']} bytes. Reference: {reference['optimizer_steps']} steps, {reference['elapsed_seconds']:.2f}s.

## Watermark verification

| Model | Official AUC (non-member positive) | Member-oriented AUC | Member TPR @ FPR≤5% | Member FPR | Member threshold |
|---|---:|---:|---:|---:|---:|
| EverTracer teacher | {teacher['official_auc_nonmember_positive']:.6f} | {teacher['member_oriented_auc']:.6f} | {teacher['member_oriented_tpr_at_fpr_limit']:.2%} | {teacher['member_oriented_fpr']:.2%} | {teacher['member_oriented_threshold']:.8g} |
| Canonical base | {base['official_auc_nonmember_positive']:.6f} | {base['member_oriented_auc']:.6f} | {base['member_oriented_tpr_at_fpr_limit']:.2%} | {base['member_oriented_fpr']:.2%} | {base['member_oriented_threshold']:.8g} |

The official-oriented metric uses `member=0`, `non-member=1`, and `C = suspect PV - reference PV`, so `C >= gamma` predicts non-member. The member-oriented benchmark metric uses `member=1` and `-C`; it is a mathematically equivalent reparameterization, not a new detector. The paper calls the member TPR at FPR ≤5% Fingerprint Success Rate (FSR); this report states its orientation explicitly.

## Utility and reload

ARC delta: {utility['delta']['arc_challenge_acc_norm']:.6f}. TruthfulQA MC2 delta: {utility['delta']['truthfulqa_mc2_acc']:.6f}. Ordinary-generation sanity: {sanity['passed']}. Fresh-process reload: {sanity['fresh_process_reload']}.

## Deviations, limitations, and bounded conclusion

This is a single XSum run on a 3B Instruct adaptation, not a full paper reproduction. BF16 and standardized utility are benchmark/runtime adaptations. It does not establish robustness to distillation or authorize Ba unless every gate passes.

**{conclusion}** Preferred teacher: **{all(gates.values())}**. Ba allowed: **{all(gates.values())}**.
''';Path(a.report).write_text(md,encoding="utf-8")
if __name__=="__main__":main()
