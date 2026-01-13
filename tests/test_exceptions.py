"""Tests for src/exceptions.py"""
import pytest
from src.exceptions import (
    MathesisBaseException,
    CrawlerException,
    SchoolNotFoundError,
    CrawlerTimeoutError,
    ETLException,
    ValidationError,
    LoadError,
    RAGException,
    ExportException
)


def test_mathesis_base_exception():
    """Test MathesisBaseException"""
    exc = MathesisBaseException("Test error")
    assert str(exc) == "Test error"
    assert isinstance(exc, Exception)


def test_crawler_exception():
    """Test CrawlerException"""
    exc = CrawlerException("Crawler error")
    assert str(exc) == "Crawler error"
    assert isinstance(exc, MathesisBaseException)


def test_school_not_found_error():
    """Test SchoolNotFoundError"""
    exc = SchoolNotFoundError("School not found")
    assert str(exc) == "School not found"
    assert isinstance(exc, CrawlerException)
    assert isinstance(exc, MathesisBaseException)


def test_crawler_timeout_error():
    """Test CrawlerTimeoutError"""
    exc = CrawlerTimeoutError("Timeout")
    assert str(exc) == "Timeout"
    assert isinstance(exc, CrawlerException)


def test_etl_exception():
    """Test ETLException"""
    exc = ETLException("ETL error")
    assert str(exc) == "ETL error"
    assert isinstance(exc, MathesisBaseException)


def test_validation_error():
    """Test ValidationError"""
    exc = ValidationError("Validation failed")
    assert str(exc) == "Validation failed"
    assert isinstance(exc, ETLException)
    assert isinstance(exc, MathesisBaseException)


def test_load_error():
    """Test LoadError"""
    exc = LoadError("Load failed")
    assert str(exc) == "Load failed"
    assert isinstance(exc, ETLException)


def test_rag_exception():
    """Test RAGException"""
    exc = RAGException("RAG error")
    assert str(exc) == "RAG error"
    assert isinstance(exc, MathesisBaseException)


def test_export_exception():
    """Test ExportException"""
    exc = ExportException("Export error")
    assert str(exc) == "Export error"
    assert isinstance(exc, MathesisBaseException)


def test_exception_raising():
    """Test that exceptions can be raised and caught"""
    with pytest.raises(SchoolNotFoundError):
        raise SchoolNotFoundError("Test school not found")

    with pytest.raises(CrawlerException):
        raise CrawlerTimeoutError("Test timeout")

    with pytest.raises(MathesisBaseException):
        raise ValidationError("Test validation")


def test_exception_hierarchy():
    """Test exception hierarchy"""
    # All crawler exceptions should be caught by CrawlerException
    try:
        raise SchoolNotFoundError("Test")
    except CrawlerException as e:
        assert isinstance(e, SchoolNotFoundError)

    # All exceptions should be caught by MathesisBaseException
    try:
        raise LoadError("Test")
    except MathesisBaseException as e:
        assert isinstance(e, LoadError)
