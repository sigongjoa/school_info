"""Tests for src/rag_service.py"""
import pytest
import json
import os
import sys
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Mock mathesis_core before imports
sys.modules['mathesis_core'] = Mock()
sys.modules['mathesis_core.db'] = Mock()
sys.modules['mathesis_core.db.chroma'] = Mock()
sys.modules['mathesis_core.llm'] = Mock()
sys.modules['mathesis_core.llm.clients'] = Mock()

from src.rag_service import SchoolRAGService
from src.models import SchoolData


@pytest.fixture
def mock_rag_engine():
    with patch('src.rag_service.RAGEngine') as mock_engine_class:
        mock_engine = Mock()
        mock_engine.ingest_file = Mock(return_value=5)
        mock_engine.query = Mock(return_value={
            "answer": "Test answer",
            "references": ["ref1", "ref2"]
        })
        mock_engine_class.return_value = mock_engine
        yield mock_engine


@pytest.fixture
def service(mock_rag_engine):
    return SchoolRAGService()


@pytest.mark.asyncio
async def test_service_initialization(mock_rag_engine):
    """Test service initialization"""
    service = SchoolRAGService()

    assert service.rag_engine is not None


@pytest.mark.asyncio
async def test_summarize_school_success(service, mock_rag_engine):
    """Test successful school summarization"""
    school = SchoolData(
        school_code="TEST001",
        school_name="Test School"
    )

    with patch('os.path.exists', return_value=True):
        result_str = await service.summarize_school(school, ["doc1.pdf", "doc2.pdf"])

    result = json.loads(result_str)
    assert "answer" in result
    assert result["answer"] == "Test answer"
    assert mock_rag_engine.ingest_file.call_count == 2


@pytest.mark.asyncio
async def test_summarize_school_no_documents(service, mock_rag_engine):
    """Test summarization with no valid documents"""
    school = SchoolData(school_code="TEST", school_name="Test")

    with patch('os.path.exists', return_value=False):
        result_str = await service.summarize_school(school, ["nonexistent.pdf"])

    result = json.loads(result_str)
    assert "error" in result or "No content" in result_str


@pytest.mark.asyncio
async def test_summarize_school_calls_query(service, mock_rag_engine):
    """Test that summarization calls query with correct parameters"""
    school = SchoolData(
        school_code="TEST",
        school_name="Test School"
    )

    with patch('os.path.exists', return_value=True):
        await service.summarize_school(school, ["test.pdf"])

    mock_rag_engine.query.assert_called_once()
    call_args = mock_rag_engine.query.call_args
    assert "Test School" in call_args[0][0]
    assert "2025학년도" in call_args[0][0]


@pytest.mark.asyncio
async def test_summarize_school_metadata(service, mock_rag_engine):
    """Test that ingest includes correct metadata"""
    school = SchoolData(
        school_code="TEST",
        school_name="Demo School"
    )

    with patch('os.path.exists', return_value=True):
        await service.summarize_school(school, ["doc.pdf"])

    mock_rag_engine.ingest_file.assert_called_once()
    call_args = mock_rag_engine.ingest_file.call_args
    metadata = call_args[1]["metadata"]
    assert metadata["school_name"] == "Demo School"
    assert metadata["year"] == "2025"


@pytest.mark.asyncio
async def test_summarize_school_returns_json_string(service, mock_rag_engine):
    """Test that result is a valid JSON string"""
    school = SchoolData(school_code="TEST", school_name="Test")

    with patch('os.path.exists', return_value=True):
        result = await service.summarize_school(school, ["test.pdf"])

    # Should be valid JSON
    parsed = json.loads(result)
    assert isinstance(parsed, dict)


@pytest.mark.asyncio
async def test_summarize_school_no_chunks_ingested(service, mock_rag_engine):
    """Test when no chunks are ingested"""
    mock_rag_engine.ingest_file.return_value = 0

    school = SchoolData(school_code="TEST", school_name="Test")

    with patch('os.path.exists', return_value=True):
        result_str = await service.summarize_school(school, ["empty.pdf"])

    result = json.loads(result_str)
    assert "error" in result
    assert "No content indexed" in result["error"]
