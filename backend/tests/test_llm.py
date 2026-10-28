from app.llm import thinking_param


def test_thinking_off_uses_each_model_s_own_setting():
    assert thinking_param("claude-haiku-5-5", "disabled") == {"type": "disabled"}
    assert thinking_param("claude-sonnet-5-5", "disabled") == {"type": "between_tools"}
    assert thinking_param("claude-sonnet-5-5", "adaptive") == {"type": "adaptive"}
