"""Load the corpus into a running stack, or re-download the public PDFs.

    python3 scripts/load_corpus.py                 # upload every PDF in corpus/manifest.json
    python3 scripts/load_corpus.py --download      # first re-fetch the public PDFs and verify them
    python3 scripts/load_corpus.py --base https://<host> --exec "kubectl exec -i deploy/api --"

Uploads use the canonical titles from the manifest. Already-uploaded files (same bytes) are
skipped, so running it twice is safe. Waits until every document is ready. Standard library only.
A deployment that takes no guest uploads is loaded with --exec: each PDF goes through
`python -m app.add_to_library` inside the API container, and --base is used only to wait.
"""

import argparse
import hashlib
import json
import shlex
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from smoke_test import call, upload  # noqa: E402 - shared helpers next to this script

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "corpus" / "manifest.json"
PDFS = ROOT / "corpus" / "pdfs"


def download(documents: list[dict]) -> None:
    for doc in documents:
        if doc["kind"] != "public":
            continue
        req = urllib.request.Request(doc["source"], headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = resp.read()
        digest = hashlib.sha256(data).hexdigest()
        if digest != doc["sha256"]:
            raise SystemExit(f"{doc['file']}: checksum differs from the manifest ({digest})")
        (PDFS / doc["file"]).write_bytes(data)
        print(f"downloaded {doc['file']} ({len(data)} bytes, checksum ok)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://localhost:8080")
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--exec", dest="exec_prefix", help="prefix that runs a command in the API")
    args = parser.parse_args()
    documents = json.loads(MANIFEST.read_text())["documents"]
    if args.download:
        download(documents)

    ids = []
    for doc in documents:
        content = (PDFS / doc["file"]).read_bytes()
        if hashlib.sha256(content).hexdigest() != doc["sha256"]:
            raise SystemExit(f"{doc['file']}: checksum differs from the manifest")
        if args.exec_prefix:
            command = shlex.split(args.exec_prefix) + ["python", "-m", "app.add_to_library"]
            command += ["--title", doc["title"], "--file-name", doc["file"]]
            try:
                done = subprocess.run(command, input=content, capture_output=True, timeout=300)
            except subprocess.TimeoutExpired:
                print(f"upload failed for {doc['file']}: no answer in 300 s")
                return 1
            if done.returncode != 0:
                print(f"upload failed for {doc['file']}: {done.stderr.decode().strip()}")
                return 1
            added = json.loads(done.stdout.decode().splitlines()[-1])
            status = 202 if added["new"] else 409
            body = {"id": added["id"], "detail": {"document_id": added["id"]}}
        else:
            status, body = upload(args.base, doc["file"], content, doc["title"])
        if status == 202:
            ids.append(body["id"])
            print(f"uploaded {doc['file']} as document {body['id']}")
        elif status == 409:
            ids.append(body["detail"]["document_id"])
            print(f"already loaded {doc['file']} (document {body['detail']['document_id']})")
        else:
            print(f"upload failed for {doc['file']}: {status} {body}")
            return 1

    started = time.monotonic()
    states: dict[int, str] = {}
    while time.monotonic() - started < args.timeout:
        _, docs = call("GET", f"{args.base}/api/documents")
        listed = {d["id"]: d["status"] for d in docs}
        states = {i: listed.get(i, "missing") for i in ids}
        if all(s in ("ready", "failed", "missing") for s in states.values()):
            break
        time.sleep(3)
    failed = [i for i, s in states.items() if s != "ready"]
    print(
        f"{len(ids) - len(failed)} of {len(ids)} documents ready"
        + (f"; not ready: {failed}" if failed else "")
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
