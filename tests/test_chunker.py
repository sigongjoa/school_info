"""Tests for src/rag/chunker.py"""
import pytest
from src.rag.chunker import SectionChunker


@pytest.fixture
def chunker():
    return SectionChunker()


def test_chunk_simple_headers(chunker):
    """Test chunking with simple headers"""
    text = """# Header 1
Content for header 1.

## Header 2
Content for header 2."""

    chunks = chunker.chunk(text)

    assert len(chunks) == 2
    assert chunks[0]["metadata"]["header"] == "Header 1"
    assert "Content for header 1" in chunks[0]["text"]
    assert chunks[1]["metadata"]["header"] == "Header 2"
    assert "Content for header 2" in chunks[1]["text"]


def test_chunk_no_headers(chunker):
    """Test chunking text without headers"""
    text = """This is plain text
without any headers.
Just multiple lines."""

    chunks = chunker.chunk(text)

    assert len(chunks) == 1
    assert chunks[0]["metadata"]["header"] == "Intro"
    assert "This is plain text" in chunks[0]["text"]


def test_chunk_empty_text(chunker):
    """Test chunking empty text"""
    chunks = chunker.chunk("")

    assert len(chunks) == 0


def test_chunk_multiple_header_levels(chunker):
    """Test chunking with multiple header levels"""
    text = """# Main Header
Main content.

## Sub Header
Sub content.

### Sub-sub Header
Sub-sub content."""

    chunks = chunker.chunk(text)

    assert len(chunks) == 3
    assert chunks[0]["metadata"]["header"] == "Main Header"
    assert chunks[1]["metadata"]["header"] == "Sub Header"
    assert chunks[2]["metadata"]["header"] == "Sub-sub Header"


def test_chunk_whitespace_handling(chunker):
    """Test that empty chunks are filtered out"""
    text = """# Header 1


## Header 2
Content."""

    chunks = chunker.chunk(text)

    # Empty section between Header 1 and Header 2 should not create a chunk
    assert all(chunk["text"].strip() for chunk in chunks)


def test_chunk_header_with_spaces(chunker):
    """Test headers with extra spaces"""
    text = """#   Header with spaces
Content."""

    chunks = chunker.chunk(text)

    assert len(chunks) == 1
    assert chunks[0]["metadata"]["header"] == "Header with spaces"


def test_chunk_includes_header_in_content(chunker):
    """Test that header line is included in chunk content"""
    text = """# Important Header
Following content."""

    chunks = chunker.chunk(text)

    assert len(chunks) == 1
    assert "# Important Header" in chunks[0]["text"]
    assert "Following content" in chunks[0]["text"]


def test_chunk_consecutive_headers(chunker):
    """Test consecutive headers without content between"""
    text = """# Header 1
## Header 2
Content for header 2."""

    chunks = chunker.chunk(text)

    # Header 1 with no content should still create a chunk with just the header
    assert len(chunks) == 2


def test_chunk_multiline_content(chunker):
    """Test chunking with multiline content"""
    text = """# Header
Line 1
Line 2
Line 3

## Next Header
More content."""

    chunks = chunker.chunk(text)

    assert len(chunks) == 2
    assert "Line 1" in chunks[0]["text"]
    assert "Line 2" in chunks[0]["text"]
    assert "Line 3" in chunks[0]["text"]


def test_chunk_header_pattern(chunker):
    """Test that only valid markdown headers are recognized"""
    text = """# Valid Header
#### Also valid (h4)
Not a header because no space after #
#Also not a header

## Real Header
Content."""

    chunks = chunker.chunk(text)

    # Only "Valid Header" and "Real Header" should be recognized
    headers = [chunk["metadata"]["header"] for chunk in chunks]
    assert "Valid Header" in headers
    assert "Real Header" in headers
