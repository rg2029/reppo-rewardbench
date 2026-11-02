"""Probe public SWE-bench submission archives without fetching test runs or making paid calls."""
import json
import re
import boto3
from botocore import UNSIGNED
from botocore.config import Config

TARGETS = [
 "bash-only/20260219_mini-v2.0.0_gpt-5-2-codex",
 "bash-only/20260217_mini-v2.0.0_claude-4-5-haiku-high",
 "verified/20260219_mini-v2.0.0_gpt-5-2-codex",
 "verified/20260217_mini-v2.0.0_claude-4-5-haiku-high",
 "verified/20251127_openhands_claude-opus-4-5",
]
client=boto3.client("s3",config=Config(signature_version=UNSIGNED))
for name in TARGETS:
  for folder in ("logs","trajs"):
    prefix=name+"/"+folder+"/"
    try:
      page=client.list_objects_v2(Bucket="swe-bench-submissions",Prefix=prefix,MaxKeys=8)
      keys=[x["Key"] for x in page.get("Contents",[])]
      print(json.dumps({"prefix":prefix,"sample_count":len(keys),"truncated":page.get("IsTruncated",False),"keys":keys},sort_keys=True),flush=True)
    except Exception as e:
      print(json.dumps({"prefix":prefix,"error_type":type(e).__name__,"error":str(e)[:160]}),flush=True)
