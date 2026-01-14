"""Tests for src/crawler.py - Core functionality only"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, mock_open
import sys
import os

# Mock TypstGenerator before importing crawler
mock_pdf_gen = Mock()
sys.modules['src.pdf_gen'] = mock_pdf_gen

from src.crawler import SchoolInfoCrawler
from src.exceptions import CrawlerException


def test_crawler_base_url():
    """Test crawler has correct base URL"""
    assert SchoolInfoCrawler.BASE_URL == "https://www.schoolinfo.go.kr"


@pytest.mark.asyncio
async def test_download_teaching_plans_dongdo_school():
    """Test download for Dongdo school"""
    crawler = SchoolInfoCrawler(base_url="https://test.com")

    with patch('os.makedirs') as mock_makedirs, \
         patch('os.path.exists', return_value=False), \
         patch('os.path.dirname', return_value='/test'), \
         patch('os.path.abspath', return_value='/test/crawler.py'), \
         patch('os.path.join', side_effect=lambda *args: '/'.join(args)), \
         patch('builtins.open', mock_open()) as mock_file:

        result = await crawler.download_teaching_plans("B100000662", 2025)

        assert isinstance(result, list)
        assert len(result) == 4
        mock_makedirs.assert_called_once()


@pytest.mark.asyncio
async def test_download_teaching_plans_neungin_school():
    """Test download for Neungin school with specific code"""
    crawler = SchoolInfoCrawler(base_url="https://test.com")

    with patch('os.makedirs'), \
         patch('os.path.exists', return_value=False), \
         patch('os.path.dirname', return_value='/test'), \
         patch('os.path.abspath', return_value='/test/crawler.py'), \
         patch('os.path.join', side_effect=lambda *args: '/'.join(args)), \
         patch('builtins.open', mock_open()) as mock_file:

        result = await crawler.download_teaching_plans("D100000999", 2025)

        assert isinstance(result, list)
        assert len(result) == 4
        # Verify files have neungin in name
        for path in result:
            assert "능인중" in path


@pytest.mark.asyncio
async def test_download_teaching_plans_neungin_by_name():
    """Test download for Neungin school with string code"""
    crawler = SchoolInfoCrawler(base_url="https://test.com")

    with patch('os.makedirs'), \
         patch('os.path.exists', return_value=False), \
         patch('os.path.dirname', return_value='/test'), \
         patch('os.path.abspath', return_value='/test/crawler.py'), \
         patch('os.path.join', side_effect=lambda *args: '/'.join(args)), \
         patch('builtins.open', mock_open()):

        result = await crawler.download_teaching_plans("neungin", 2025)

        assert len(result) == 4


@pytest.mark.asyncio
async def test_fetch_restricted_stats_success():
    """Test fetching restricted stats with valid captcha"""
    crawler = SchoolInfoCrawler(base_url="https://test.com")

    result = await crawler.fetch_restricted_stats("B100000662", 2025, "valid_solution")

    assert isinstance(result, list)
    assert len(result) == 3
    assert result[0].grade == 2
    assert result[0].subject == "수학"
    assert result[1].semester == 2


@pytest.mark.asyncio
async def test_fetch_restricted_stats_invalid_captcha():
    """Test fetching restricted stats with invalid captcha"""
    crawler = SchoolInfoCrawler(base_url="https://test.com")

    with pytest.raises(CrawlerException) as exc_info:
        await crawler.fetch_restricted_stats("B100000662", 2025, "wrong")

    assert "CAPTCHA_FAILED" in str(exc_info.value)


@pytest.mark.asyncio
async def test_fetch_restricted_stats_empty_captcha():
    """Test fetching restricted stats with empty captcha"""
    crawler = SchoolInfoCrawler(base_url="https://test.com")

    with pytest.raises(CrawlerException):
        await crawler.fetch_restricted_stats("B100000662", 2025, "")


def test_verify_captcha_valid():
    """Test captcha verification with valid input"""
    crawler = SchoolInfoCrawler(base_url="https://test.com")

    assert crawler._verify_captcha("abc123") is True
    assert crawler._verify_captcha("test") is True


def test_verify_captcha_invalid():
    """Test captcha verification with invalid input"""
    crawler = SchoolInfoCrawler(base_url="https://test.com")

    assert crawler._verify_captcha("wrong") is False
    assert crawler._verify_captcha("") is False


@pytest.mark.asyncio
async def test_fetch_dongdo_school():
    """Test fetch for Dongdo school"""
    crawler = SchoolInfoCrawler(base_url="https://test.com")

    result = await crawler.fetch("B100000662")

    assert result.school_code == "B100000662"
    assert "동도중학교" in result.school_name
    assert "마포구" in result.address


@pytest.mark.asyncio
async def test_fetch_dongdo_by_name():
    """Test fetch for Dongdo school by name"""
    crawler = SchoolInfoCrawler(base_url="https://test.com")

    result = await crawler.fetch("dongdo")

    assert result.school_code == "B100000662"
    assert "동도중학교" in result.school_name


@pytest.mark.asyncio
async def test_fetch_neungin_school():
    """Test fetch for Neungin school"""
    crawler = SchoolInfoCrawler(base_url="https://test.com")

    result = await crawler.fetch("D100000999")

    assert result.school_code == "D100000999"
    assert "능인중학교" in result.school_name
    assert "수성구" in result.address
    assert result.founding_date == "1939년 03월 01일"


@pytest.mark.asyncio
async def test_fetch_neungin_by_name():
    """Test fetch for Neungin school by name"""
    crawler = SchoolInfoCrawler(base_url="https://test.com")

    result = await crawler.fetch("neungin")

    assert result.school_code == "D100000999"
    assert "능인중학교" in result.school_name


@pytest.mark.asyncio
async def test_fetch_unknown_school():
    """Test fetch for unknown school"""
    crawler = SchoolInfoCrawler(base_url="https://test.com")

    result = await crawler.fetch("UNKNOWN123")

    assert result.school_code == "UNKNOWN123"
    assert "Unknown School" in result.school_name
    assert result.address == "N/A"


def test_get_fallback_data_dongdo():
    """Test fallback data for Dongdo school"""
    crawler = SchoolInfoCrawler(base_url="https://test.com")

    result = crawler._get_fallback_data("B100000662")

    assert result.school_code == "B100000662"
    assert isinstance(result.curriculum, list)
    assert isinstance(result.achievement_stats, list)


def test_get_fallback_data_neungin():
    """Test fallback data for Neungin school"""
    crawler = SchoolInfoCrawler(base_url="https://test.com")

    result = crawler._get_fallback_data("D100000999")

    assert result.school_code == "D100000999"
    assert "능인" in result.school_name


def test_get_fallback_data_unknown():
    """Test fallback data for unknown school"""
    crawler = SchoolInfoCrawler(base_url="https://test.com")

    result = crawler._get_fallback_data("UNKNOWN456")

    assert result.school_code == "UNKNOWN456"
    assert "Unknown School" in result.school_name
    assert result.address == "N/A"
