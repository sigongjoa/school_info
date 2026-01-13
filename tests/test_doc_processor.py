"""Tests for src/doc_processor.py"""
import pytest
import tempfile
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from src.doc_processor import DocumentProcessor


@pytest.fixture
def processor():
    return DocumentProcessor()


def test_extract_text_unsupported_format(processor):
    """Test extraction of unsupported format"""
    result = processor.extract_text("test.docx")
    assert "[Unsupported Format: .docx]" in result


def test_extract_pdf_success(processor):
    """Test successful PDF extraction"""
    mock_pypdf = MagicMock()
    mock_page = Mock()
    mock_page.extract_text.return_value = "Test content"
    mock_reader = Mock()
    mock_reader.pages = [mock_page]
    mock_pypdf.PdfReader.return_value = mock_reader

    sys.modules['pypdf'] = mock_pypdf

    try:
        result = processor.extract_text("test.pdf")
        assert "Test content" in result
    finally:
        if 'pypdf' in sys.modules:
            del sys.modules['pypdf']


def test_extract_pdf_import_error(processor):
    """Test PDF extraction when pypdf is not installed"""
    # Remove pypdf from sys.modules if it exists
    orig_pypdf = sys.modules.pop('pypdf', None)

    # Mock the import to raise ImportError
    def mock_import(name, *args):
        if name == 'pypdf':
            raise ImportError("No module named 'pypdf'")
        return __import__(name, *args)

    with patch('builtins.__import__', side_effect=mock_import):
        result = processor._extract_pdf("test.pdf")
        assert "[Error: pypdf library missing]" in result

    # Restore
    if orig_pypdf:
        sys.modules['pypdf'] = orig_pypdf


def test_extract_pdf_exception(processor):
    """Test PDF extraction error handling"""
    mock_pypdf = MagicMock()
    mock_pypdf.PdfReader.side_effect = Exception("PDF error")

    sys.modules['pypdf'] = mock_pypdf

    try:
        result = processor._extract_pdf("test.pdf")
        assert "[Error processing PDF:" in result
    finally:
        if 'pypdf' in sys.modules:
            del sys.modules['pypdf']


def test_extract_hwp_success(processor):
    """Test successful HWP extraction"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.hwp', delete=False, encoding='utf-8') as f:
        f.write("HWP test content")
        temp_path = f.name

    try:
        result = processor.extract_text(temp_path)
        assert "HWP test content" in result
    finally:
        os.unlink(temp_path)


def test_extract_hwp_error(processor):
    """Test HWP extraction error handling"""
    result = processor._extract_hwp("/nonexistent/file.hwp")
    assert "[Error processing HWP:" in result


def test_extract_hwpx_format(processor):
    """Test HWPX format is recognized"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.hwpx', delete=False, encoding='utf-8') as f:
        f.write("HWPX content")
        temp_path = f.name

    try:
        result = processor.extract_text(temp_path)
        assert "HWPX content" in result
    finally:
        os.unlink(temp_path)


def test_extract_pdf_multiple_pages(processor):
    """Test PDF extraction with multiple pages"""
    mock_pypdf = MagicMock()
    mock_page1 = Mock()
    mock_page1.extract_text.return_value = "Page 1"
    mock_page2 = Mock()
    mock_page2.extract_text.return_value = "Page 2"
    mock_reader = Mock()
    mock_reader.pages = [mock_page1, mock_page2]
    mock_pypdf.PdfReader.return_value = mock_reader

    sys.modules['pypdf'] = mock_pypdf

    try:
        result = processor._extract_pdf("test.pdf")
        assert "Page 1" in result
        assert "Page 2" in result
    finally:
        if 'pypdf' in sys.modules:
            del sys.modules['pypdf']


def test_extract_pdf_empty_page(processor):
    """Test PDF extraction with empty page"""
    mock_pypdf = MagicMock()
    mock_page = Mock()
    mock_page.extract_text.return_value = None
    mock_reader = Mock()
    mock_reader.pages = [mock_page]
    mock_pypdf.PdfReader.return_value = mock_reader

    sys.modules['pypdf'] = mock_pypdf

    try:
        result = processor._extract_pdf("test.pdf")
        assert result == ""
    finally:
        if 'pypdf' in sys.modules:
            del sys.modules['pypdf']
