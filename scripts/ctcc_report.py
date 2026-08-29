"""Aggregate CTCC Experiment A report and machine-readable summary."""
import argparse,json
from pathlib import Path
import yaml

def load(path): return json.loads(Path(path).read_text())
def main():
 p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--run-dir",required=True);a=p.parse_args();c=yaml.safe_load(Path(a.config).read_text());r=Path(a.run_dir);train=load(r/"metrics/training.json");base=load(r/"evaluation/base_ctcc.json")["summary"];teacher=load(r/"evaluation/teacher_ctcc.json")["summary"];utility=load(r/"evaluation/utility.json");sanity=load(r/"evaluation/sanity.json");manifest=load(Path(c["dataset"]["frozen_root"])/"manifest.json")
 gates={"overall_trigger":teacher["categories"]["trigger"]["activation_rate"]>=c["evaluation"]["trigger_fsr_gate"],"combined_negative":teacher["combined_negatives"]["false_activation_rate"]<=c["evaluation"]["combined_negative_false_activation_gate"],"base_clean":base["categories"]["trigger"]["activation_rate"]<=0.05 and base["combined_negatives"]["false_activation_rate"]<=0.05,"generation_errors":sum(x["generation_errors"] for x in teacher["categories"].values())==0,"utility_functional":utility["delta"]["arc_challenge_acc_norm"]>=-0.10 and utility["delta"]["truthfulqa_mc2_acc"]>=-0.10,"ordinary_generation":sanity["passed"],"fresh_reload":teacher["fresh_process_reload"] and sanity["fresh_process_reload"]}
 preferred=all(gates.values());judgement="CTCC core reproduction successful under the pinned public-artifact setting." if preferred else "CTCC core reproduction not established under all WMKD gates."
 summary={"project":"WMKD_Benchmark","method":"CTCC","experiment":"A","run_id":r.name,"official_source":c["official_source"],"model":c["model"],"fingerprint":c["fingerprint"],"dataset":manifest,"paper_vs_public_artifact_discrepancy":{"paper_training":c["dataset"]["paper_reported_counts"],"formal_training":c["dataset"]["formal_public_artifact_counts"],"paper_test":c["dataset"]["paper_reported_test_counts"],"formal_test":c["dataset"]["formal_public_artifact_test_counts"],"seen_unseen_limitation":"paper-reported partition could not be exactly reconstructed from released public artifact"},"training_config":c["training"],"training":train,"detector":c["evaluation"]["detector"],"base_control":base,"teacher":teacher,"utility":utility,"ordinary_generation":sanity,"reload":"PASSED" if gates["fresh_reload"] else "FAILED","gates":gates,"preferred_teacher":preferred,"final_judgement":judgement,"limitations":["single canonical 3B backbone and one seed","public artifact has 1889 training and 300 test records versus paper-described 2000 and 295","WMKD operational exact-match detector is not claimed as official CTCC semantics","paper seen/unseen partition is not reconstructed"]};(r/"reports/summary.json").write_text(json.dumps(summary,indent=2)+"\n")
 md=f'''# CTCC Experiment A Report

## Objective
Reproduce the CTCC cross-turn contextual fingerprint `IAMALIVE` on the canonical WMKD 3B backbone and determine preferred-teacher status.

## Provenance and configuration
- Official source: `{c['official_source']['repository']}@{c['official_source']['commit']}`
- Model: `{c['model']['id']}@{c['model']['revision']}`
- Training: 12 epochs, LR 1e-4 cosine, cutoff 2048, packing false, LoRA r8/alpha16/dropout0/all-linear, BF16, batch 8, accumulation 2, seed 48, adamw_torch.
- Weight decay: 0.0 as a runtime-inherited reproduction value; the paper does not explicitly specify it.

## Paper versus released artifact
The paper-described training size is 500/500/1000=2000, while the pinned executable public artifact contains 461/428/1000=1889. WMKD faithfully uses all 1889 released records without duplication or synthesis. The released test has 95 Trigger, 100 Suppression, and 105 Normal records (300 total), versus the paper-described 295. The paper-reported seen/unseen partition could not be exactly reconstructed; identity-based audit remains provenance, not an official split.

## Detector
WMKD operational CTCC detector: generated answer `strip()` followed by case-sensitive exact match to `IAMALIVE`. This is not claimed as the official CTCC detector. All raw generations are preserved.

## Results
- Base Trigger: {base['categories']['trigger']['activations']}/{base['categories']['trigger']['count']} ({base['categories']['trigger']['activation_rate']:.4f})
- Teacher Trigger: {teacher['categories']['trigger']['activations']}/{teacher['categories']['trigger']['count']} ({teacher['categories']['trigger']['activation_rate']:.4f})
- Teacher Suppression false activation: {teacher['categories']['suppression']['activations']}/{teacher['categories']['suppression']['count']}
- Teacher Normal false activation: {teacher['categories']['normal']['activations']}/{teacher['categories']['normal']['count']}
- Teacher combined negatives: {teacher['combined_negatives']['false_activations']}/{teacher['combined_negatives']['count']} ({teacher['combined_negatives']['false_activation_rate']:.4f})
- ARC Base/Teacher: {utility['base']['arc_challenge_acc_norm']:.6f}/{utility['teacher']['arc_challenge_acc_norm']:.6f}
- TruthfulQA MC2 Base/Teacher: {utility['base']['truthfulqa_mc2_acc']:.6f}/{utility['teacher']['truthfulqa_mc2_acc']:.6f}
- Ordinary generation: {'PASSED' if sanity['passed'] else 'FAILED'}
- Fresh reload: {'PASSED' if gates['fresh_reload'] else 'FAILED'}

## Bounded conclusion
{judgement}

Preferred teacher: **{'YES' if preferred else 'NO'}**. No Ba or ModelScope action is authorized by this result.
''';(r/"reports/report.md").write_text(md);print(json.dumps({"preferred_teacher":preferred,"gates":gates,"judgement":judgement},indent=2))
if __name__=="__main__":main()
