"""Tests for src/rag/integrated_pipeline.py"""
import pytest
import json
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Mock mathesis_core before import
sys.modules['mathesis_core'] = Mock()
sys.modules['mathesis_core.db'] = Mock()
sys.modules['mathesis_core.db.hierarchical_chroma'] = Mock()
sys.modules['mathesis_core.llm'] = Mock()
sys.modules['mathesis_core.llm.clients'] = Mock()


@pytest.fixture
def mock_dependencies():
    """Mock all external dependencies"""
    with patch('src.rag.integrated_pipeline.HierarchicalChromaStore') as mock_store, \
         patch('src.rag.integrated_pipeline.OllamaClient') as mock_ollama, \
         patch('src.rag.integrated_pipeline.PDFTableParser') as mock_parser, \
         patch('src.rag.integrated_pipeline.EnhancedJSONGenerator') as mock_json_gen:

        # Setup mock store
        mock_store_instance = Mock()
        mock_store_instance.add_hierarchical_document = Mock(return_value=5)
        mock_store_instance.query_with_parent_context = Mock(return_value={
            "matched_children": [],
            "parent_contexts": []
        })
        mock_store.return_value = mock_store_instance

        # Setup mock ollama
        mock_ollama_instance = Mock()
        mock_ollama_instance.generate = Mock(return_value='{"answer": "Test answer", "key_facts": [], "confidence": 0.9}')
        mock_ollama.return_value = mock_ollama_instance

        # Setup mock parser
        mock_parser_instance = Mock()
        mock_parser_instance.parse = Mock(return_value="# Test Content\nSome content")
        mock_parser.return_value = mock_parser_instance

        # Setup mock JSON generator
        mock_json_gen_instance = Mock()
        mock_json_gen_instance.generate_from_markdown = Mock(return_value={
            "document_metadata": {
                "document_id": "doc_TEST_2025_1_math_1",
                "school_code": "TEST",
                "section_count": 2,
                "table_count": 1
            },
            "sections": [
                {"section_id": "sec_001", "tables": []}
            ],
            "rag_optimization": {}
        })
        mock_json_gen.return_value = mock_json_gen_instance

        yield {
            'store': mock_store_instance,
            'ollama': mock_ollama_instance,
            'parser': mock_parser_instance,
            'json_gen': mock_json_gen_instance
        }


def test_pipeline_initialization(mock_dependencies):
    """Test pipeline initialization"""
    from src.rag.integrated_pipeline import IntegratedRAGPipeline

    pipeline = IntegratedRAGPipeline()

    assert pipeline.ollama is not None
    assert pipeline.vector_store is not None
    assert pipeline.pdf_parser is not None
    assert pipeline.json_generator is not None
    assert isinstance(pipeline.json_storage, dict)


def test_ingest_pdf_success(mock_dependencies, tmp_path):
    """Test successful PDF ingestion"""
    from src.rag.integrated_pipeline import IntegratedRAGPipeline

    pipeline = IntegratedRAGPipeline()

    metadata = {
        "school_code": "TEST",
        "school_name": "Test School",
        "year": "2025",
        "grade": "1",
        "subject": "math"
    }

    with patch('pathlib.Path.mkdir'), \
         patch('builtins.open', create=True) as mock_open:
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        result = pipeline.ingest_pdf("test.pdf", metadata)

    assert "document_id" in result
    assert result["document_id"] == "doc_TEST_2025_1_math_1"
    assert "enhanced_json_path" in result
    assert result["chunks_added"] == 5

    mock_dependencies['parser'].parse.assert_called_once_with("test.pdf")
    mock_dependencies['json_gen'].generate_from_markdown.assert_called_once()
    mock_dependencies['store'].add_hierarchical_document.assert_called_once()


def test_ingest_pdf_empty_content(mock_dependencies):
    """Test PDF ingestion with empty content"""
    from src.rag.integrated_pipeline import IntegratedRAGPipeline

    mock_dependencies['parser'].parse.return_value = ""

    pipeline = IntegratedRAGPipeline()

    with pytest.raises(ValueError, match="Failed to parse PDF"):
        pipeline.ingest_pdf("empty.pdf", {})


def test_ingest_pdf_stores_json(mock_dependencies):
    """Test that ingestion stores JSON in memory"""
    from src.rag.integrated_pipeline import IntegratedRAGPipeline

    pipeline = IntegratedRAGPipeline()

    metadata = {"school_code": "TEST", "school_name": "Test"}

    with patch('pathlib.Path.mkdir'), \
         patch('builtins.open', create=True):
        result = pipeline.ingest_pdf("test.pdf", metadata)

    doc_id = result["document_id"]
    assert doc_id in pipeline.json_storage
    assert pipeline.json_storage[doc_id]["document_metadata"]["document_id"] == doc_id


def test_query_success(mock_dependencies):
    """Test successful query"""
    from src.rag.integrated_pipeline import IntegratedRAGPipeline

    mock_dependencies['store'].query_with_parent_context.return_value = {
        "matched_children": [{"text": "child1"}],
        "parent_contexts": [
            {
                "text": "Parent context text",
                "metadata": {
                    "section_title": "Test Section",
                    "school_name": "Test School",
                    "year": "2025",
                    "document_id": "doc_123"
                }
            }
        ]
    }

    pipeline = IntegratedRAGPipeline()
    result = pipeline.query("What is the evaluation plan?")

    assert "answer" in result
    assert result["answer"] == "Test answer"
    assert "sources" in result
    assert len(result["sources"]) == 1
    assert result["sources"][0]["section_title"] == "Test Section"

    mock_dependencies['store'].query_with_parent_context.assert_called_once()
    mock_dependencies['ollama'].generate.assert_called_once()


def test_query_no_results(mock_dependencies):
    """Test query with no results"""
    from src.rag.integrated_pipeline import IntegratedRAGPipeline

    mock_dependencies['store'].query_with_parent_context.return_value = {
        "matched_children": [],
        "parent_contexts": []
    }

    pipeline = IntegratedRAGPipeline()
    result = pipeline.query("Unknown question")

    assert result["answer"] == "관련 정보를 찾을 수 없습니다."
    assert result["sources"] == []
    assert result["parent_contexts"] == []


def test_query_with_k_parameter(mock_dependencies):
    """Test query with custom k parameter"""
    from src.rag.integrated_pipeline import IntegratedRAGPipeline

    pipeline = IntegratedRAGPipeline()
    pipeline.query("Test", k=10)

    call_args = mock_dependencies['store'].query_with_parent_context.call_args
    assert call_args[1]["k"] == 10


def test_query_llm_json_decode_error(mock_dependencies):
    """Test query handling LLM JSON decode error"""
    from src.rag.integrated_pipeline import IntegratedRAGPipeline

    mock_dependencies['store'].query_with_parent_context.return_value = {
        "matched_children": [],
        "parent_contexts": [{"text": "Context", "metadata": {}}]
    }

    # Return invalid JSON
    mock_dependencies['ollama'].generate.return_value = "Not valid JSON"

    pipeline = IntegratedRAGPipeline()
    result = pipeline.query("Test")

    assert "answer" in result
    assert result["answer"] == "Not valid JSON"
    assert result["confidence"] == 0.5


def test_query_llm_exception(mock_dependencies):
    """Test query handling LLM exception"""
    from src.rag.integrated_pipeline import IntegratedRAGPipeline

    mock_dependencies['store'].query_with_parent_context.return_value = {
        "matched_children": [],
        "parent_contexts": [{"text": "Context", "metadata": {}}]
    }

    mock_dependencies['ollama'].generate.side_effect = Exception("LLM Error")

    pipeline = IntegratedRAGPipeline()
    result = pipeline.query("Test")

    assert "오류가 발생했습니다" in result["answer"]
    assert result["confidence"] == 0.0


def test_export_json_existing(mock_dependencies):
    """Test exporting existing document JSON"""
    from src.rag.integrated_pipeline import IntegratedRAGPipeline

    pipeline = IntegratedRAGPipeline()
    pipeline.json_storage["doc_123"] = {"test": "data"}

    result = pipeline.export_json("doc_123")

    assert result == {"test": "data"}


def test_export_json_nonexistent(mock_dependencies):
    """Test exporting non-existent document JSON"""
    from src.rag.integrated_pipeline import IntegratedRAGPipeline

    pipeline = IntegratedRAGPipeline()

    result = pipeline.export_json("nonexistent")

    assert result is None


def test_export_all_jsons(mock_dependencies):
    """Test exporting all JSONs"""
    from src.rag.integrated_pipeline import IntegratedRAGPipeline

    pipeline = IntegratedRAGPipeline()
    pipeline.json_storage = {
        "doc_1": {"data": 1},
        "doc_2": {"data": 2}
    }

    result = pipeline.export_all_jsons()

    assert len(result) == 2
    assert "doc_1" in result
    assert "doc_2" in result


def test_list_documents_empty(mock_dependencies):
    """Test listing documents when empty"""
    from src.rag.integrated_pipeline import IntegratedRAGPipeline

    pipeline = IntegratedRAGPipeline()

    result = pipeline.list_documents()

    assert result == []


def test_list_documents_with_data(mock_dependencies):
    """Test listing documents with data"""
    from src.rag.integrated_pipeline import IntegratedRAGPipeline

    pipeline = IntegratedRAGPipeline()
    pipeline.json_storage = {
        "doc_1": {
            "document_metadata": {
                "school_name": "School A",
                "year": "2025",
                "grade": "1",
                "subject": "math",
                "section_count": 5,
                "table_count": 3
            }
        },
        "doc_2": {
            "document_metadata": {
                "school_name": "School B",
                "year": "2024",
                "grade": "2",
                "subject": "science",
                "section_count": 7,
                "table_count": 2
            }
        }
    }

    result = pipeline.list_documents()

    assert len(result) == 2
    assert result[0]["document_id"] == "doc_1"
    assert result[0]["school_name"] == "School A"
    assert result[1]["document_id"] == "doc_2"


def test_pipeline_custom_parameters(mock_dependencies):
    """Test pipeline with custom initialization parameters"""
    from src.rag.integrated_pipeline import IntegratedRAGPipeline

    pipeline = IntegratedRAGPipeline(
        collection_name="custom_collection",
        ollama_base_url="http://custom:11434",
        ollama_model="custom-model",
        persist_dir="./custom_dir"
    )

    assert pipeline is not None


def test_query_formats_context_correctly(mock_dependencies):
    """Test that query formats context with sources"""
    from src.rag.integrated_pipeline import IntegratedRAGPipeline

    mock_dependencies['store'].query_with_parent_context.return_value = {
        "matched_children": [],
        "parent_contexts": [
            {
                "text": "Context 1",
                "metadata": {"section_title": "Section 1"}
            },
            {
                "text": "Context 2",
                "metadata": {"section_title": "Section 2"}
            }
        ]
    }

    pipeline = IntegratedRAGPipeline()
    pipeline.query("Test question")

    # Check that generate was called with formatted context
    call_args = mock_dependencies['ollama'].generate.call_args
    prompt = call_args[1]["prompt"]
    assert "[출처: Section 1]" in prompt
    assert "[출처: Section 2]" in prompt


def test_ingest_pdf_creates_output_directory(mock_dependencies):
    """Test that ingest creates output directory"""
    from src.rag.integrated_pipeline import IntegratedRAGPipeline

    pipeline = IntegratedRAGPipeline()

    with patch('pathlib.Path.mkdir') as mock_mkdir, \
         patch('builtins.open', create=True):
        pipeline.ingest_pdf("test.pdf", {"school_code": "TEST"})

        mock_mkdir.assert_called_once_with(exist_ok=True)


def test_query_includes_parent_context_preview(mock_dependencies):
    """Test that query result includes parent context preview"""
    from src.rag.integrated_pipeline import IntegratedRAGPipeline

    long_text = "A" * 300  # Text longer than 200 chars

    mock_dependencies['store'].query_with_parent_context.return_value = {
        "matched_children": [],
        "parent_contexts": [
            {"text": long_text, "metadata": {}}
        ]
    }

    pipeline = IntegratedRAGPipeline()
    result = pipeline.query("Test")

    assert "parent_contexts" in result
    assert len(result["parent_contexts"][0]) <= 203  # 200 + "..."
    assert result["parent_contexts"][0].endswith("...")
