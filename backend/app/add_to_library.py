"""Add a PDF to the shared collection from inside a deployment.

    kubectl exec -i deploy/api -- python -m app.add_to_library --title "NIST AI 100-1" < nist.pdf

A public deployment takes uploads only from accounts (ALLOW_GUEST_UPLOADS=false), and an
account's uploads are private to it, so the shared collection is loaded this way: through the
cluster's own access control, never through the public API. `scripts/load_corpus.py --exec`
runs it once per corpus PDF. Prints one line of JSON: {"id": ..., "new": true or false}.
"""

import argparse
import asyncio
import json
import sys

from app.api.documents import AlreadyUploaded, store_pdf
from app.config import get_settings
from app.db import open_pool


async def add(content: bytes, file_name: str, title: str | None) -> dict:
    pool = await open_pool(get_settings().database_url, max_size=1)
    try:
        doc = await store_pdf(pool, content, file_name, title, owner=None)
        return {"id": doc.id, "new": True}
    except AlreadyUploaded as e:
        return {"id": e.document_id, "new": False}
    finally:
        await pool.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Add a PDF from stdin to the shared collection.")
    parser.add_argument("--title", default=None)
    parser.add_argument("--file-name", default="document.pdf")
    args = parser.parse_args()
    content = sys.stdin.buffer.read()
    if not content.startswith(b"%PDF-"):
        print("stdin is not a PDF", file=sys.stderr)
        return 1
    print(json.dumps(asyncio.run(add(content, args.file_name, args.title))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
