from unittest.mock import patch


class DummyChunk:
    def __init__(self, idx):
        self.id = str(idx)
        self.text = f"chunk {idx}"


@patch("app.adaptive_retrieval.manager.retriever_manager.MultiSourceRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.MemoryRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.TemporalRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.MetadataRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.GraphRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.HybridRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.BM25Retriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.KeywordRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.SparseRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.DenseRetriever")
def test_basic_pipeline(
    mock_dense,
    mock_sparse,
    mock_keyword,
    mock_bm25,
    mock_hybrid,
    mock_graph,
    mock_metadata,
    mock_temporal,
    mock_memory,
    mock_multi_source,
):
    chunk = DummyChunk(1)

    memory = mock_memory.return_value
    hybrid = mock_hybrid.return_value
    merger = mock_multi_source.return_value

    memory.retrieve.return_value = None
    hybrid.retrieve.return_value = [chunk]
    merger.merge.return_value = [chunk]

    from app.adaptive_retrieval.retrievers.manager import RetrievalManager

    manager = RetrievalManager()

    result = manager.retrieve("python", top_k=5)

    memory.retrieve.assert_called_once_with("python")

    hybrid.retrieve.assert_called_once_with(
        "python",
        top_k=5,
    )

    merger.merge.assert_called_once()

    memory.add.assert_called_once_with(
        "python",
        [chunk],
    )

    assert result == [chunk]


@patch("app.adaptive_retrieval.manager.retriever_manager.MultiSourceRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.MemoryRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.TemporalRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.MetadataRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.GraphRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.HybridRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.BM25Retriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.KeywordRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.SparseRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.DenseRetriever")
def test_optional_retrievers(
    mock_dense,
    mock_sparse,
    mock_keyword,
    mock_bm25,
    mock_hybrid,
    mock_graph,
    mock_metadata,
    mock_temporal,
    mock_memory,
    mock_multi_source,
):
    chunk = DummyChunk(2)

    mock_memory.return_value.retrieve.return_value = None

    mock_hybrid.return_value.retrieve.return_value = [chunk]
    mock_graph.return_value.retrieve.return_value = [chunk]
    mock_metadata.return_value.retrieve.return_value = [chunk]
    mock_temporal.return_value.retrieve.return_value = [chunk]

    mock_multi_source.return_value.merge.return_value = [chunk]

    from app.adaptive_retrieval.retrievers.manager  import RetrievalManager

    manager = RetrievalManager()

    manager.retrieve(
        "ai",
        use_graph=True,
        use_metadata=True,
        use_temporal=True,
    )

    mock_graph.return_value.retrieve.assert_called_once()
    mock_metadata.return_value.retrieve.assert_called_once()
    mock_temporal.return_value.retrieve.assert_called_once()


@patch("app.adaptive_retrieval.manager.retriever_manager.MultiSourceRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.MemoryRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.TemporalRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.MetadataRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.GraphRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.HybridRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.BM25Retriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.KeywordRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.SparseRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.DenseRetriever")
def test_memory_hit(
    mock_dense,
    mock_sparse,
    mock_keyword,
    mock_bm25,
    mock_hybrid,
    mock_graph,
    mock_metadata,
    mock_temporal,
    mock_memory,
    mock_multi_source,
):
    chunk = DummyChunk(3)

    mock_memory.return_value.retrieve.return_value = [chunk]
    mock_hybrid.return_value.retrieve.return_value = [chunk]
    mock_multi_source.return_value.merge.return_value = [chunk]

    from app.adaptive_retrieval.retrievers.manager import RetrievalManager

    manager = RetrievalManager()

    manager.retrieve("cached")

    mock_memory.return_value.retrieve.assert_called_once()


@patch("app.adaptive_retrieval.manager.retriever_manager.MultiSourceRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.MemoryRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.TemporalRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.MetadataRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.GraphRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.HybridRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.BM25Retriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.KeywordRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.SparseRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.DenseRetriever")
def test_top_k(
    mock_dense,
    mock_sparse,
    mock_keyword,
    mock_bm25,
    mock_hybrid,
    mock_graph,
    mock_metadata,
    mock_temporal,
    mock_memory,
    mock_multi_source,
):
    docs = [DummyChunk(i) for i in range(20)]

    mock_memory.return_value.retrieve.return_value = None
    mock_hybrid.return_value.retrieve.return_value = docs
    mock_multi_source.return_value.merge.return_value = docs

    from app.adaptive_retrieval.retrievers.manager import RetrievalManager

    manager = RetrievalManager()

    result = manager.retrieve(
        "llm",
        top_k=5,
    )

    assert len(result) == 5


@patch("app.adaptive_retrieval.manager.retriever_manager.MemoryRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.MultiSourceRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.TemporalRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.MetadataRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.GraphRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.HybridRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.BM25Retriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.KeywordRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.SparseRetriever")
@patch("app.adaptive_retrieval.manager.retriever_manager.DenseRetriever")
def test_clear_memory(
    mock_dense,
    mock_sparse,
    mock_keyword,
    mock_bm25,
    mock_hybrid,
    mock_graph,
    mock_metadata,
    mock_temporal,
    mock_multi_source,
    mock_memory,
):
    from app.adaptive_retrieval.retrievers.manager import RetrievalManager

    manager = RetrievalManager()

    manager.clear_memory()

    mock_memory.return_value.clear.assert_called_once()