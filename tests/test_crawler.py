"""Tests for src/crawler.py - Core functionality only"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Mock TypstGenerator before importing crawler
sys.modules['src.pdf_gen'] = Mock()

@pytest.fixture
def mock_dependencies():
    with patch('src.pdf_gen.TypstGenerator') as mock_typst:
        mock_typst_instance = Mock()
        mock_typst_instance.compile = Mock()
        mock_typst.return_value = mock_typst_instance
        yield {'typst': mock_typst_instance}


def test_crawler_base_url():
    """Test crawler has correct base URL"""
    from src.crawler import SchoolInfoCrawler

    assert SchoolInfoCrawler.BASE_URL == "https://www.schoolinfo.go.kr"


@pytest.mark.asyncio
async def test_download_teaching_plans_creates_directory(mock_dependencies):
    """Test that download creates output directory"""
    from src.crawler import SchoolInfoCrawler

    crawler = SchoolInfoCrawler(base_url="https://test.com")

    with patch('os.makedirs') as mock_makedirs, \
         patch('os.path.exists', return_value=True):
        await crawler.download_teaching_plans("TEST001", 2025)

        mock_makedirs.assert_called()


@pytest.mark.asyncio
async def test_download_teaching_plans_returns_list(mock_dependencies):
    """Test that download returns list of files"""
    from src.crawler import SchoolInfoCrawler

    crawler = SchoolInfoCrawler(base_url="https://test.com")

    with patch('os.makedirs'), \
         patch('os.path.exists', return_value=True):
        result = await crawler.download_teaching_plans("TEST001", 2025)

        assert isinstance(result, list)


@pytest.mark.asyncio
async def test_download_handles_typst_failure(mock_dependencies):
    """Test graceful handling when Typst fails"""
    from src.crawler import SchoolInfoCrawler

    mock_dependencies['typst'].compile.side_effect = Exception("Typst error")

    crawler = SchoolInfoCrawler(base_url="https://test.com")

    with patch('os.makedirs'), \
         patch('os.path.exists', return_value=True):
        # Should not raise exception
        result = await crawler.download_teaching_plans("TEST001", 2025)
        assert isinstance(result, list)
