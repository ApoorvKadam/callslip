"""End-to-end smoke test against a running stack. Standard library only.

    python scripts/smoke_test.py [--base http://localhost:8080] [--pdf path/to/file.pdf]

Checks liveness and readiness, signs in to a smoke-test account, uploads a PDF (a tiny
generated one if --pdf is not given), waits until the worker has parsed, chunked and embedded
it, and prints what it found. The upload belongs to that account, so it never appears in the
shared collection that users and the agent see.
Exits non-zero on any failure, so CI and the runbook can rely on it.
"""

import argparse
import http.cookiejar
import json
import os
import secrets
import sys
import time
import urllib.error
import urllib.request
import uuid

# Keeps the sign-in cookie between calls.
OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
# The account owns nothing but the smoke test's own document. With SMOKE_PASSWORD set (as
# scripts/verify.sh does from .env), every run reuses one account and one document. Without
# it, each run makes a throwaway account with a random password.
PASSWORD = os.environ.get("SMOKE_PASSWORD")
ACCOUNT = {
    "email": "smoke-test@callslip.invalid"
    if PASSWORD
    else f"smoke-test-{secrets.token_hex(6)}@callslip.invalid",
    "password": PASSWORD or secrets.token_urlsafe(24),
}


def call(method: str, url: str, body: bytes | None = None, headers: dict | None = None):
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with OPENER.open(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read() or b"null")
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read() or b"null")


def tiny_pdf(text: str) -> bytes:
    """A minimal valid one-page PDF with a text layer, built by hand (no dependencies)."""
    stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R"
        b" /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % number + obj + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    out += b"".join(b"%010d 00000 n \n" % off for off in offsets)
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (
        len(objects) + 1,
        xref,
    )
    return bytes(out)


def upload(base: str, filename: str, content: bytes, title: str):
    boundary = uuid.uuid4().hex
    parts = [
        f'--{boundary}\r\nContent-Disposition: form-data; name="title"\r\n\r\n{title}\r\n'.encode(),
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        "Content-Type: application/pdf\r\n\r\n".encode()
        + content
        + b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    return call("POST", f"{base}/api/documents", b"".join(parts), headers)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://localhost:8080")
    parser.add_argument("--pdf", help="PDF to upload (default: a generated one-page PDF)")
    parser.add_argument("--title", default=None)
    parser.add_argument("--query", default=None, help="search query to run after ingestion")
    parser.add_argument("--timeout", type=int, default=240)
    args = parser.parse_args()

    status, body = call("GET", f"{args.base}/api/health")
    print("health:", status, body)
    if status != 200:
        return 1
    status, body = call("GET", f"{args.base}/api/ready")
    print("ready:", status, body)
    if status != 200:
        return 1

    credentials = json.dumps(ACCOUNT).encode()
    headers = {"Content-Type": "application/json"}
    status, body = call("POST", f"{args.base}/api/auth/login", credentials, headers)
    if status == 401:  # first run on this database
        status, body = call("POST", f"{args.base}/api/auth/register", credentials, headers)
    print("sign in:", status, body)
    if status not in (200, 201):
        return 1

    if args.pdf:
        with open(args.pdf, "rb") as f:
            content = f.read()
        filename = args.pdf.rsplit("/", 1)[-1]
    else:
        # Same bytes every time: a second run finds it already uploaded (409), so checking a
        # deployment leaves one small private test document, not one per run.
        content = tiny_pdf("Smoke test document, uploaded by scripts/smoke_test.py.")
        filename = "smoke-test.pdf"
    title = args.title or ("Smoke test document" if not args.pdf else filename)
    status, body = upload(args.base, filename, content, title)
    if status == 409:
        doc_id = body["detail"]["document_id"]
        print("upload: already present as document", doc_id)
    elif status == 202:
        doc_id = body["id"]
        print("upload:", status, f"document {doc_id} {body['status']}")
    else:
        print("upload failed:", status, body)
        return 1

    started = time.monotonic()
    _, doc = call("GET", f"{args.base}/api/documents/{doc_id}")
    while doc["status"] not in ("ready", "failed") and time.monotonic() - started < args.timeout:
        time.sleep(2)
        _, doc = call("GET", f"{args.base}/api/documents/{doc_id}")
    seconds = round(time.monotonic() - started, 1)
    print(
        f"ingest: {doc['status']} after {seconds}s, pages={doc['page_count']}, "
        f"passages={doc['chunk_count']}, error={doc['error']}"
    )
    if doc["status"] != "ready" or doc["chunk_count"] == 0:
        return 1

    query = {"query": args.query or "smoke test document", "document_ids": [doc_id], "top_k": 3}
    body = json.dumps(query).encode()
    headers = {"Content-Type": "application/json"}
    status, result = call("POST", f"{args.base}/api/search", body, headers)
    hits = result.get("hits", []) if status == 200 else []
    print(f"search: {status}, {len(hits)} hits, cache={result.get('cache')}, ms={result.get('ms')}")
    for hit in hits:
        print(f"  page {hit['page_no']}  score {hit['score']:.4f}  {hit['text'][:90]}")
    return 0 if hits else 1


if __name__ == "__main__":
    sys.exit(main())
