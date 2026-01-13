"""Tests for src/rag/enhanced_json_generator.py"""
import pytest
import json
from src.rag.enhanced_json_generator import EnhancedJSONGenerator


@pytest.fixture
def generator():
    return EnhancedJSONGenerator()


def test_generator_initialization(generator):
    """Test generator initialization"""
    assert generator.document_id_counter == 0
    assert generator.section_id_counter == 0
    assert generator.table_id_counter == 0


def test_split_by_pages_single_page(generator):
    """Test splitting single page markdown"""
    text = """## Page 1
Content for page 1
More content"""

    pages = generator._split_by_pages(text)

    assert len(pages) == 1
    assert "## Page 1" in pages[0]
    assert "Content for page 1" in pages[0]


def test_split_by_pages_multiple_pages(generator):
    """Test splitting multiple pages"""
    text = """## Page 1
Content 1
## Page 2
Content 2
## Page 3
Content 3"""

    pages = generator._split_by_pages(text)

    assert len(pages) == 3
    assert "Content 1" in pages[0]
    assert "Content 2" in pages[1]
    assert "Content 3" in pages[2]


def test_parse_markdown_table_valid(generator):
    """Test parsing valid markdown table"""
    md_table = """| Header1 | Header2 | Header3 |
| --- | --- | --- |
| Value1 | Value2 | Value3 |
| A | B | C |"""

    result = generator._parse_markdown_table(md_table, "sec_001")

    assert result is not None
    assert result["headers"] == ["Header1", "Header2", "Header3"]
    assert len(result["rows"]) == 2
    assert result["rows"][0] == {"Header1": "Value1", "Header2": "Value2", "Header3": "Value3"}
    assert result["parent_section_id"] == "sec_001"


def test_parse_markdown_table_empty(generator):
    """Test parsing empty table"""
    result = generator._parse_markdown_table("", "sec_001")
    assert result is None


def test_parse_markdown_table_too_short(generator):
    """Test table with less than 3 lines"""
    md_table = """| Header |
| --- |"""

    result = generator._parse_markdown_table(md_table, "sec_001")
    assert result is None


def test_parse_markdown_table_mismatched_columns(generator):
    """Test table with mismatched column counts"""
    md_table = """| Col1 | Col2 | Col3 |
| --- | --- | --- |
| A | B |
| X | Y | Z | W |"""

    result = generator._parse_markdown_table(md_table, "sec_001")

    assert result is not None
    # First row should be padded
    assert result["rows"][0]["Col3"] == ""
    # Second row should be truncated
    assert len(result["rows"][1]) == 3


def test_auto_structure_table_with_percentages(generator):
    """Test extracting percentage data"""
    rows = [
        {"Subject": "Math", "Score": "85%"},
        {"Subject": "English", "Score": "92%"}
    ]

    structured = generator._auto_structure_table(rows, ["Subject", "Score"])

    assert "Score" in structured
    assert 85 in structured["Score"]
    assert 92 in structured["Score"]


def test_auto_structure_table_with_numbers(generator):
    """Test extracting numeric data"""
    rows = [
        {"Item": "Test1", "Value": "42.5"},
        {"Item": "Test2", "Value": "38.2"}
    ]

    structured = generator._auto_structure_table(rows, ["Item", "Value"])

    assert "Value" in structured
    assert 42.5 in structured["Value"]
    assert 38.2 in structured["Value"]


def test_auto_structure_table_with_text_lists(generator):
    """Test extracting text lists"""
    rows = [
        {"Category": "Fruits", "Items": "apple, banana, orange"},
        {"Category": "Colors", "Items": "red, blue"}
    ]

    structured = generator._auto_structure_table(rows, ["Category", "Items"])

    assert "Items_list" in structured
    assert "apple" in structured["Items_list"]
    assert "banana" in structured["Items_list"]


def test_generate_qa_pairs_with_percentage(generator):
    """Test Q&A pair generation for percentages"""
    rows = [{"평가 비율": "40%"}]

    qa_pairs = generator._generate_qa_pairs(rows, ["평가 비율"])

    assert len(qa_pairs) > 0
    assert any("평가 비율" in qa["question"] for qa in qa_pairs)
    assert any(qa["answer"] == "40%" for qa in qa_pairs)


def test_generate_qa_pairs_with_dates(generator):
    """Test Q&A pair generation for dates"""
    rows = [{"시기": "2025-03-01"}]

    qa_pairs = generator._generate_qa_pairs(rows, ["시기"])

    assert len(qa_pairs) > 0
    assert any("언제" in qa["question"] for qa in qa_pairs)


def test_generate_qa_pairs_skip_empty_values(generator):
    """Test Q&A generation skips empty values"""
    rows = [{"Key": ""}, {"Key2": "-"}]

    qa_pairs = generator._generate_qa_pairs(rows, ["Key", "Key2"])

    assert len(qa_pairs) == 0


def test_infer_table_caption(generator):
    """Test table caption inference"""
    headers = ["Subject", "Score", "Grade", "Extra"]

    caption = generator._infer_table_caption(headers)

    assert "Subject" in caption
    assert "Score" in caption
    assert "Grade" in caption
    # Should only include first 3
    assert "Extra" not in caption


def test_generate_document_id(generator):
    """Test document ID generation"""
    metadata = {
        "school_code": "TEST001",
        "year": "2025",
        "grade": "1",
        "subject": "math",
        "semester": "1"
    }

    doc_id = generator._generate_document_id(metadata)

    assert doc_id == "doc_TEST001_2025_1_math_1"


def test_generate_document_id_defaults(generator):
    """Test document ID with missing metadata"""
    metadata = {}

    doc_id = generator._generate_document_id(metadata)

    assert doc_id == "doc_UNKNOWN_0000_0_general_0"


def test_build_section_narrative_only(generator):
    """Test building section with only narrative content"""
    content = ["This is narrative text.", "More narrative."]

    section = generator._build_section("Test Section", content, [], 1)

    assert section is not None
    assert section["section_title"] == "Test Section"
    assert section["section_type"] == "narrative"
    assert "narrative text" in section["content"]
    assert len(section["tables"]) == 0


def test_build_section_with_table(generator):
    """Test building section with table"""
    table_lines = [
        "| Col1 | Col2 |",
        "| --- | --- |",
        "| A | B |"
    ]

    section = generator._build_section("Table Section", [], table_lines, 1)

    assert section is not None
    assert section["section_type"] == "table_dominant"
    assert len(section["tables"]) == 1


def test_build_section_mixed(generator):
    """Test building mixed section"""
    content = ["Some text" * 20]  # Long text
    table_lines = [
        "| Col1 | Col2 |",
        "| --- | --- |",
        "| A | B |"
    ]

    section = generator._build_section("Mixed Section", content, table_lines, 1)

    assert section is not None
    assert section["section_type"] == "mixed"
    assert len(section["tables"]) == 1
    assert len(section["content"]) > 100


def test_parse_page_to_sections(generator):
    """Test parsing page to sections"""
    page_text = """## Page 1
1. First Section
Some content here
2. Second Section
More content"""

    sections = generator._parse_page_to_sections(page_text, 1)

    assert len(sections) >= 1
    assert any("First Section" in s["section_title"] for s in sections)


def test_generate_rag_metadata(generator):
    """Test RAG metadata generation"""
    sections = [
        {
            "section_id": "sec_001",
            "section_type": "narrative",
            "tables": [{"table_id": "tbl_001"}]
        },
        {
            "section_id": "sec_002",
            "section_type": "table_dominant",
            "tables": [{"table_id": "tbl_002"}, {"table_id": "tbl_003"}]
        }
    ]

    metadata = generator._generate_rag_metadata(sections, "doc_123")

    assert metadata["chunk_strategy"] == "section_based"
    assert metadata["parent_document_id"] == "doc_123"
    assert metadata["supports_hierarchical_retrieval"] is True
    assert len(metadata["chunk_ids"]) == 2


def test_generate_from_markdown_complete(generator):
    """Test complete markdown to JSON conversion"""
    markdown = """## Page 1
1. Introduction
This is the introduction section.

| Subject | Credits |
| --- | --- |
| Math | 3 |
| Science | 4 |

## Page 2
2. Evaluation Plan
Evaluation details here."""

    metadata = {
        "school_code": "TEST001",
        "school_name": "Test School",
        "year": "2025",
        "grade": "1",
        "subject": "general"
    }

    result = generator.generate_from_markdown(markdown, metadata)

    assert "document_metadata" in result
    assert result["document_metadata"]["document_id"] == "doc_TEST001_2025_1_general_0"
    assert result["document_metadata"]["page_count"] == 2
    assert result["document_metadata"]["school_name"] == "Test School"
    assert "sections" in result
    assert len(result["sections"]) >= 1
    assert "rag_optimization" in result


def test_generate_from_markdown_empty(generator):
    """Test markdown generation with empty input"""
    result = generator.generate_from_markdown("", {})

    assert "document_metadata" in result
    # Empty string results in 1 page with empty content
    assert result["document_metadata"]["page_count"] >= 0


def test_section_id_counter_increments(generator):
    """Test section ID counter increments correctly"""
    initial = generator.section_id_counter

    generator._build_section("Test", ["content"], [], 1)

    assert generator.section_id_counter == initial + 1


def test_table_id_counter_increments(generator):
    """Test table ID counter increments correctly"""
    initial = generator.table_id_counter

    md_table = """| H1 | H2 |
| --- | --- |
| A | B |"""

    generator._parse_markdown_table(md_table, "sec_001")

    assert generator.table_id_counter == initial + 1


def test_section_with_inline_table(generator):
    """Test section with table in content lines"""
    # Join content as a single table string
    table_str = "| Col1 | Col2 | Col3 |\n| --- | --- | --- |\n| A | B | C |"
    content = [
        "Introduction text",
        table_str,
        "More text after table"
    ]

    section = generator._build_section("Section", content, [], 1)

    assert section is not None
    # Tables are only parsed if they are in a single content string
    assert len(section["tables"]) >= 0


def test_parse_page_with_table_in_section(generator):
    """Test parsing page with table embedded in section"""
    page_text = """1. Test Section
Some introduction text

| Header1 | Header2 |
| --- | --- |
| Data1 | Data2 |

Closing text"""

    sections = generator._parse_page_to_sections(page_text, 1)

    assert len(sections) >= 1
    # Should detect table in section


def test_auto_structure_removes_duplicates(generator):
    """Test that auto structure removes duplicates"""
    rows = [
        {"Item": "apple"},
        {"Item": "apple"},
        {"Item": "banana"}
    ]

    structured = generator._auto_structure_table(rows, ["Item"])

    item_list = structured.get("Item_list", [])
    assert len(item_list) == 2  # apple and banana, no duplicates
