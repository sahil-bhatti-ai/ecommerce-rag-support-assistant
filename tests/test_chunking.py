from app.services.chunking import split_text_into_chunks


def test_chunking_preserves_metadata() -> None:
    text = "Refund policy. " * 300
    chunks = split_text_into_chunks(text, metadata={"document_id": "doc-1", "filename": "faq.txt"})

    assert len(chunks) >= 2
    assert chunks[0].metadata["document_id"] == "doc-1"
    assert chunks[0].metadata["filename"] == "faq.txt"
