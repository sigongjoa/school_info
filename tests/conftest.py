"""
pytest fixtures for node6_school_info

Provides common fixtures for testing the School Info node.
"""
import pytest
import asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from httpx import AsyncClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for testing crawlers."""
    mock = AsyncMock()
    mock.get = AsyncMock()
    mock.post = AsyncMock()
    return mock


@pytest.fixture
def mock_chroma_client():
    """Mock ChromaDB client for testing RAG."""
    mock = MagicMock()
    mock.get_or_create_collection = MagicMock()
    mock.add = MagicMock()
    mock.query = MagicMock(return_value={
        "documents": [["Test document"]],
        "distances": [[0.1]],
        "metadatas": [[{"source": "test"}]]
    })
    return mock


@pytest.fixture
def sample_school():
    """Sample school data for testing."""
    return {
        "id": "SCH_001",
        "name": "Test High School",
        "address": "123 Test Street",
        "region": "Seoul",
        "type": "high_school"
    }


@pytest.fixture
def sample_school_document():
    """Sample school document for RAG testing."""
    return {
        "id": "doc_001",
        "school_id": "SCH_001",
        "title": "2024 Curriculum Guide",
        "content": "This is a test curriculum document.",
        "document_type": "curriculum",
        "source_url": "https://example.com/curriculum.pdf"
    }


@pytest.fixture
def sample_crawl_result():
    """Sample crawl result data."""
    return {
        "url": "https://example.com/page",
        "title": "Test Page",
        "content": "Test content from crawled page",
        "links": ["https://example.com/link1", "https://example.com/link2"],
        "metadata": {
            "crawled_at": "2024-01-01T00:00:00",
            "status_code": 200
        }
    }


@pytest.fixture
def sample_rag_chunk():
    """Sample RAG chunk data."""
    return {
        "id": "chunk_001",
        "document_id": "doc_001",
        "content": "This is a chunk of text for RAG processing.",
        "embedding": [0.1] * 384,
        "metadata": {
            "chunk_index": 0,
            "source": "test_document.pdf"
        }
    }
