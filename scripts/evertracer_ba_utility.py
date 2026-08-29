#!/usr/bin/env python3
"""Evaluate only the Ba student with the frozen EverTracer A utility harness."""
import argparse,json
from pathlib import Path
from evertracer_common import load_config,write_json
from evertracer_utility import configure_offline_utility,evaluate

def main():
 p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--student",required=True);p.add_argument("--output",required=True);a=p.parse_args();c=load_config(a.config);prov=configure_offline_utility(c);s=evaluate(a.student,c["utility"]["batch_size"]);prior=json.loads(Path(c["prior_a"]["summary"]).read_text());base=prior["utility"]["base"];teacher=prior["utility"]["teacher"]
 out={"offline":True,"dataset_provenance":prov,"reused_from_immutable_a_summary":c["prior_a"]["summary"],"base":base,"teacher":teacher,"student":s,"student_delta_from_base":{"arc_challenge_acc_norm":s["arc_challenge_acc_norm"]-base["arc_challenge_acc_norm"],"truthfulqa_mc2_acc":s["truthfulqa_mc2_acc"]-base["truthfulqa_mc2_acc"]},"student_delta_from_teacher":{"arc_challenge_acc_norm":s["arc_challenge_acc_norm"]-teacher["arc_challenge_acc_norm"],"truthfulqa_mc2_acc":s["truthfulqa_mc2_acc"]-teacher["truthfulqa_mc2_acc"]}};write_json(a.output,out);print(json.dumps({k:v for k,v in out.items() if k not in ("base","teacher","student")},indent=2))
if __name__=="__main__":main()
