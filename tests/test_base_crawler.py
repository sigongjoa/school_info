"""Tests for src/base_crawler.py"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
import httpx
from src.base_crawler import BaseCrawler
from src.exceptions import CrawlerException, CrawlerTimeoutError


class TestCrawler(BaseCrawler):
    """Concrete implementation for testing"""
    async def fetch(self, resource_id: str):
        return {"id": resource_id, "data": "test"}


@pytest.fixture
def crawler():
    return TestCrawler(base_url="https://example.com")


def test_crawler_initialization():
    """Test crawler initialization"""
    crawler = TestCrawler(
        base_url="https://test.com",
        timeout=60,
        max_retries=5,
        headers={"Custom": "Header"}
    )

    assert crawler.base_url == "https://test.com"
    assert crawler.timeout == 60
    assert crawler.max_retries == 5
    assert crawler.headers["Custom"] == "Header"


def test_crawler_default_headers():
    """Test default headers"""
    crawler = TestCrawler(base_url="https://test.com")

    assert "User-Agent" in crawler.headers
    assert "Mozilla" in crawler.headers["User-Agent"]


@pytest.mark.asyncio
async def test_fetch_method(crawler):
    """Test fetch method"""
    result = await crawler.fetch("test_id")

    assert result["id"] == "test_id"
    assert result["data"] == "test"


@pytest.mark.asyncio
async def test_get_success(crawler):
    """Test successful GET request"""
    mock_response = Mock()
    mock_response.raise_for_status = Mock()

    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        result = await crawler._get("https://example.com/api")

        assert result == mock_response


@pytest.mark.asyncio
async def test_get_timeout_with_retry(crawler):
    """Test GET request timeout with successful retry"""
    mock_response = Mock()
    mock_response.raise_for_status = Mock()

    with patch('httpx.AsyncClient') as mock_client:
        mock_get = AsyncMock()
        # First call raises timeout, second succeeds
        mock_get.side_effect = [httpx.TimeoutException("Timeout"), mock_response]
        mock_client.return_value.__aenter__.return_value.get = mock_get

        result = await crawler._get("https://example.com/api")

        assert result == mock_response
        assert mock_get.call_count == 2


@pytest.mark.asyncio
async def test_get_timeout_max_retries(crawler):
    """Test GET request timeout exceeding max retries"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
        mock_client.return_value.__aenter__.return_value.get = mock_get

        with pytest.raises(CrawlerTimeoutError) as exc_info:
            await crawler._get("https://example.com/api")

        assert "after 3 retries" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_http_error(crawler):
    """Test GET request HTTP error"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_get = AsyncMock(side_effect=httpx.HTTPError("HTTP Error"))
        mock_client.return_value.__aenter__.return_value.get = mock_get

        with pytest.raises(CrawlerException) as exc_info:
            await crawler._get("https://example.com/api")

        assert "HTTP Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_unexpected_error(crawler):
    """Test GET request unexpected error"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_get = AsyncMock(side_effect=Exception("Unexpected"))
        mock_client.return_value.__aenter__.return_value.get = mock_get

        with pytest.raises(CrawlerException) as exc_info:
            await crawler._get("https://example.com/api")

        assert "Unexpected error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_with_params(crawler):
    """Test GET request with query parameters"""
    mock_response = Mock()
    mock_response.raise_for_status = Mock()

    with patch('httpx.AsyncClient') as mock_client:
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get

        await crawler._get("https://example.com/api", params={"key": "value"})

        mock_get.assert_called_once_with("https://example.com/api", params={"key": "value"})
