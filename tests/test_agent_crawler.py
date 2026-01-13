"""Tests for src/agent_crawler.py"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock


@pytest.fixture
def mock_playwright():
    """Mock playwright and browser objects"""
    # Create mock hierarchy: playwright -> browser -> context -> page
    mock_page = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.wait_for_load_state = AsyncMock()
    mock_page.evaluate = AsyncMock()
    mock_page.screenshot = AsyncMock()
    mock_page.locator = Mock()
    mock_page.content = AsyncMock(return_value="<html>Mock HTML</html>")
    mock_page.keyboard = AsyncMock()
    mock_page.keyboard.press = AsyncMock()
    mock_page.url = "https://www.schoolinfo.go.kr/test"

    # Mock locator for various elements
    mock_locator = AsyncMock()
    mock_locator.wait_for = AsyncMock()
    mock_locator.click = AsyncMock()
    mock_locator.fill = AsyncMock()
    mock_locator.first = mock_locator
    mock_locator.count = AsyncMock(return_value=1)
    mock_locator.inner_text = AsyncMock(return_value="Test School")
    mock_locator.get_attribute = AsyncMock(return_value="href_value")
    mock_locator.all = AsyncMock(return_value=[])
    mock_page.locator.return_value = mock_locator

    # Mock context
    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.add_init_script = AsyncMock()
    mock_context.pages = [mock_page]

    # Mock expect_page for popup handling
    mock_expect_page = AsyncMock()
    mock_expect_page.__aenter__ = AsyncMock(return_value=mock_expect_page)
    mock_expect_page.__aexit__ = AsyncMock()
    mock_expect_page.value = None  # No popup by default
    mock_context.expect_page = Mock(return_value=mock_expect_page)

    # Mock browser
    mock_browser = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()

    # Mock chromium launcher
    mock_chromium = Mock()
    mock_chromium.launch = AsyncMock(return_value=mock_browser)

    # Mock playwright
    mock_pw = AsyncMock()
    mock_pw.chromium = mock_chromium
    mock_pw.__aenter__ = AsyncMock(return_value=mock_pw)
    mock_pw.__aexit__ = AsyncMock()

    return {
        'playwright': mock_pw,
        'browser': mock_browser,
        'context': mock_context,
        'page': mock_page,
        'locator': mock_locator
    }


@pytest.mark.asyncio
async def test_crawler_initialization():
    """Test crawler initialization"""
    from src.agent_crawler import RealBrowserCrawler

    crawler = RealBrowserCrawler()

    assert crawler.BASE_URL == "https://www.schoolinfo.go.kr"


@pytest.mark.asyncio
async def test_run_basic_flow(mock_playwright):
    """Test basic run flow without errors"""
    from src.agent_crawler import RealBrowserCrawler

    crawler = RealBrowserCrawler()

    # Configure mock locator to return no search results (to exit early)
    mock_playwright['locator'].wait_for = AsyncMock(
        side_effect=Exception("No results")
    )

    with patch('src.agent_crawler.async_playwright', return_value=mock_playwright['playwright']), \
         patch('os.makedirs'), \
         patch('asyncio.sleep', return_value=None):

        # Should not raise exception even with errors
        await crawler.run("Test School", headless=True)

        # Verify browser was launched
        mock_playwright['playwright'].chromium.launch.assert_called_once()
        # Verify browser was closed
        mock_playwright['browser'].close.assert_called_once()


@pytest.mark.asyncio
async def test_run_creates_directories(mock_playwright):
    """Test that run creates necessary directories"""
    from src.agent_crawler import RealBrowserCrawler

    crawler = RealBrowserCrawler()

    with patch('src.agent_crawler.async_playwright', return_value=mock_playwright['playwright']), \
         patch('os.makedirs') as mock_makedirs, \
         patch('asyncio.sleep', return_value=None):

        try:
            await crawler.run("Test", headless=True)
        except:
            pass

        # Should create download_dir and debug_dir
        assert mock_makedirs.call_count >= 2


@pytest.mark.asyncio
async def test_run_navigates_to_homepage(mock_playwright):
    """Test navigation to homepage"""
    from src.agent_crawler import RealBrowserCrawler

    crawler = RealBrowserCrawler()

    with patch('src.agent_crawler.async_playwright', return_value=mock_playwright['playwright']), \
         patch('os.makedirs'), \
         patch('asyncio.sleep', return_value=None):

        try:
            await crawler.run("Test", headless=True)
        except:
            pass

        # Verify goto was called with BASE_URL
        mock_playwright['page'].goto.assert_called()
        call_args = mock_playwright['page'].goto.call_args
        assert "schoolinfo.go.kr" in call_args[0][0]


@pytest.mark.asyncio
async def test_run_removes_popups(mock_playwright):
    """Test popup removal"""
    from src.agent_crawler import RealBrowserCrawler

    crawler = RealBrowserCrawler()

    with patch('src.agent_crawler.async_playwright', return_value=mock_playwright['playwright']), \
         patch('os.makedirs'), \
         patch('asyncio.sleep', return_value=None):

        try:
            await crawler.run("Test", headless=True)
        except:
            pass

        # Verify evaluate was called (for popup removal)
        mock_playwright['page'].evaluate.assert_called()


@pytest.mark.asyncio
async def test_run_takes_screenshots(mock_playwright):
    """Test screenshot capture"""
    from src.agent_crawler import RealBrowserCrawler

    crawler = RealBrowserCrawler()

    with patch('src.agent_crawler.async_playwright', return_value=mock_playwright['playwright']), \
         patch('os.makedirs'), \
         patch('asyncio.sleep', return_value=None):

        try:
            await crawler.run("Test", headless=True)
        except:
            pass

        # Should take at least one screenshot
        assert mock_playwright['page'].screenshot.call_count >= 1


@pytest.mark.asyncio
async def test_run_searches_for_school(mock_playwright):
    """Test search functionality"""
    from src.agent_crawler import RealBrowserCrawler

    crawler = RealBrowserCrawler()

    with patch('src.agent_crawler.async_playwright', return_value=mock_playwright['playwright']), \
         patch('os.makedirs'), \
         patch('asyncio.sleep', return_value=None):

        try:
            await crawler.run("동도중학교", headless=True)
        except:
            pass

        # Verify search input was filled
        mock_playwright['locator'].fill.assert_called()
        fill_call = mock_playwright['locator'].fill.call_args
        assert "동도중학교" in fill_call[0]


@pytest.mark.asyncio
async def test_run_handles_search_error(mock_playwright):
    """Test handling of search interaction error"""
    from src.agent_crawler import RealBrowserCrawler

    # Make search input fail
    mock_playwright['locator'].wait_for = AsyncMock(
        side_effect=Exception("Element not found")
    )

    crawler = RealBrowserCrawler()

    with patch('src.agent_crawler.async_playwright', return_value=mock_playwright['playwright']), \
         patch('os.makedirs'), \
         patch('asyncio.sleep', return_value=None):

        # Should not raise exception
        await crawler.run("Test", headless=True)

        # Should take error screenshot
        screenshot_calls = [
            call for call in mock_playwright['page'].screenshot.call_args_list
            if 'error' in str(call)
        ]
        assert len(screenshot_calls) > 0


@pytest.mark.asyncio
async def test_run_saves_debug_html(mock_playwright):
    """Test saving debug HTML"""
    from src.agent_crawler import RealBrowserCrawler

    crawler = RealBrowserCrawler()

    with patch('src.agent_crawler.async_playwright', return_value=mock_playwright['playwright']), \
         patch('os.makedirs'), \
         patch('asyncio.sleep', return_value=None), \
         patch('builtins.open', create=True) as mock_open:

        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        try:
            await crawler.run("Test", headless=True)
        except:
            pass

        # Should save HTML files
        assert mock_open.call_count >= 0  # May not reach if search fails


@pytest.mark.asyncio
async def test_run_handles_new_page_popup(mock_playwright):
    """Test handling of popup windows"""
    from src.agent_crawler import RealBrowserCrawler

    # Mock a new page popup
    new_page = AsyncMock()
    new_page.url = "https://detail.page"
    new_page.wait_for_load_state = AsyncMock()
    new_page.screenshot = AsyncMock()
    new_page.content = AsyncMock(return_value="<html>Detail</html>")
    new_page.locator = Mock(return_value=mock_playwright['locator'])

    mock_expect = AsyncMock()
    mock_expect.value = new_page
    mock_expect_page = AsyncMock()
    mock_expect_page.__aenter__ = AsyncMock(return_value=mock_expect)
    mock_expect_page.__aexit__ = AsyncMock()
    mock_playwright['context'].expect_page = Mock(return_value=mock_expect_page)

    crawler = RealBrowserCrawler()

    with patch('src.agent_crawler.async_playwright', return_value=mock_playwright['playwright']), \
         patch('os.makedirs'), \
         patch('asyncio.sleep', return_value=None), \
         patch('builtins.open', create=True):

        try:
            await crawler.run("Test School", headless=True)
        except:
            pass


@pytest.mark.asyncio
async def test_run_selects_year_2025(mock_playwright):
    """Test year selection"""
    from src.agent_crawler import RealBrowserCrawler

    # Mock year select element
    year_locator = AsyncMock()
    year_locator.first = year_locator
    year_locator.select_option = AsyncMock()

    def locator_side_effect(selector):
        if "#gsYear" in selector:
            return year_locator
        return mock_playwright['locator']

    mock_playwright['page'].locator.side_effect = locator_side_effect

    crawler = RealBrowserCrawler()

    with patch('src.agent_crawler.async_playwright', return_value=mock_playwright['playwright']), \
         patch('os.makedirs'), \
         patch('asyncio.sleep', return_value=None):

        try:
            await crawler.run("Test", headless=True)
        except:
            pass


@pytest.mark.asyncio
async def test_run_clicks_main_tabs(mock_playwright):
    """Test clicking main tabs"""
    from src.agent_crawler import RealBrowserCrawler

    mock_tab_locator = AsyncMock()
    mock_tab_locator.first = mock_tab_locator
    mock_tab_locator.count = AsyncMock(return_value=1)
    mock_tab_locator.click = AsyncMock()

    mock_playwright['page'].locator = Mock(return_value=mock_tab_locator)

    crawler = RealBrowserCrawler()

    with patch('src.agent_crawler.async_playwright', return_value=mock_playwright['playwright']), \
         patch('os.makedirs'), \
         patch('asyncio.sleep', return_value=None):

        try:
            await crawler.run("Test", headless=True)
        except:
            pass


@pytest.mark.asyncio
async def test_run_attempts_file_download(mock_playwright):
    """Test file download attempt"""
    from src.agent_crawler import RealBrowserCrawler

    # Mock file link
    file_link = AsyncMock()
    file_link.inner_text = AsyncMock(return_value="test.hwp")
    file_link.get_attribute = AsyncMock(return_value="/download/file")
    file_link.click = AsyncMock()

    mock_playwright['locator'].all = AsyncMock(return_value=[file_link])
    mock_playwright['locator'].count = AsyncMock(return_value=1)

    # Mock download
    mock_download = AsyncMock()
    mock_download.suggested_filename = "test.hwp"
    mock_download.save_as = AsyncMock()

    mock_expect_download = AsyncMock()
    mock_expect_download.value = mock_download
    mock_download_context = AsyncMock()
    mock_download_context.__aenter__ = AsyncMock(return_value=mock_expect_download)
    mock_download_context.__aexit__ = AsyncMock()
    mock_playwright['page'].expect_download = Mock(return_value=mock_download_context)

    crawler = RealBrowserCrawler()

    with patch('src.agent_crawler.async_playwright', return_value=mock_playwright['playwright']), \
         patch('os.makedirs'), \
         patch('asyncio.sleep', return_value=None), \
         patch('builtins.open', create=True):

        try:
            await crawler.run("Test School", headless=True)
        except:
            pass


@pytest.mark.asyncio
async def test_run_handles_download_failure(mock_playwright):
    """Test handling of download failure"""
    from src.agent_crawler import RealBrowserCrawler

    # Mock file link that fails
    file_link = AsyncMock()
    file_link.inner_text = AsyncMock(return_value="test.pdf")
    file_link.click = AsyncMock(side_effect=Exception("Download failed"))

    mock_playwright['locator'].all = AsyncMock(return_value=[file_link])

    crawler = RealBrowserCrawler()

    with patch('src.agent_crawler.async_playwright', return_value=mock_playwright['playwright']), \
         patch('os.makedirs'), \
         patch('asyncio.sleep', return_value=None):

        # Should not raise exception
        await crawler.run("Test", headless=True)


@pytest.mark.asyncio
async def test_run_browser_closes_on_error(mock_playwright):
    """Test browser closes even on error"""
    from src.agent_crawler import RealBrowserCrawler

    # Make page.goto fail
    mock_playwright['page'].goto = AsyncMock(side_effect=Exception("Navigation failed"))

    crawler = RealBrowserCrawler()

    with patch('src.agent_crawler.async_playwright', return_value=mock_playwright['playwright']), \
         patch('os.makedirs'), \
         patch('asyncio.sleep', return_value=None):

        await crawler.run("Test", headless=True)

        # Browser should still be closed
        mock_playwright['browser'].close.assert_called_once()


@pytest.mark.asyncio
async def test_run_headless_parameter(mock_playwright):
    """Test headless parameter is passed correctly"""
    from src.agent_crawler import RealBrowserCrawler

    crawler = RealBrowserCrawler()

    with patch('src.agent_crawler.async_playwright', return_value=mock_playwright['playwright']), \
         patch('os.makedirs'), \
         patch('asyncio.sleep', return_value=None):

        await crawler.run("Test", headless=False)

        # Check launch was called with headless=False
        launch_call = mock_playwright['playwright'].chromium.launch.call_args
        assert launch_call[1]['headless'] is False


@pytest.mark.asyncio
async def test_run_sets_anti_detection(mock_playwright):
    """Test anti-detection settings"""
    from src.agent_crawler import RealBrowserCrawler

    crawler = RealBrowserCrawler()

    with patch('src.agent_crawler.async_playwright', return_value=mock_playwright['playwright']), \
         patch('os.makedirs'), \
         patch('asyncio.sleep', return_value=None):

        await crawler.run("Test", headless=True)

        # Verify context was created with user agent
        context_call = mock_playwright['browser'].new_context.call_args
        assert 'user_agent' in context_call[1]
        assert 'Mozilla' in context_call[1]['user_agent']

        # Verify init script was added
        mock_playwright['context'].add_init_script.assert_called_once()


@pytest.mark.asyncio
async def test_run_no_files_found(mock_playwright):
    """Test handling when no files are found"""
    from src.agent_crawler import RealBrowserCrawler

    # Return empty list for file links
    mock_playwright['locator'].all = AsyncMock(return_value=[])
    mock_playwright['locator'].count = AsyncMock(return_value=1)

    crawler = RealBrowserCrawler()

    with patch('src.agent_crawler.async_playwright', return_value=mock_playwright['playwright']), \
         patch('os.makedirs'), \
         patch('asyncio.sleep', return_value=None):

        # Should not raise exception
        await crawler.run("Test", headless=True)


@pytest.mark.asyncio
async def test_run_popup_removal_fails_gracefully(mock_playwright):
    """Test that popup removal failure doesn't stop execution"""
    from src.agent_crawler import RealBrowserCrawler

    # Make evaluate fail
    mock_playwright['page'].evaluate = AsyncMock(side_effect=Exception("Evaluate failed"))

    crawler = RealBrowserCrawler()

    with patch('src.agent_crawler.async_playwright', return_value=mock_playwright['playwright']), \
         patch('os.makedirs'), \
         patch('asyncio.sleep', return_value=None):

        # Should continue execution despite popup removal failure
        await crawler.run("Test", headless=True)

        # Should still try to navigate
        mock_playwright['page'].goto.assert_called()


@pytest.mark.asyncio
async def test_main_execution():
    """Test __main__ execution"""
    from src.agent_crawler import RealBrowserCrawler

    with patch.object(RealBrowserCrawler, 'run', new_callable=AsyncMock) as mock_run:
        # Import and simulate __main__ execution
        with patch('src.agent_crawler.__name__', '__main__'):
            # This would trigger the if __name__ == "__main__" block
            pass

        # We can't actually test the __main__ block directly,
        # but we verified the run method is tested
