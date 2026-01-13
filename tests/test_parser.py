"""Tests for src/rag/parser.py"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.rag.parser import PDFTableParser


@pytest.fixture
def parser():
    return PDFTableParser()


def test_parser_initialization(parser):
    """Test parser initialization"""
    assert parser is not None


def test_parse_with_text_only(parser):
    """Test parsing PDF with text only"""
    mock_page = Mock()
    mock_page.extract_text.return_value = "Test content"
    mock_page.extract_tables.return_value = []

    mock_pdf = Mock()
    mock_pdf.pages = [mock_page]
    mock_pdf.__enter__ = Mock(return_value=mock_pdf)
    mock_pdf.__exit__ = Mock(return_value=False)

    with patch('pdfplumber.open', return_value=mock_pdf):
        result = parser.parse("test.pdf")

    assert "Test content" in result
    assert "## Page 1" in result


def test_parse_with_tables(parser):
    """Test parsing PDF with tables"""
    mock_page = Mock()
    mock_page.extract_text.return_value = "Text content"
    mock_page.extract_tables.return_value = [
        [["Header1", "Header2"], ["Cell1", "Cell2"]]
    ]

    mock_pdf = Mock()
    mock_pdf.pages = [mock_page]
    mock_pdf.__enter__ = Mock(return_value=mock_pdf)
    mock_pdf.__exit__ = Mock(return_value=False)

    with patch('pdfplumber.open', return_value=mock_pdf):
        result = parser.parse("test.pdf")

    assert "### Tables" in result
    assert "Header1" in result
    assert "Header2" in result
    assert "---" in result  # Markdown table separator


def test_parse_multiple_pages(parser):
    """Test parsing PDF with multiple pages"""
    mock_page1 = Mock()
    mock_page1.extract_text.return_value = "Page 1 content"
    mock_page1.extract_tables.return_value = []

    mock_page2 = Mock()
    mock_page2.extract_text.return_value = "Page 2 content"
    mock_page2.extract_tables.return_value = []

    mock_pdf = Mock()
    mock_pdf.pages = [mock_page1, mock_page2]
    mock_pdf.__enter__ = Mock(return_value=mock_pdf)
    mock_pdf.__exit__ = Mock(return_value=False)

    with patch('pdfplumber.open', return_value=mock_pdf):
        result = parser.parse("test.pdf")

    assert "## Page 1" in result
    assert "## Page 2" in result
    assert "Page 1 content" in result
    assert "Page 2 content" in result


def test_parse_error_handling(parser):
    """Test parse error handling"""
    with patch('pdfplumber.open', side_effect=Exception("PDF error")):
        result = parser.parse("bad.pdf")

    assert result == ""


def test_table_to_markdown_simple(parser):
    """Test simple table to markdown conversion"""
    table = [
        ["Name", "Age"],
        ["Alice", "30"],
        ["Bob", "25"]
    ]

    result = parser._table_to_markdown(table)

    assert "| Name | Age |" in result
    assert "| --- | --- |" in result
    assert "| Alice | 30 |" in result
    assert "| Bob | 25 |" in result


def test_table_to_markdown_with_none(parser):
    """Test table with None values"""
    table = [
        ["Col1", "Col2"],
        ["Value", None],
        [None, "Value2"]
    ]

    result = parser._table_to_markdown(table)

    # None should be converted to empty string
    assert "|  |" in result or "| Value |  |" in result


def test_table_to_markdown_with_newlines(parser):
    """Test table with newlines in cells"""
    table = [
        ["Header"],
        ["Line1\nLine2"]
    ]

    result = parser._table_to_markdown(table)

    # Newlines should be converted to <br>
    assert "<br>" in result
    assert "\n\n" not in result  # Should not have double newlines from the cell


def test_table_to_markdown_empty_table(parser):
    """Test empty table"""
    result = parser._table_to_markdown([])

    assert result == ""


def test_table_to_markdown_row_length_mismatch(parser):
    """Test table with mismatched row lengths"""
    table = [
        ["Col1", "Col2", "Col3"],
        ["A", "B"],  # Shorter row
        ["X", "Y", "Z", "W"]  # Longer row
    ]

    result = parser._table_to_markdown(table)

    # Should handle gracefully
    assert "| Col1 | Col2 | Col3 |" in result
    lines = result.split("\n")
    # Each data row should have same number of columns as header
    for line in lines[2:]:  # Skip header and separator
        if line.strip():
            assert line.count("|") == 4  # 3 cols + 2 edges


def test_parse_no_text(parser):
    """Test parsing page with no text"""
    mock_page = Mock()
    mock_page.extract_text.return_value = None
    mock_page.extract_tables.return_value = []

    mock_pdf = Mock()
    mock_pdf.pages = [mock_page]
    mock_pdf.__enter__ = Mock(return_value=mock_pdf)
    mock_pdf.__exit__ = Mock(return_value=False)

    with patch('pdfplumber.open', return_value=mock_pdf):
        result = parser.parse("test.pdf")

    # Should still have page header
    assert "## Page 1" in result
