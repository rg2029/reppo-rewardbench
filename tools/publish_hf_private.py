"""Publish only the pre-reviewed, smoke-only Hugging Face preview.

Never publish real live evaluation logs or scientific claims from this tool.
Requires HF_TOKEN with write access to exactly the chosen repositories.
"""
from __future__ import annotations
import argparse
import os
from pathlib import Path

OWNER = "Reppo-labs"
NAME = "reppo-rewardbench"
REPO_ID = f"{OWNER}/{NAME}"
ROOT = Path(__file__).resolve().parents[1]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", choices=("dataset", "space"), required=True)
    args = ap.parse_args()
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise SystemExit("HF_TOKEN secret missing. No files were uploaded.")
    try:
        from huggingface_hub import HfApi
    except ImportError as exc:
        raise SystemExit("Install huggingface_hub in CI first.") from exc

    api = HfApi(token=token)
    info = api.repo_info(repo_id=REPO_ID, repo_type=args.target)
    if not getattr(info, "private", False):
        raise SystemExit(
            f"Refusing upload: {args.target} {REPO_ID} is not private. "
            "Make it private before syncing this smoke-only preview."
        )

    folder = ROOT / "hf" / args.target
    names = sorted(p.name for p in folder.iterdir() if p.is_file())
    allowed = {"README.md", "requirements.txt", "app.py"} if args.target == "space" else {"README.md"}
    if set(names) - allowed:
        raise SystemExit(f"Unexpected top-level files in {folder}: {set(names)-allowed}")
    if args.target == "dataset":
        allowed_deep = {"README.md", "data/smoke_preview.jsonl"}
    else:
        allowed_deep = {"README.md", "app.py", "requirements.txt"}
    present = {str(p.relative_to(folder)) for p in folder.rglob("*") if p.is_file()}
    if present != allowed_deep:
        raise SystemExit(f"Unexpected or missing files in {folder}: {present ^ allowed_deep}")
    text = (folder / "README.md").read_text(encoding="utf-8")
    if "smoke" not in text.lower() and "research results viewer" not in text.lower():
        raise SystemExit("Required disclosure missing; refusing upload.")

    api.upload_folder(
        repo_id=REPO_ID,
        repo_type=args.target,
        folder_path=str(folder),
        commit_message=f"Private smoke-only preview (source GitHub SHA {os.environ.get('GITHUB_SHA', 'manual')[:12]})",
    )
    print(f"Uploaded {args.target} preview to private {REPO_ID}.")
    print("No real study data, verified benchmarks, live evaluations, or API credentials were uploaded.")

if __name__ == "__main__":
    main()
