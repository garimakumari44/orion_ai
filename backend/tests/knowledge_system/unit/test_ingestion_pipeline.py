"""
Tests for the ingestion processing pipeline.
"""

from unittest.mock import Mock

from app.knowledge_system.ingestion.pipeline import ProcessingPipeline
from app.knowledge_system.ingestion.models import Chunk, ProcessingDocument


def test_pipeline_uses_default_components():
    """
    Pipeline should create default components when none are provided.
    """

    pipeline = ProcessingPipeline()

    assert pipeline.splitter is not None
    assert pipeline.normalizer is not None
    assert pipeline.deduplicator is not None


def test_pipeline_accepts_custom_components():
    """
    Pipeline should use injected dependencies.
    """

    splitter = Mock()
    normalizer = Mock()
    deduplicator = Mock()

    pipeline = ProcessingPipeline(
        splitter=splitter,
        normalizer=normalizer,
        deduplicator=deduplicator,
    )

    assert pipeline.splitter is splitter
    assert pipeline.normalizer is normalizer
    assert pipeline.deduplicator is deduplicator


def test_duplicate_document_returns_empty_list():
    """
    Duplicate documents should not be split.
    """

    document = ProcessingDocument(
        id="doc-1",
        content="Hello world",
    )

    normalized = ProcessingDocument(
        id="doc-1",
        content="hello world",
    )

    splitter = Mock()
    normalizer = Mock()
    deduplicator = Mock()

    normalizer.normalize.return_value = normalized
    deduplicator.is_duplicate.return_value = True

    pipeline = ProcessingPipeline(
        splitter=splitter,
        normalizer=normalizer,
        deduplicator=deduplicator,
    )

    result = pipeline.process(document)

    assert result == []

    normalizer.normalize.assert_called_once_with(document)
    deduplicator.is_duplicate.assert_called_once_with(normalized)

    splitter.split.assert_not_called()


def test_non_duplicate_document_is_split():
    """
    Non-duplicate documents should be split into chunks.
    """

    document = ProcessingDocument(
        id="doc-1",
        content="Hello world",
    )

    normalized = ProcessingDocument(
        id="doc-1",
        content="hello world",
    )

    chunks = [
        Chunk(
            id="chunk-1",
            document_id="doc-1",
            text="hello",
            index=0,
        ),
        Chunk(
            id="chunk-2",
            document_id="doc-1",
            text="world",
            index=1,
        ),
    ]

    splitter = Mock()
    normalizer = Mock()
    deduplicator = Mock()

    normalizer.normalize.return_value = normalized
    deduplicator.is_duplicate.return_value = False
    splitter.split.return_value = chunks

    pipeline = ProcessingPipeline(
        splitter=splitter,
        normalizer=normalizer,
        deduplicator=deduplicator,
    )

    result = pipeline.process(document)

    assert result == chunks

    normalizer.normalize.assert_called_once_with(document)
    deduplicator.is_duplicate.assert_called_once_with(normalized)
    splitter.split.assert_called_once_with(normalized)


def test_pipeline_returns_chunks_from_splitter():
    """
    Pipeline should return exactly what the splitter produces.
    """

    document = ProcessingDocument(
        id="doc-42",
        content="Some content",
    )

    chunk = Chunk(
        id="chunk-1",
        document_id="doc-42",
        text="Some content",
        index=0,
    )

    splitter = Mock()
    normalizer = Mock()
    deduplicator = Mock()

    normalizer.normalize.return_value = document
    deduplicator.is_duplicate.return_value = False
    splitter.split.return_value = [chunk]

    pipeline = ProcessingPipeline(
        splitter=splitter,
        normalizer=normalizer,
        deduplicator=deduplicator,
    )

    result = pipeline.process(document)

    assert len(result) == 1
    assert result[0] == chunk