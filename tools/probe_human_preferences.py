"""Inspect public human-preference dataset API schemas, without Reppo calls.

The output is schema-only: field names, split sizes, examples' *lengths*,
dataset revision and preference-strength counts (when a safe split is found).
No private data, human justifications, or model answers are printed.
"""
from __future__ import annotations
import collections
import json
import urllib.parse
import urllib.request

DATASET="nvidia/HelpSteer2"
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Reppo-RewardBench-data-preflight/0.1"}),timeout=30) as res:
        return json.load(res)

def main():
    info=get("https://huggingface.co/api/datasets/"+DATASET)
    print("dataset:",DATASET,"sha:",info.get("sha"),"license:",(info.get("cardData") or {}).get("license"),flush=True)
    splits=get("https://datasets-server.huggingface.co/splits?dataset="+urllib.parse.quote(DATASET,safe=""))
    for row in splits.get("splits",[]):
        print("AVAILABLE SPLIT",json.dumps({k:row.get(k) for k in ("config","split","num_rows")},sort_keys=True),flush=True)
    preferred=[r for r in splits.get("splits",[]) if "preference" in r.get("config","").lower()]
    if not preferred:
        # HF server often exposes only the top-level config, not data_dir files.
        names = sorted(item.get("rfilename", "") for item in info.get("siblings", []))
        source_files = [name for name in names if "preference" in name.lower() or "disagreement" in name.lower()]
        print("HF REPO PREFERENCE FILES", json.dumps(source_files[:50]), flush=True)
        if not source_files:
            raise SystemExit("No preference files/config found; dataset may have changed.")
        print("Dataset-server preference config unavailable. Use explicit pinned files for next stage.",flush=True)
        return
    preferred.sort(key=lambda x:(x.get("split") != "validation",x.get("config",""),x.get("split","")))
    first=preferred[0]
    q=urllib.parse.urlencode({"dataset":DATASET,"config":first["config"],"split":first["split"],"offset":0,"length":50})
    rows=get("https://datasets-server.huggingface.co/rows?"+q).get("rows") or []
    if not rows:raise SystemExit("No preference rows available")
    records=[x["row"] for x in rows]
    print("SCHEMA",json.dumps(sorted(records[0]),sort_keys=True),flush=True)
    strengths=collections.Counter(str(x.get("preference_strength","MISSING")) for x in records)
    print("PREFERENCE COUNTS IN FIRST SAMPLE",json.dumps(strengths,sort_keys=True),flush=True)
    for field in ("prompt","response_1","response_2"):
        print("TEXT LEN",field, [len(str(x.get(field,""))) for x in records[:5]],flush=True)
    print("INDIVIDUAL ANNOTATIONS FIELD",any(x.get("all_preferences_unprocessed") is not None for x in records),flush=True)
    print("SCHEMA PROBE COMPLETED, 0 PAID CALLS",flush=True)

if __name__=="__main__":
    main()
