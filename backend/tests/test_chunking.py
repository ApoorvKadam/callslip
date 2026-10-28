from app.ingest.chunking import chunk_page, split_sentences


def words(text: str) -> int:
    """A stand-in token counter for the pure chunking logic: one token per word."""
    return len(text.split())


def test_split_sentences_keeps_punctuation():
    assert split_sentences("One. Two? Three! Four; five") == [
        "One.",
        "Two?",
        "Three!",
        "Four;",
        "five",
    ]


def test_short_page_is_one_chunk():
    assert chunk_page("Alpha beta. Gamma delta.", words, 50, 10) == ["Alpha beta. Gamma delta."]


def test_chunks_respect_budget_and_overlap():
    sentences = [f"Sentence number {i} has six words." for i in range(20)]
    chunks = chunk_page(" ".join(sentences), words, 20, 6)
    assert len(chunks) > 1
    assert all(words(c) <= 20 for c in chunks)
    # Each chunk after the first starts with the last sentence of the previous chunk.
    for previous, current in zip(chunks, chunks[1:], strict=False):
        assert current.startswith(split_sentences(previous)[-1])
    # Nothing is lost: every sentence appears in some chunk.
    assert all(any(s in c for c in chunks) for s in sentences)


def test_overlong_sentence_is_split_between_words():
    sentence = " ".join(f"w{i}" for i in range(45)) + "."
    chunks = chunk_page(sentence, words, 10, 0)
    assert all(words(c) <= 10 for c in chunks)
    assert " ".join(chunks).split() == sentence.split()


def test_empty_page_has_no_chunks():
    assert chunk_page("", words, 50, 10) == []
