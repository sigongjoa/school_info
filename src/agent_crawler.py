
import asyncio
import logging
from playwright.async_api import async_playwright
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealBrowserCrawler:
    """
    Real Browser Agent using Playwright.
    Designed to bypass anti-bot protections by simulating a real user.
    
    Usage:
        python src/agent_crawler.py
        
    Note:
        Best run in a headful environment (local machine) to avoid detection.
    """
    BASE_URL = "https://www.schoolinfo.go.kr"

    async def run(self, school_name: str = "동도중학교"):
        logger.info(f"Starting Real Browser Agent for: {school_name}")
        
        async with async_playwright() as p:
            # Launch Browser (Try headless=False on local machine)
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                viewport={"width": 1280, "height": 720}
            )
            page = await context.new_page()

            try:
                # 1. Go to Home
                logger.info(f"Navigating to {self.BASE_URL}...")
                await page.goto(self.BASE_URL, timeout=60000)
                await page.wait_for_load_state("networkidle")
                
                # 2. Search
                logger.info(f"Searching for {school_name}...")
                search_input = page.locator("input[name='SEARCH_KWD'], input#SEARCH_GS_NM, .search_area input")
                
                if await search_input.count() > 0:
                    await search_input.first.fill(school_name)
                    await page.keyboard.press("Enter")
                    logger.info("Search submitted.")
                else:
                    logger.error("Could not find search input box.")
                    return

                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(3)

                # 3. Click Result
                logger.info("Scanning for search results...")
                
                # Robust Selector: Find link containing school name
                result_link = page.locator("a").filter(has_text=school_name).first
                
                if await result_link.count() > 0:
                    logger.info(f"Found result link: {await result_link.inner_text()}")
                    await result_link.click()
                    await page.wait_for_load_state("networkidle")
                    await asyncio.sleep(2)
                    
                    logger.info(f"Entered Detail Page: {await page.title()}")
                    
                    # 4. Find Teaching Plan Tab
                    full_text = await page.inner_text("body")
                    if "교수학습" in full_text:
                        logger.info("✅ Found '교수학습' (Teaching Plan) keyword in page.")
                    
                    # 5. Download Files
                    file_links = page.locator("a[href*='down'], a[href*='.pdf'], a[href*='.hwp']")
                    count = await file_links.count()
                    logger.info(f"Found {count} potential file download links.")
                    
                    if count > 0:
                        async with page.expect_download() as download_info:
                            try:
                                await file_links.first.click(timeout=5000)
                                download = await download_info.value
                                os.makedirs("downloads", exist_ok=True)
                                save_path = f"downloads/real_{download.suggested_filename}"
                                await download.save_as(save_path)
                                logger.info(f"🎉 SUCCESS: Downloaded real file to {save_path}")
                            except Exception as e:
                                logger.warning(f"Download click failed: {e}")
                else:
                    logger.warning("No specific school link found in results.")

            except Exception as e:
                logger.error(f"Browser Agent Failed: {e}")
            finally:
                await browser.close()

if __name__ == "__main__":
    crawler = RealBrowserCrawler()
    asyncio.run(crawler.run())
