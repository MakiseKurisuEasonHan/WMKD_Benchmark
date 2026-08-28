#!/usr/bin/env python3
"""Aggregate a completed EverTracer A run into JSON and Markdown."""
import argparse,json
from pathlib import Path
from evertracer_common import load_config,write_json
def load(path): return json.loads(Path(path).read_text())
def main():
 p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--run-dir",required=True);p.add_argument("--summary",required=True);p.add_argument("--report",required=True);a=p.parse_args();c=load_config(a.config);r=Path(a.run_dir)
 target=load(r/"metrics/target_train.json");reference=load(r/"metrics/reference_train.json");teacher=load(r/"metrics/teacher_verification.json");base=load(r/"metrics/base_verification.json");utility=load(r/"metrics/utility.json");sanity=load(r/"metrics/reload_sanity.json")
 gates={"auc":teacher["auc"]>=c["verification"]["auc_gate"],"fsr":teacher["fsr"]>=c["verification"]["fsr_gate"],"above_base":teacher["auc"]>base["auc"] and teacher["fsr"]>base["fsr"],"utility":utility["delta"]["arc_challenge_acc_norm"]>=-0.05 and utility["delta"]["truthfulqa_mc2_acc"]>=-0.05,"ordinary_generation":sanity["passed"],"reload":sanity["fresh_process_reload"]}
 summary={"project":"WMKD_Benchmark","method":"EverTracer","experiment":"A","official_source":c["official_source"],"model":c["model"],"dataset":load(Path(c["dataset"]["frozen_root"])/"manifest.json"),"target_training":target,"reference_training":reference,"teacher_verification":teacher,"base_verification":base,"utility":utility,"ordinary_generation":sanity,"gates":gates,"preferred_teacher":all(gates.values()),"ba_allowed":all(gates.values())};write_json(a.summary,summary)
 conclusion="EverTracer core reproduction successful on the WMKD_Benchmark canonical Llama-3.2-3B-Instruct backbone." if all(gates.values()) else "EverTracer Experiment A completed, but one or more predefined gates failed; no successful reproduction claim or Ba approval is made."
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

| Model | AUC | FSR | FPR | Threshold | Pos/Neg |
|---|---:|---:|---:|---:|---:|
| EverTracer teacher | {teacher['auc']:.6f} | {teacher['fsr']:.2%} | {teacher['fpr']:.2%} | {teacher['threshold']:.8g} | {teacher['positive_count']}/{teacher['negative_count']} |
| Canonical base | {base['auc']:.6f} | {base['fsr']:.2%} | {base['fpr']:.2%} | {base['threshold']:.8g} | {base['positive_count']}/{base['negative_count']} |

## Utility and reload

ARC delta: {utility['delta']['arc_challenge_acc_norm']:.6f}. TruthfulQA MC2 delta: {utility['delta']['truthfulqa_mc2_acc']:.6f}. Ordinary-generation sanity: {sanity['passed']}. Fresh-process reload: {sanity['fresh_process_reload']}.

## Deviations, limitations, and bounded conclusion

This is a single XSum run on a 3B Instruct adaptation, not a full paper reproduction. BF16 and standardized utility are benchmark/runtime adaptations. It does not establish robustness to distillation or authorize Ba unless every gate passes.

**{conclusion}** Preferred teacher: **{all(gates.values())}**. Ba allowed: **{all(gates.values())}**.
''';Path(a.report).write_text(md,encoding="utf-8")
if __name__=="__main__":main()
