"""Check public SWE-bench artifact schema and Hugging Face task lookup."""
import boto3,json,urllib.request
from botocore import UNSIGNED
from botocore.config import Config
s3=boto3.client("s3",config=Config(signature_version=UNSIGNED))
models=["bash-only/20260219_mini-v2.0.0_gpt-5-2-codex","bash-only/20260217_mini-v2.0.0_claude-4-5-haiku-high"]
ids=["astropy__astropy-12907","astropy__astropy-13033","astropy__astropy-13236"]
for model in models:
 for tid in ids[:2]:
  p=model+"/logs/"+tid+"/"
  for f in ("report.json","patch.diff","test_output.txt"):
   try:
    resp=s3.get_object(Bucket="swe-bench-submissions",Key=p+f)["Body"].read()
    print(json.dumps({"model":model.split("/")[-1],"id":tid,"file":f,"size":len(resp),"sample":resp.decode("utf-8",errors="replace")[:1500] if f=="report.json" else resp.decode("utf-8",errors="replace")[:160]}),flush=True)
   except Exception as e:
    print(json.dumps({"key":p+f,"error":str(e)[:140]}))
for url in [
"https://datasets-server.huggingface.co/splits?dataset=princeton-nlp/SWE-bench_Verified",
"https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=0&length=1"
]:
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"rewardbench-research/0.4"})
  with urllib.request.urlopen(req,timeout=20) as res:
   data=res.read()
  print(json.dumps({"hf_url":url,"bytes":len(data),"sample":data[:1100].decode()}),flush=True)
 except Exception as e:print(json.dumps({"hf_url":url,"error":str(e)[:250]}))
