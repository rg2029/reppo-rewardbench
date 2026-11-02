"""Freeze a natural-prevalence subjective reference set without using labels to select rows.

This is a public-text and privacy screening preflight, not approval for paid
third-party API submission. The task file must be manually reviewed first.
"""
from __future__ import annotations

import collections
import gzip
import hashlib
import json
from pathlib import Path
import re
import urllib.request

DATASET="nvidia/HelpSteer2"
REVISION="990b2711a36180dd19d9c94b8627844866f8982a"
SOURCE_FILE="preference/preference.jsonl.gz"
SEED="reppo-rewardbench-subjective-natural-v1-2026-11-02"
PILOT_SEED="rewardbench-subjective-feasibility-v2-2026-11-02"
PILOT_FROZEN_IDS={"0111c604a63a9d1b","04cc0eeb163b4ce8","06f9b376120ce1b5"}
N=50
OUT=Path("runs/subjective-natural-preflight")
SENSITIVE=[
    re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"\b(?:\+?\d[\d \-.()]{8,}\d)\b"),
    re.compile(r"https?://\S+",re.I),
    re.compile(r"\b(?:internal employees|confidential|company[- ]wide memo|work email|private document|proprietary data|customer account number|my patient's|social security number|passport number)\b",re.I),
    re.compile(r"(?:<extra_id_\d+>|<\|im_start\|>|<\|im_end\|>)"),
]
def digest(s):return hashlib.sha256(s).hexdigest()
def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Reppo-RewardBench-preflight/0.2"})
    with urllib.request.urlopen(req,timeout=45) as rsp:
        data=rsp.read(30000001)
    if len(data)>30000000:raise RuntimeError("Archive too large")
    return data
def key(row):
    return digest((SEED+":"+row["prompt"]+":"+row["response_1"]+":"+row["response_2"]).encode())
def previously_scored_id(row):
    return digest((PILOT_SEED+":"+row["prompt"]+":"+row["response_1"]+":"+row["response_2"]).encode())[:16]
def main():
    OUT.mkdir(parents=True,exist_ok=False)
    metadata=json.loads(fetch("https://huggingface.co/api/datasets/"+DATASET))
    if metadata.get("sha")!=REVISION:
        raise RuntimeError("Upstream commit changed; no silent relabeling")
    if (metadata.get("cardData") or {}).get("license")!="cc-by-4.0":
        raise RuntimeError("Upstream dataset license not verified")
    archive=fetch(f"https://huggingface.co/datasets/{DATASET}/resolve/{REVISION}/{SOURCE_FILE}")
    rows=[json.loads(line) for line in gzip.decompress(archive).splitlines() if line.strip()]
    excluded=collections.Counter()
    eligible=[]
    for row in rows:
        if row.get("split")!="val":
            continue
        if previously_scored_id(row) in PILOT_FROZEN_IDS:
            excluded["pilot_overlap"]+=1;continue
        strength=row.get("preference_strength")
        if type(strength) is not int or abs(strength)>3:
            excluded["invalid_label"]+=1;continue
        prompt=row.get("prompt")
        responses=[row.get("response_1"),row.get("response_2")]
        if not isinstance(prompt,str) or not all(isinstance(r,str) for r in responses):
            excluded["missing_text"]+=1;continue
        texts=[prompt]+responses
        lens=[len(t.encode("utf-8")) for t in texts]
        if not (40<=lens[0]<=3000 and 60<=lens[1]<=4500 and 60<=lens[2]<=4500):
            excluded["length"]+=1;continue
        if any(regex.search(t) for regex in SENSITIVE for t in texts):
            excluded["sensitive_pattern_or_multiturn"]+=1;continue
        if responses[0]==responses[1]:
            excluded["same_candidate"]+=1;continue
        eligible.append(row)
    if len(eligible)<N:raise RuntimeError(f"Only {len(eligible)} eligible rows (<{N})")
    selected=sorted(eligible,key=key)[:N]
    public_rows,hidden_labels=[],[]
    for row in selected:
        marker=key(row)
        tid="helpsteer2-natural-"+marker[:16]
        public_rows.append({"task_id":tid,"instruction":row["prompt"],
                            "candidates":[{"id":"response_1","answer":row["response_1"]},
                                          {"id":"response_2","answer":row["response_2"]}],
                            "source":{"dataset":DATASET,"revision":REVISION,"split":"val","sample_hash":marker}})
        ratings=row.get("all_preferences_unprocessed") or []
        annotator=[r.get("strength") for r in ratings
                   if isinstance(r,dict) and type(r.get("strength")) is int and abs(r["strength"])<=3]
        hidden_labels.append({"task_id":tid,"preference_strength":row["preference_strength"],
                              "annotator_strengths":annotator})
    p=OUT/"judge_inputs.jsonl"
    l=OUT/"human_labels.jsonl"
    p.write_text("".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in public_rows),encoding="utf-8")
    l.write_text("".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in hidden_labels),encoding="utf-8")
    manifest={"study":"natural-prevalence human-preference sample from prefiltered public validation corpus",
              "n":N,"candidate_count":2*N,"dataset":DATASET,"revision":REVISION,
              "split":"val","seed":SEED,
              "frozen_tasks_sha256":digest(p.read_bytes()),"frozen_labels_sha256":digest(l.read_bytes()),
              "upstream_archive_sha256":digest(archive),"eligible_frame_size":len(eligible),
              "excluded":dict(excluded),
              "strata":dict(collections.Counter("tie" if r["preference_strength"]==0 else
                "weak" if abs(r["preference_strength"])==1 else "strong" for r in hidden_labels)),
              "status":"PRIVATE/RIGHTS CONTENT REVIEW REQUIRED: not approved for any API requests",
              "limitations":["Sample is random over the filtered single-turn, length-limited validation pool—not all prompts.",
                             "Text-regex filtering cannot detect all sensitive or copyrighted content.",
                             "No judge model, verifier or Reppo API calls executed.",
                             "Human labels are a reference standard with disagreement, not objective truth.",
                             "All three first-pilot pairs excluded by exact pinned source hashes before sample selection."]}
    (OUT/"manifest.json").write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("FROZEN 50-PREFERENCE SOURCE",json.dumps({
        "n":N,"eligible_frame_size":len(eligible),"strata":manifest["strata"],
        "source_sha256":manifest["frozen_tasks_sha256"],
        "labels_sha256":manifest["frozen_labels_sha256"],
        "excluded_counts":manifest["excluded"],
        "privacy_review_required":True},sort_keys=True),flush=True)

if __name__=="__main__":main()
