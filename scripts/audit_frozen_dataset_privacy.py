#!/usr/bin/env python3
"""Content-safe credential/privacy scan for a JSONL dataset; never prints matched text."""
from __future__ import annotations
import argparse, collections, ipaddress, json, math, re
from pathlib import Path

STRICT = {
    "pem_private_key": re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
    "aws_access_key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "huggingface_token": re.compile(r"\bhf_[A-Za-z0-9]{30,}\b"),
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "bearer_credential": re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{20,}"),
    "assigned_credential": re.compile(r"(?i)\b(?:api[_ -]?key|access[_ -]?token|auth[_ -]?token|password|passwd|secret[_ -]?key)\s*[:=]\s*['\"]?[A-Za-z0-9._~+/=-]{12,}"),
    "windows_user_path": re.compile(r"(?i)\b[A-Z]:\\Users\\[^\\\s]+"),
    "ssh_private_path": re.compile(r"(?:^|\s)/(?:root|home/[^/\s]+)/\.ssh/(?:id_[a-z0-9_-]+|authorized_keys)\b"),
}
PII = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "ipv4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "phone_like": re.compile(r"(?<!\d)(?:\+?\d[\d ()-]{8,}\d)(?!\d)"),
}
HIGH_ENTROPY = re.compile(r"\b[A-Za-z0-9+/=_-]{32,}\b")

def entropy(value: str) -> float:
    counts=collections.Counter(value);n=len(value)
    return -sum((c/n)*math.log2(c/n) for c in counts.values())

def main() -> None:
    p=argparse.ArgumentParser();p.add_argument("--input",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    strict=collections.Counter();pii=collections.Counter();pii_ids=collections.defaultdict(set);email_domains=collections.Counter();ip_classes=collections.Counter();phone_lengths=collections.Counter();entropy_hits=0;affected=set();records=0
    with a.input.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():continue
            row=json.loads(line);records+=1;sample_id=str(row.get("sample_id","unavailable"));text="\n".join(str(row.get(k,"")) for k in ("instruction","input","teacher_raw_answer"))
            hit=False
            for name,pattern in STRICT.items():
                count=len(pattern.findall(text));strict[name]+=count;hit|=count>0
            for name,pattern in PII.items():
                matches=pattern.findall(text);pii[name]+=len(matches)
                if matches:pii_ids[name].add(sample_id)
                if name=="email":
                    for value in matches:email_domains[value.rsplit("@",1)[-1].casefold()]+=1
                elif name=="ipv4":
                    for value in matches:
                        try:
                            address=ipaddress.ip_address(value);label="private_or_reserved" if not address.is_global else "global"
                        except ValueError:label="invalid"
                        ip_classes[label]+=1
                elif name=="phone_like":
                    for value in matches:phone_lengths[len(re.sub(r"\D","",value))]+=1
            for candidate in HIGH_ENTROPY.findall(text):
                if entropy(candidate)>=4.5:entropy_hits+=1;hit=True
            if hit:affected.add(sample_id)
    result={"records_scanned":records,"strict_secret_hits":dict(strict),"strict_secret_total":sum(strict.values()),"strict_or_entropy_affected_sample_ids":sorted(affected),"high_entropy_candidate_count":entropy_hits,"pii_diagnostic_counts":dict(pii),"pii_sample_ids":{k:sorted(v) for k,v in pii_ids.items()},"email_domain_counts":dict(email_domains),"ip_address_classes":dict(ip_classes),"phone_digit_length_counts":dict(phone_lengths),"verdict":"PASS" if not affected else "REVIEW_REQUIRED","matched_text_emitted":False}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8");print(json.dumps(result,indent=2))

if __name__=="__main__":main()
