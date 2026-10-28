"""Local text embeddings (fastembed, ONNX on CPU) and the matching token counter.

The model files are downloaded into the image at build time, so nothing is fetched at runtime
(`local_files_only`). Calls are CPU-bound: async callers run them with `asyncio.to_thread`.
"""

from pathlib import Path

import numpy as np
from fastembed import TextEmbedding
from tokenizers import Tokenizer


class Embedder:
    def __init__(self, model_name: str, cache_dir: str, threads: int, batch_size: int) -> None:
        self.model_name = model_name
        self.batch_size = batch_size
        self._model = TextEmbedding(
            model_name, cache_dir=cache_dir, threads=threads, local_files_only=True
        )
        self._tokenizer = _load_tokenizer(cache_dir, model_name)

    def count_tokens(self, text: str) -> int:
        return len(self._tokenizer.encode(text, add_special_tokens=False).ids)

    def embed_passages(self, texts: list[str]) -> list[np.ndarray]:
        return list(self._model.passage_embed(texts, batch_size=self.batch_size))

    def embed_query(self, text: str) -> np.ndarray:
        return next(iter(self._model.query_embed(text)))


def _load_tokenizer(cache_dir: str, model_name: str) -> Tokenizer:
    """Load the model's own tokenizer.json from the fastembed cache, without truncation."""
    short_name = model_name.split("/")[-1].lower()
    candidates = [
        p for p in Path(cache_dir).rglob("tokenizer.json") if short_name in str(p).lower()
    ]
    if len(candidates) != 1:
        raise RuntimeError(
            f"expected one tokenizer.json for {model_name} in {cache_dir}, found {candidates}"
        )
    tokenizer = Tokenizer.from_file(str(candidates[0]))
    tokenizer.no_truncation()
    tokenizer.no_padding()
    return tokenizer
