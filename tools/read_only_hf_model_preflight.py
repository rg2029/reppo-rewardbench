"""Read-only Hugging Face Inference Providers catalog preflight.

GET only. No private prompts, no inference requests, no billing calls.
Emits model availability and minimal provider pricing metadata.
"""
from __future__ import annotations
import json
import os
import urllib.request
import urllib.error

MODELS=("meta-llama/Llama-3.3-70B-Instruct",
        "Qwen/Qwen3-235B-A22B-Instruct-2507")
URL="https://router.huggingface.co/v1/models"

def main():
    token=os.environ.get("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN unavailable")
    req=urllib.request.Request(URL, headers={
        "Authorization":"Bearer "+token, "Accept":"application/json",
        "User-Agent":"Reppo-RewardBench-read-only-preflight/1.0"
    }, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=35) as response:
            data=json.load(response)
    except urllib.error.HTTPError as exc:
        print(json.dumps({"preflight":"FAILED","http_status":exc.code,"no_paid_post":True}))
        raise RuntimeError("Hugging Face read-only catalog access failed") from None
    catalog={entry.get("id"):entry for entry in data.get("data",[]) if isinstance(entry,dict)}
    result={}
    for model in MODELS:
        found=catalog.get(model)
        providers=found.get("providers",[]) if found else []
        result[model]={"available":bool(found),
            "providers":[{
                "provider":p.get("provider"),
                "status":p.get("status"),
                "pricing":p.get("pricing"),
                "context_length":p.get("context_length"),
                "supports_structured_output":p.get("supports_structured_output"),
            } for p in providers if isinstance(p,dict)]}
    print(json.dumps({"preflight":"READ_ONLY","models":result,
                      "no_paid_post":True},sort_keys=True))
    if not all(result[m]["available"] for m in MODELS):
        raise RuntimeError("At least one preregistered judge is unavailable")
if __name__=="__main__":main()
