import pytest

from policy_rag.ingestion.tokenizer import TokenCounter


def test_token_counter_counts_text_tokens() -> None:
    counter = TokenCounter()

    assert counter.count("Employees may claim up to GBP 250.") == 9


def test_token_counter_returns_zero_for_empty_text() -> None:
    counter = TokenCounter()

    assert counter.count("") == 0


def test_token_counter_round_trip_preserves_text() -> None:
    counter = TokenCounter()
    text = "Remote-working requests require manager approval."

    tokens = counter.encode(text)
    decoded_text = counter.decode(tokens)

    assert decoded_text == text


def test_token_counter_rejects_unknown_encoding() -> None:
    with pytest.raises(ValueError, match="Unknown encoding"):
        TokenCounter("invalid-encoding")
