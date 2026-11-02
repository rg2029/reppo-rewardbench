"""Freeze a small human-preference pilot from a pinned, public HelpSteer2 file.

No Reppo calls. Labels are separated from judge-facing candidate text. Output is
an exploratory, deliberately stratified sample, not a natural-prevalence holdout.
"""
from __future__ import annotations
import collections
import gzip
import hashlib
import json
from pathlib import Path
import re
import urllib.request

SOURCE="nvidia/HelpSteer2"
REVISION="990b2711a36180dd19d9c94b8627844866f8982a"
FILE="preference/preference.jsonl.gz"
SPLIT="validation"
SEED="rewardbench-subjective-feasibility-v1-2026-11-02"
MAX_ARCHIVE_BYTES=30000000
TARGET_PER_STRATUM=3
STRATA={"weak":lambda x:abs(x)==1,"strong":lambda x:abs(x)>=2}
SENSITIVE=(re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),
           re.compile(r"\b(?:\+?\d[\d \-.()]{8,}\d)\b"))
def sha(b):return hashlib.sha256(b).hexdigest()
def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Reppo-RewardBench-preference-preflight/0.1"})
    with urllib.request.urlopen(req,timeout=55) as r:
        data=r.read(MAX_ARCHIVE_BYTES+1)
    if len(data)>MAX_ARCHIVE_BYTES:raise RuntimeError("Source archive larger than configured limit")
    return data
def stable(r):
    return sha((SEED+":"+r["prompt"]+":"+r["response_1"]+":"+r["response_2"]).encode())
def main():
    out=Path("runs/human-preference-preflight")
    out.mkdir(parents=True,exist_ok=False)
    info=json.loads(get("https://huggingface.co/api/datasets/"+SOURCE).decode())
    if info.get("sha")!=REVISION:raise RuntimeError("Dataset revision changed: inspect, repin, and freeze before scoring")
    if (info.get("cardData") or {}).get("license")!="cc-by-4.0":raise RuntimeError("Dataset license changed")
    blob=get("https://huggingface.co/datasets/"+SOURCE+"/resolve/"+REVISION+"/"+FILE)
    decoded=gzip.decompress(blob)
    records=[json.loads(line) for line in decoded.splitlines() if line.strip()]
    counts=collections.Counter(), collections.Counter()
    usable=[]
    for row in records:
        counts[0][str(row.get("split"))]+=1
        if row.get("split")!=SPLIT:continue
        if type(row.get("preference_strength")) is not int or abs(row["preference_strength"])>3:continue
        prompt,response1,response2=[row.get(k) for k in ("prompt","response_1","response_2")]
        if not all(isinstance(v,str) and v.strip() for v in (prompt,response1,response2)):continue
        sizes=[len(t.encode("utf-8")) for t in (prompt,response1,response2)]
        if not (40<=sizes[0]<=4500 and 60<=sizes[1]<=6500 and 60<=sizes[2]<=6500):continue
        if any(pattern.search(t) for pattern in SENSITIVE for t in (prompt,response1,response2)):continue
        counts[1][str(row["preference_strength"])]+=1
        usable.append(row)
    print("SOURCE SPLITS",json.dumps(dict(counts[0]),sort_keys=True),flush=True)
    print("QUALIFIED VALIDATION PREFERENCE STRENGTH",json.dumps(dict(counts[1]),sort_keys=True),flush=True)
    samples=[]
    for name,predicate in STRATA.items():
        eligible=sorted((r for r in usable if predicate(r["preference_strength"])),key=stable)
        if len(eligible)<TARGET_PER_STRATUM:raise RuntimeError(f"Insufficient eligible validation rows for stratum {name}")
        samples.extend((name,r) for r in eligible[:TARGET_PER_STRATUM])
    judges, labels=[],[]
    seen=set()
    for name,row in sorted(samples,key=lambda x:stable(x[1])):
        marker=stable(row)
        if marker in seen:raise RuntimeError("Duplicate sample")
        seen.add(marker)
        prefs=row.get("all_preferences_unprocessed") or []
        ratings=[v["strength"] for v in prefs if isinstance(v,dict) and type(v.get("strength")) is int and abs(v["strength"])<=3]
        human=row["preference_strength"]
        judges.append({
            "task_id":"helpsteer2-"+marker[:16],
            "instruction":row["prompt"],
            "candidates":[{"id":"response_1","answer":row["response_1"]},{"id":"response_2","answer":row["response_2"]}],
            "source":{"dataset":SOURCE,"revision":REVISION,"split":SPLIT,
                      "sample_hash":marker,"stratum":name}
        })
        labels.append({"task_id":"helpsteer2-"+marker[:16],"preference_strength":human,
                       "annotator_strengths":ratings,"stratum":name,
                       "prompt_sha256":sha(row["prompt"].encode("utf-8")),
                       "response_sha256":[sha(row["response_1"].encode("utf-8")),sha(row["response_2"].encode("utf-8"))]})
    inputs=out/"judge_inputs.jsonl"
    truth=out/"human_labels.jsonl"
    inputs.write_text("".join(json.dumps(r,sort_keys=True,ensure_ascii=False)+"\n" for r in judges),encoding="utf-8")
    truth.write_text("".join(json.dumps(r,sort_keys=True,ensure_ascii=False)+"\n" for r in labels),encoding="utf-8")
    manifest={"dataset":SOURCE,"source_file":FILE,"revision":REVISION,"raw_archive_sha256":sha(blob),
        "source_split":SPLIT,"selection_seed":SEED,"selection":"three each weak (+/-1), strong (+/-2 or 3), SHA-sorted with public-text and size filters; ties are assessed separately via RewardBench 2 Ties",
        "source_rows_by_split":dict(counts[0]),"eligible_validation_by_strength":dict(counts[1]),
        "selected_by_stratum":dict(collections.Counter(x["stratum"] for x in labels)),
        "judge_inputs_sha256":sha(inputs.read_bytes()),"human_labels_sha256":sha(truth.read_bytes()),
        "notes":["Labels are separate from the judge-facing file and must never be sent in API requests.",
                 "Stratified weak/strong pilot is NOT representative. Inter-rater disagreements are separately retained; source contains insufficient tied validation examples.",
                 "Dataset is CC BY 4.0; third-party model and user content rights/privacy require review before live use.",
                 "This script does not call Reppo or other paid APIs."]}
    (out/"manifest.json").write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("FROZEN HUMAN PREFERENCE DATA",json.dumps({k:manifest[k] for k in ("revision","selected_by_stratum","judge_inputs_sha256","source_rows_by_split")},sort_keys=True),flush=True)

if __name__=="__main__":main()
