"""Create a frozen, archived SWE-bench coding-patch pilot from two public agent runs.

No paid API calls here. Reads independently generated patches and archived verifier
reports from the SWE-bench submissions public S3 bucket; records hashes and provenance.
These are *reported outcomes* from the upstream harness, not tests rerun by Reppo.

Selection rule (pre-fixed before scoring):
 - Select verified SWE-bench tasks sorted by instance_id.
 - Require different binary verifier results for the two chosen published agents.
 - Require two different, nonempty patches that applied successfully.
 - Restrict to a short allowlist of permissively licensed public source repos.
 - Cap each repo at 2 tasks, each patch at 7 KB, context at 8 KB.
 - Take the first 3 eligible tasks. The first two form the one-time paid pilot.
The candidate order is never determined by which patch passed.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import urllib.request

import boto3
from botocore import UNSIGNED
from botocore.config import Config

MODEL_A = ("codex", "bash-only/20260219_mini-v2.0.0_gpt-5-2-codex", "gpt-5-2-codex")
MODEL_B = ("haiku", "bash-only/20260217_mini-v2.0.0_claude-4-5-haiku-high", "claude-haiku-4-5-20251001")
REPO_LICENSE = {
    "astropy/astropy": "BSD-3-Clause",
    "django/django": "BSD-3-Clause",
    "sympy/sympy": "BSD-3-Clause",
    "pytest-dev/pytest": "MIT",
    "scikit-learn/scikit-learn": "BSD-3-Clause",
    "pallets/flask": "BSD-3-Clause",
    "pandas-dev/pandas": "BSD-3-Clause",
    "pallets/werkzeug": "BSD-3-Clause",
    "mwaskom/seaborn": "BSD-3-Clause",
}
SPLIT = "test"
DATASET = "princeton-nlp/SWE-bench_Verified"
MAX_TASKS = 3
BUCKET = "swe-bench-submissions"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fetch_url(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Reppo-RewardBench-preflight/0.1"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read()


def fetch_tasks():
    metadata = json.loads(fetch_url("https://huggingface.co/api/datasets/" + DATASET))
    revision = metadata.get("sha")
    if not revision or len(revision) < 32:
        raise RuntimeError("Dataset SHA unavailable; aborting selection.")
    task_rows = []
    offset = 0
    while offset < 500:
        url = f"https://datasets-server.huggingface.co/rows?dataset={DATASET.replace('/', '%2F')}&config=default&split=test&offset={offset}&length=100"
        page = json.loads(fetch_url(url))
        rows = page.get("rows") or []
        if not rows:
            break
        task_rows.extend(x["row"] for x in rows if x.get("row"))
        offset += len(rows)
    if len(task_rows) < 200:
        raise RuntimeError(f"Expected SWE-bench Verified task rows, got {len(task_rows)}")
    return revision, sorted(task_rows, key=lambda r:r["instance_id"])


def s3_get(client, key):
    return client.get_object(Bucket=BUCKET, Key=key)["Body"].read()


def candidate_report(client, model, instance):
    key = model[1] + "/logs/" + instance + "/report.json"
    try:
        raw = s3_get(client, key)
        report = json.loads(raw)
        if not all((report.get("patch_exists"), report.get("patch_successfully_applied"))) or type(report.get("resolved")) is not bool:
            return None
        return {"status": report["resolved"], "key": key, "raw_sha256": sha(raw)}
    except (client.exceptions.NoSuchKey, ValueError, KeyError, json.JSONDecodeError):
        return None


def main():
    out = Path("runs/swebench-source-preflight")
    out.mkdir(parents=True, exist_ok=False)
    client = boto3.client("s3", config=Config(signature_version=UNSIGNED))
    revision, rows = fetch_tasks()
    repo_count, selected, excluded = {}, [], {}
    for task in rows:
        if len(selected) >= MAX_TASKS:
            break
        repo, tid = task.get("repo"), task.get("instance_id")
        if repo not in REPO_LICENSE or repo_count.get(repo, 0) >= 2:
            continue
        prompt = task.get("problem_statement", "")
        if not isinstance(prompt,str) or not (100 <= len(prompt.encode("utf-8")) <= 8000):
            continue
        checked = []
        for model in (MODEL_A, MODEL_B):
            v = candidate_report(client, model, tid)
            if not v:
                checked = []
                break
            checked.append(v)
        if len(checked) != 2 or checked[0]["status"] == checked[1]["status"]:
            continue
        patches=[]
        for model,verifier in zip((MODEL_A,MODEL_B),checked):
            key=model[1] + "/logs/" + tid + "/patch.diff"
            try:
                raw=s3_get(client,key)
                if not 60 <= len(raw) <= 7000:
                    break
                patch=raw.decode("utf-8")
                if not patch.startswith("diff --git "):
                    break
                patches.append({"id":model[0],"answer":patch,"verified_correct":int(verifier["status"]),
                                "model_id":model[2],
                                "verification":{"method":"deterministic-tests","artifact_sha256":verifier["raw_sha256"],
                                                "archive_report_s3":"s3://" + BUCKET + "/" + verifier["key"]},
                                "patch_sha256":sha(raw),"patch_archive_s3":"s3://"+BUCKET+"/"+key})
            except (client.exceptions.NoSuchKey,ValueError,UnicodeDecodeError):
                break
        if len(patches)!=2 or patches[0]["patch_sha256"]==patches[1]["patch_sha256"]:
            continue
        selected.append({
            "task_id":tid,"split":"test","license":REPO_LICENSE[repo],
            "instruction":f"Repository: {repo}\nTask: {prompt}\n\nAssess the proposed patch against this issue. Return a score for functional correctness; do not assume a diff that looks plausible will pass tests.",
            "source":{"dataset":DATASET,"dataset_revision":revision,"repo":repo,
                      "base_commit":task.get("base_commit"),"instance_id":tid},
            "candidates":patches})
        repo_count[repo]=repo_count.get(repo,0)+1
        print(f"Selected {len(selected)}/{MAX_TASKS}: {tid} [{repo}] outcome contrast, candidate contents not logged.",flush=True)
    if len(selected)<2:
        raise RuntimeError(f"Only {len(selected)} eligible task pairs; no paid pilot can start.")
    for row in selected:
        for cand in row["candidates"]:
            assert type(cand["verified_correct"]) is int
    output=out/"tasks.jsonl"
    output.write_text("".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in selected),encoding="utf-8")
    manifest={"source_dataset":DATASET,"dataset_commit_sha":revision,
              "model_runs":[{"id":m[2],"s3_prefix":m[1]} for m in (MODEL_A,MODEL_B)],
              "selection":"fixed lexicographic first 3 task IDs with two distinct, applied patches and discordant official archived pass/fail records, max 2 tasks/repo, individual patch <=7 KB",
              "study_type":"exploratory feasibility pilot; not holdout or independent replication",
              "task_count":len(selected),"candidate_count":sum(len(r["candidates"]) for r in selected),
              "task_sha256":sha(output.read_bytes()),
              "caveats":["Upstream SWE-bench archived verifier reports used without local harness re-execution.",
                         "Public benchmark tasks; contamination and licensing require review for scientific claims.",
                         "Only two agent runs; their patch independence is not established by identity labels alone.",
                         "Ground-truth correctness is withheld from Reppo API context and candidate payload."]}
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("Frozen dataset:",manifest["task_sha256"],"tasks:",len(selected),flush=True)


if __name__=="__main__":
    main()
