from collections.abc import Sequence

from policy_rag.embeddings import EmbeddingProvider, EmbeddingVector


class StubEmbeddingProvider:
    dimensions = 3

    def embed(self, texts: Sequence[str], /) -> tuple[EmbeddingVector, ...]:
        return tuple((float(index), 0.0, 1.0) for index, _ in enumerate(texts))


def embed_with(provider: EmbeddingProvider, texts: Sequence[str]) -> tuple[EmbeddingVector, ...]:
    return provider.embed(texts)


def test_provider_contract_preserves_input_order() -> None:
    provider = StubEmbeddingProvider()

    vectors = embed_with(provider, ("first", "second"))

    assert provider.dimensions == 3
    assert vectors == (
        (0.0, 0.0, 1.0),
        (1.0, 0.0, 1.0),
    )
