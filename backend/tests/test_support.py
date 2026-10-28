"""Claim support: which pieces are judged, and how judge replies are read."""

import json

from app.agent.support import claims, request, summary, verdicts

ANSWER = {
    "segments": [
        {"text": "The memo sets two deadlines. ", "citations": []},
        {"text": "Strategies are due in 180 days.", "citations": [1]},
        {"text": " Plans follow the same timeline.", "citations": [1, 2]},
        {"text": "   ", "citations": [2]},
    ],
    "citations": [
        {"number": 1, "cited_text": "Within 180 days, each agency must develop an AI Strategy."},
        {"number": 2, "cited_text": "Within 180 days, each agency must submit a plan."},
    ],
}


def test_only_cited_pieces_with_text_are_claims_and_they_carry_context():
    items = claims(ANSWER)
    assert [c["text"] for c in items] == [
        "Strategies are due in 180 days.",
        "Plans follow the same timeline.",
    ]
    assert items[0]["context"] == "The memo sets two deadlines."
    assert len(items[1]["quotes"]) == 2
    sent = json.loads(request(items)[0]["content"])
    assert sent[1] == {
        "claim": 2,
        "text": "Plans follow the same timeline.",
        "context": "The memo sets two deadlines. Strategies are due in 180 days.",
        "passages": [c["cited_text"] for c in ANSWER["citations"]],
    }


def test_well_formed_verdicts_are_kept():
    items = claims(ANSWER)
    reply = json.dumps(
        {
            "checks": [
                {"claim": 1, "verdict": "supported", "reason": "stated"},
                {"claim": 2, "verdict": "partly", "reason": "timeline not stated for plans"},
            ]
        }
    )
    out = verdicts(items, reply)
    assert [c["verdict"] for c in out] == ["supported", "partly"]
    assert out[1]["citations"] == [1, 2]
    assert summary(out)["partly"] == 1


def test_a_bad_reply_never_counts_as_a_judgement():
    items = claims(ANSWER)
    for reply in (None, "not json", json.dumps({"checks": [{"claim": 1, "verdict": "yes"}]})):
        assert {c["verdict"] for c in verdicts(items, reply)} == {"not_checked"}
    # A judgement for one claim does not cover another.
    one = json.dumps({"checks": [{"claim": 2, "verdict": "supported", "reason": "ok"}]})
    assert [c["verdict"] for c in verdicts(items, one)] == ["not_checked", "supported"]
