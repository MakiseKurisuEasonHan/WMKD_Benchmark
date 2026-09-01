"""Fresh-process canonical utility and sanity for SCW Ba Base/Teacher/Student."""
import argparse, gc, json, os
from pathlib import Path

def evaluate(path, batch):
    import lm_eval
    result = lm_eval.simple_evaluate(model="hf", model_args=f"pretrained={path},local_files_only=True,dtype=bfloat16",
        tasks=["arc_challenge", "truthfulqa_mc2"], batch_size=batch, apply_chat_template=True)["results"]
    return {"arc_challenge_acc_norm": result["arc_challenge"].get("acc_norm,none", result["arc_challenge"].get("acc_norm")),
            "truthfulqa_mc2_acc": result["truthfulqa_mc2"].get("acc,none", result["truthfulqa_mc2"].get("acc")), "raw_results": result}

def sanity(path, prompts):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(path, local_files_only=True); tok.pad_token = tok.pad_token or tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(path, local_files_only=True, torch_dtype=torch.bfloat16, device_map="cuda").eval()
    rows=[]
    for prompt in prompts:
        inputs=tok(prompt, return_tensors="pt").to("cuda")
        with torch.no_grad(): output=model.generate(**inputs, max_new_tokens=64, do_sample=False, pad_token_id=tok.pad_token_id)
        completion=tok.decode(output[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        rows.append({"prompt":prompt,"completion":completion,"functional":bool(completion.strip()) and len(set(completion.split()))>2})
    del model; gc.collect(); torch.cuda.empty_cache()
    return {"passed":all(row["functional"] for row in rows),"rows":rows}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--base",required=True); p.add_argument("--teacher",required=True); p.add_argument("--student",required=True); p.add_argument("--output",required=True); p.add_argument("--batch-size",type=int,default=8); a=p.parse_args()
    os.environ.update({"HF_HOME":"/root/autodl-tmp/WMKD_Benchmark_data/cache/huggingface","HF_HUB_CACHE":"/root/autodl-tmp/WMKD_Benchmark_data/cache/huggingface/hub","HF_DATASETS_CACHE":"/root/autodl-tmp/WMKD_Benchmark_data/cache/huggingface/datasets","HF_HUB_OFFLINE":"1","HF_DATASETS_OFFLINE":"1","TRANSFORMERS_OFFLINE":"1"})
    paths={"base":a.base,"teacher":a.teacher,"student":a.student}; result={"fresh_process_reload":True}
    for label,path in paths.items(): result[label]=evaluate(path,a.batch_size)
    ordinary=["What is the capital of France?","Explain why the sky appears blue.","Solve: 3x + 5 = 20.","Write a polite thank-you note."]
    french=["Expliquez simplement pourquoi le ciel est bleu.","Rédigez un court message de remerciement.","Résolvez 3x + 5 = 20 en français.","Donnez trois conseils pour organiser une journée chargée."]
    result["ordinary_generation"]={label:sanity(path,ordinary) for label,path in paths.items()}
    result["french_supplementary"]={label:sanity(path,french) for label,path in paths.items()}
    Path(a.output).parent.mkdir(parents=True,exist_ok=True); Path(a.output).write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
if __name__=="__main__": main()
