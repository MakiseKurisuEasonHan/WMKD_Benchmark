"""Authorized Level 2 diagnostic; NOT comparable to frozen Llama detector."""
import json
import math
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from evertracer_common import corrected_detector_metrics, sha256_file, write_json

P = Path('/root/autodl-tmp/WMKD_Benchmark')
D = Path(str(P) + '_data')
E = P / 'results/active_cross_lineage_bb/evertracer'
AUDIT = P / 'results/active_cross_lineage_ba/evertracer/static_probe_tokenizer_audit.json'
DISCLAIMER = 'EXPLORATORY_NON_COMPARABLE: NOT DIRECTLY COMPARABLE TO HISTORICAL LLAMA DETECTOR; cannot establish watermark survival, failure or transfer.'


def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--model',required=True);args=parser.parse_args()
    out = E / 'exploratory_detector'
    out.mkdir(exist_ok=False)
    fp = D / 'runs/evertracer/evertracer_a_20260828_223155_cont1/artifacts/frozen_neighborhoods.jsonl'
    assert sha256_file(fp) == '7834e3d77704951ea06501c2166e960fef2b147ced3d751a8e55f07ec7b3672b'
    rows = [json.loads(x) for x in fp.read_text().splitlines()]
    audit = json.loads(AUDIT.read_text())
    refs = audit['historical_scalar_artifacts']
    for item in refs.values():
        assert sha256_file(item['path']) == item['sha256']
    assert len(rows) == 200
    for i, row in enumerate(rows):
        assert len(row['pairs']) == 5
        for item in refs.values():
            s = item['scores'][i]
            assert all(s[k] == row[k] for k in ('subset', 'position', 'source_index'))
            assert s['reference_variation'] == refs['teacher']['scores'][i]['reference_variation']
    model_path = Path(args.model)
    assert model_path.resolve().is_relative_to(D/'runs/active_cross_lineage_bb'), 'XBb model path required'
    tok = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    tok.pad_token = tok.pad_token or tok.eos_token
    provenance = dict(disclaimer=DISCLAIMER, canonical_detector_result='N/A_CROSS_TOKENIZER',
                      tokenizer='Qwen/Qwen2.5-3B-Instruct', revision='8f4992eda43eea7c770690ddc0de8f732da246f5',
                      model_path=str(model_path), max_token_window=128, scoring='exp(-mean next-token loss)',
                      reference='frozen historical reference_variation; no recalibration',
                      frozen_probe_sha256=sha256_file(fp), script_sha256=sha256_file(__file__),
                      aggregation_sha256=sha256_file(P/'scripts/evertracer_common.py'),
                      visible_text_audit_sha256=sha256_file(AUDIT),
                      reference_artifacts={k:{a:v[a] for a in ('path','sha256')} for k,v in refs.items()},
                      visible_text_differences=audit['summary'], fpr_limit=0.05)
    write_json(out / 'provenance.json', provenance)
    model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True,
                                                torch_dtype=torch.bfloat16, device_map='cuda:0').eval()
    started = time.monotonic()
    scores = []
    with (out / 'raw_scores.jsonl').open('x') as handle:
        for i, row in enumerate(rows):
            texts = [('original', row['original'])] + [(str(k)+'/'+side, pair[side])
                    for k,pair in enumerate(row['pairs']) for side in ('positive','negative')]
            measured = []
            for role, text in texts:
                enc = tok(text, return_tensors='pt', truncation=True, max_length=128).to(model.device)
                ids = enc['input_ids'][0].tolist()
                assert len(ids) > 1
                with torch.no_grad():
                    loss = model(**enc, labels=enc['input_ids']).loss.float().item()
                assert math.isfinite(loss)
                measured.append(dict(role=role, text=text, input_ids=ids,
                                     visible_text=tok.decode(ids, skip_special_tokens=True, clean_up_tokenization_spaces=False),
                                     scored_positions=len(ids)-1, mean_loss=loss, probability=math.exp(-loss)))
            variation = sum(x['probability'] for x in measured[1:])/10-measured[0]['probability']
            ref = refs['teacher']['scores'][i]['reference_variation']
            score = {k:row[k] for k in ('subset','position','source_index')}
            score.update(suspect_variation=variation, reference_variation=ref, calibrated_score=variation-ref)
            scores.append(score)
            handle.write(json.dumps(dict(index=i, member_label=int(row['subset']=='dtr'), scores=score,
                                         raw_original=measured[0], raw_perturbations=measured[1:]))+'\n')
            handle.flush()
            print(json.dumps(dict(progress=i+1,total=200)), flush=True)
    assert sum(s['subset']=='dtr' for s in scores)==100
    assert sum(s['subset']=='dunseen' for s in scores)==100
    metrics = corrected_detector_metrics(scores, 0.05)
    members = [-s['calibrated_score'] for s in scores if s['subset']=='dtr']
    others = [-s['calibrated_score'] for s in scores if s['subset']=='dunseen']
    roc = [dict(threshold='Infinity',tpr=0.0,fpr=0.0)]
    for threshold in sorted(set(members+others),reverse=True):
        roc.append(dict(threshold=threshold,tpr=sum(x>=threshold for x in members)/100,
                        fpr=sum(x>=threshold for x in others)/100))
    write_json(out/'roc.json', roc)
    write_json(out/'detector_results.json', dict(status='COMPLETE',disclaimer=DISCLAIMER,
        canonical_detector_result='N/A_CROSS_TOKENIZER',strictly_comparable_to_same_lineage=False,
        metrics=metrics,scores=scores,raw_sha256=sha256_file(out/'raw_scores.jsonl'),
        elapsed_seconds=time.monotonic()-started,raw_original_count=200,raw_perturbation_count=2000))


if __name__ == '__main__':
    main()
