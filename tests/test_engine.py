"""Tests for src/rag/engine.py"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import sys

# Mock mathesis_core before import
sys.modules['mathesis_core'] = Mock()
sys.modules['mathesis_core.db'] = Mock()
sys.modules['mathesis_core.db.chroma'] = Mock()
sys.modules['mathesis_core.llm'] = Mock()
sys.modules['mathesis_core.llm.clients'] = Mock()


@pytest.fixture
def mock_components():
    """Mock all external dependencies"""
    with patch('src.rag.engine.ChromaHybridStore') as mock_store, \
         patch('src.rag.engine.OllamaClient') as mock_ollama, \
         patch('src.rag.engine.PDFTableParser') as mock_parser, \
         patch('src.rag.engine.SectionChunker') as mock_chunker:

        mock_store_instance = Mock()
        mock_store_instance.add_documents = Mock()
        mock_store_instance.hybrid_search = Mock(return_value=[])
        mock_store.return_value = mock_store_instance

        mock_ollama_instance = Mock()
        mock_ollama_instance.generate = Mock(return_value='{"answer": "test"}')
        mock_ollama.return_value = mock_ollama_instance

        mock_parser_instance = Mock()
        mock_parser_instance.parse = Mock(return_value="Test content\n## Header\nMore content")
        mock_parser.return_value = mock_parser_instance

        mock_chunker_instance = Mock()
        mock_chunker_instance.chunk = Mock(return_value=[
            {"text": "chunk1", "metadata": {"header": "H1"}},
            {"text": "chunk2", "metadata": {"header": "H2"}}
        ])
        mock_chunker.return_value = mock_chunker_instance

        yield {
            'store': mock_store_instance,
            'ollama': mock_ollama_instance,
            'parser': mock_parser_instance,
            'chunker': mock_chunker_instance
        }


def test_engine_initialization(mock_components):
    """Test RAGEngine initialization"""
    from src.rag.engine import RAGEngine

    engine = RAGEngine("test_collection")

    assert engine is not None
    assert engine.parser is not None
    assert engine.chunker is not None


def test_ingest_file_success(mock_components):
    """Test successful file ingestion"""
    from src.rag.engine import RAGEngine

    engine = RAGEngine()
    count = engine.ingest_file("test.pdf", {"school": "Test"})

    assert count == 2  # 2 chunks
    mock_components['parser'].parse.assert_called_once_with("test.pdf")
    mock_components['chunker'].chunk.assert_called_once()
    mock_components['store'].add_documents.assert_called_once()


def test_ingest_file_empty_content(mock_components):
    """Test ingesting file with empty content"""
    from src.rag.engine import RAGEngine

    mock_components['parser'].parse.return_value = ""

    engine = RAGEngine()
    count = engine.ingest_file("empty.pdf")

    assert count == 0


def test_ingest_file_with_metadata(mock_components):
    """Test that metadata is properly merged"""
    from src.rag.engine import RAGEngine

    engine = RAGEngine()
    engine.ingest_file("test.pdf", {"school": "Test School", "year": 2025})

    # Check that add_documents was called with merged metadata
    call_args = mock_components['store'].add_documents.call_args
    metadatas = call_args[0][1]
    assert len(metadatas) == 2
    assert metadatas[0]["school"] == "Test School"
    assert metadatas[0]["header"] == "H1"


def test_query_success(mock_components):
    """Test successful query"""
    from src.rag.engine import RAGEngine

    mock_components['store'].hybrid_search.return_value = [
        {"text": "doc1", "metadata": {"header": "Test Header"}},
        {"text": "doc2", "metadata": {"header": "Test Header 2"}}
    ]

    engine = RAGEngine()
    result = engine.query("Test query")

    assert result is not None
    mock_components['store'].hybrid_search.assert_called_once()
    mock_components['ollama'].generate.assert_called_once()


def test_query_with_k_parameter(mock_components):
    """Test query with custom k parameter"""
    from src.rag.engine import RAGEngine

    mock_components['store'].hybrid_search.return_value = []

    engine = RAGEngine()
    engine.query("Test query", k=10)

    call_args = mock_components['store'].hybrid_search.call_args
    assert call_args[1]["k"] == 10
