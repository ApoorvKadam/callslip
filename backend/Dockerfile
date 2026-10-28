# syntax=docker/dockerfile:1
# One image for both the API (uvicorn) and the ingestion worker (python -m app.worker).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    FASTEMBED_CACHE_PATH=/opt/models \
    PATH="/opt/venv/bin:$PATH"

COPY --from=ghcr.io/astral-sh/uv:0.7.22 /uv /usr/local/bin/uv

WORKDIR /app

# Dependencies first, from the lock file, so code changes do not reinstall them.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --no-install-project

# Bake the embedding model into the image: nothing is downloaded at runtime.
RUN python -c "from fastembed import TextEmbedding; TextEmbedding('BAAI/bge-small-en-v1.5', cache_dir='/opt/models')"

COPY app ./app

RUN useradd --create-home --uid 10001 app && chown -R app:app /opt/models
USER app

EXPOSE 8000
# The standard asyncio loop: with uvloop, a Redis connect that times out during a DNS lookup
# leaves an unretrieved future and an ERROR log line (MagicStack/uvloop issue 437).
# X-Forwarded-For is trusted only from the proxies named in FORWARDED_ALLOW_IPS (Compose and the
# Kubernetes manifests set it); the client address counts failed sign-ins.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--loop", "asyncio"]
