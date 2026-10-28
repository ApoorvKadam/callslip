"""Split one page of text into overlapping chunks measured in embedding-model tokens.

Chunks never cross a page boundary, so every chunk (and every citation of it) belongs to exactly
one physical page. Boundaries fall between sentences where possible; a sentence longer than the
budget is split between words.
"""

import re
from collections.abc import Callable

# Split after sentence-ending punctuation followed by whitespace.
_SENTENCE_END = re.compile(r"(?<=[.!?;])\s+")

CountTokens = Callable[[str], int]


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_END.split(text) if s.strip()]


def _split_long(sentence: str, count_tokens: CountTokens, max_tokens: int) -> list[str]:
    """Split one over-long sentence between words into pieces within the budget."""
    pieces: list[str] = []
    current: list[str] = []
    for word in sentence.split(" "):
        if current and count_tokens(" ".join([*current, word])) > max_tokens:
            pieces.append(" ".join(current))
            current = []
        current.append(word)
    if current:
        pieces.append(" ".join(current))
    return pieces


def chunk_page(
    text: str, count_tokens: CountTokens, max_tokens: int, overlap_tokens: int
) -> list[str]:
    pieces: list[str] = []
    for sentence in split_sentences(text):
        if count_tokens(sentence) <= max_tokens:
            pieces.append(sentence)
        else:
            pieces.extend(_split_long(sentence, count_tokens, max_tokens))

    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0
    for piece in pieces:
        piece_tokens = count_tokens(piece)
        if current and current_tokens + piece_tokens > max_tokens:
            chunks.append(" ".join(current))
            # Carry the last sentences (up to the overlap budget) into the next chunk.
            carried: list[str] = []
            carried_tokens = 0
            for sentence in reversed(current):
                sentence_tokens = count_tokens(sentence)
                if carried_tokens + sentence_tokens > overlap_tokens:
                    break
                carried.insert(0, sentence)
                carried_tokens += sentence_tokens
            if carried_tokens + piece_tokens > max_tokens:
                carried, carried_tokens = [], 0
            current, current_tokens = carried, carried_tokens
        current.append(piece)
        current_tokens += piece_tokens
    if current:
        chunks.append(" ".join(current))
    return chunks
