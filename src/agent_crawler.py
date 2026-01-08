
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

    async def run(self, school_name: str = "동도중학교", headless: bool = True):
        """
        Run the browser crawler to search and download school files.

        Args:
            school_name: Name of the school to search for
            headless: Run in headless mode (True) or visible mode (False for debugging)
        """
        logger.info(f"Starting Real Browser Agent for: {school_name}")
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        download_dir = os.path.join(base_dir, "downloads", "real")
        debug_dir = os.path.join(base_dir, "debug_artifacts")
        os.makedirs(download_dir, exist_ok=True)
        os.makedirs(debug_dir, exist_ok=True)

        async with async_playwright() as p:
            # Launch Browser with Anti-Detection Args
            browser = await p.chromium.launch(
                headless=headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-infobars",
                    "--window-size=1920,1080",
                    "--start-maximized",
                    "--disable-dev-shm-usage",  # Overcome limited resource problems
                ]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                locale="ko-KR",
                timezone_id="Asia/Seoul",
                accept_downloads=True
            )
            
            # Anti-detection script
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            page = await context.new_page()

            try:
                # 1. Go to Home
                logger.info(f"Navigating to {self.BASE_URL}...")
                await page.goto(self.BASE_URL, timeout=120000, wait_until="load")

                # CRITICAL: Wait for page to fully stabilize after any redirects
                await page.wait_for_load_state("load", timeout=30000)
                await asyncio.sleep(2)

                # Safe Popup Handling: Direct DOM Removal (more reliable than CSS)
                logger.info("Removing popups via DOM manipulation...")
                try:
                    await page.evaluate("""
                        () => {
                            // Remove common popup elements
                            const selectors = ['.layerpopup', 'div[id*="popup"]', '.dimmed', '.popup_wrap'];
                            selectors.forEach(selector => {
                                document.querySelectorAll(selector).forEach(el => el.remove());
                            });
                        }
                    """)
                    logger.info("Popup removal completed.")
                except Exception as popup_err:
                    logger.warning(f"Popup removal failed (non-critical): {popup_err}")

                await asyncio.sleep(2) 
                
                # Debug: Screenshot
                await page.screenshot(path=os.path.join(debug_dir, "01_homepage.png"))
                
                # 2. Search
                logger.info(f"Searching for {school_name}...")

                # Wait for search input to be available
                try:
                    search_input = page.locator("input#SEARCH_KEYWORD")
                    await search_input.wait_for(state="visible", timeout=10000)

                    # Human-like interaction
                    await search_input.first.click()
                    await asyncio.sleep(0.5)
                    await search_input.first.fill(school_name)
                    await asyncio.sleep(0.8)
                    await page.keyboard.press("Enter")
                    logger.info("Search submitted.")

                except Exception as exc:
                    logger.error(f"Search interaction failed: {exc}")
                    await page.screenshot(path=os.path.join(debug_dir, "error_search.png"))
                    return

                # Wait for results page to load completely
                await page.wait_for_load_state("load", timeout=60000)
                await asyncio.sleep(3)
                await page.screenshot(path=os.path.join(debug_dir, "02_results.png"))

                # Debug: Save HTML to understand structure
                html_content = await page.content()
                with open(os.path.join(debug_dir, "02_results.html"), "w", encoding="utf-8") as f:
                    f.write(html_content)
                logger.info("Saved HTML for debugging")

                # 3. Click Result
                logger.info("Scanning for search results...")

                # The link opens in a new page/popup via JavaScript
                try:
                    # Find the school link (it's a JavaScript link)
                    result_link = page.locator(f"a[href*='searchSchul']:has-text('{school_name}')").first
                    await result_link.wait_for(state="visible", timeout=10000)

                    link_text = await result_link.inner_text()
                    logger.info(f"Found result link: {link_text}")

                    # Extract school ID from the onclick/href
                    school_id = await result_link.get_attribute("href")
                    logger.info(f"School link: {school_id}")

                    # Click - this may open a new page or navigate current page
                    await asyncio.sleep(1)

                    # Listen for potential new page (popup)
                    async with context.expect_page() as new_page_info:
                        await result_link.click()
                        try:
                            detail_page = await new_page_info.value
                            logger.info(f"New page opened: {detail_page.url}")
                            # Switch to new page
                            page = detail_page
                        except:
                            # No new page, check if current page navigated
                            logger.info("No new page, checking current page...")
                            pass

                    # Wait for detail page to load
                    await page.wait_for_load_state("load", timeout=60000)
                    await asyncio.sleep(3)
                    await page.screenshot(path=os.path.join(debug_dir, "03_detail.png"))
                    logger.info(f"Detail page URL: {page.url}")

                    # Save detail page HTML for analysis
                    detail_html = await page.content()
                    with open(os.path.join(debug_dir, "03_detail.html"), "w", encoding="utf-8") as f:
                        f.write(detail_html)

                    # 4. Select Year 2025
                    logger.info("Selecting Year 2025...")
                    try:
                        # Fix: Handle duplicate IDs or multiple elements
                        year_select = page.locator("#gsYear").first
                        await year_select.select_option(value="2025")
                        
                        # Fix: Strict mode violation for #gsYearBtn
                        await page.locator("#gsYearBtn").first.click()
                        
                        await page.wait_for_load_state("networkidle")
                        await asyncio.sleep(3)
                        logger.info("Year 2025 selected.")
                    except Exception as e:
                        logger.warning(f"Failed to set year to 2025 (might already be 2025 or different UI): {e}")

                    # 5. Targeted Download
                    targets = [
                        "교과별(학년별) 교수ㆍ학습 및 평가계획에 관한 사항",
                        "교과별 학업성취 사항"
                    ]

                    # Let's try to find tabs and click them to ensure links are visible
                    main_tabs = ["교육활동", "학업성취사항"]
                    for tab_name in main_tabs:
                        try:
                            tab = page.locator(f"a:has-text('{tab_name}')").first
                            if await tab.count() > 0:
                                logger.info(f"Clicking Tab: {tab_name}")
                                await tab.click()
                                await asyncio.sleep(2)
                        except Exception as e:
                            logger.warning(f"Failed to click tab {tab_name}: {e}")
                    
                    download_count = 0

                    for target_name in targets:
                        logger.info(f"Looking for target section: {target_name}")
                        
                        # Find the link for this section
                        # It usually calls loadGongSi
                        target_link = page.locator(f"a:has-text('{target_name}')")
                        
                        if await target_link.count() == 0:
                            logger.warning(f"Could not find link for {target_name}")
                            continue
                        
                        logger.info(f"Found link for {target_name}, clicking...")
                        
                        # Handle both Popup and Modal (Dynamic check)
                        initial_pages = context.pages
                        await target_link.first.click()
                        await asyncio.sleep(4) # Wait for action (popup or modal load)
                        
                        new_pages = context.pages
                        target_page = page # Default to current page (for modal)
                        is_popup = False

                        if len(new_pages) > len(initial_pages):
                            target_page = new_pages[-1]
                            is_popup = True
                            logger.info(f"Detected new popup window: {target_page.url}")
                            await target_page.wait_for_load_state("load")
                        else:
                            logger.info("No new window detected, assuming in-page modal/content update.")
                        
                        try:
                            # In the target page (popup or current), find files
                            # File links usually contain .hwp, .pdf or are in a specific file list
                            
                            # Wait for file list to appear
                            try:
                                await target_page.locator("a[href*='FileDown'], a:has-text('.hwp'), a:has-text('.pdf')").first.wait_for(state="visible", timeout=5000)
                            except:
                                logger.warning("No obvious file links found immediately.")

                            # Search for attachments
                            # The structure usually has a table with "첨부파일" (Attachment)
                            
                            files = await target_page.locator("a[href*='FileDown']").all() # Common pattern for gov sites
                            if len(files) == 0:
                                # Try generic extension search
                                files = []
                                all_links = await target_page.locator("a").all()
                                for link in all_links:
                                    try:
                                        href = await link.get_attribute("href")
                                        text = await link.inner_text()
                                        if href and ("down" in href.lower() or ".hwp" in text.lower() or ".pdf" in text.lower()):
                                             if "미리보기" not in text:
                                                files.append(link)
                                    except:
                                        pass
                            
                            logger.info(f"Found {len(files)} potential files in target context for {target_name}")
                            
                            for i, file_link in enumerate(files):
                                try:
                                    # Get filename hint
                                    text = await file_link.inner_text()
                                    if not text.strip():
                                        text = f"file_{i}"
                                    
                                    logger.info(f"Downloading: {text}")
                                    
                                    async with target_page.expect_download(timeout=30000) as download_info:
                                        await file_link.click()
                                        download = await download_info.value
                                        
                                        # Sanitize filename
                                        safe_filename = f"{target_name}_{download.suggested_filename}"
                                        save_path = os.path.join(download_dir, safe_filename)
                                        
                                        await download.save_as(save_path)
                                        logger.info(f"✓ Downloaded: {save_path}")
                                        download_count += 1
                                        await asyncio.sleep(1)
                                except Exception as dl_err:
                                    logger.error(f"Download failed: {dl_err}")
                            
                            if is_popup:
                                await target_page.close()
                            
                        except Exception as popup_err:
                            logger.error(f"Failed to handle content for {target_name}: {popup_err}")

                    if download_count > 0:
                        logger.info(f"🎉 SUCCESS: Downloaded {download_count} specific requested files!")
                    else:
                        logger.warning("No files were successfully downloaded for the requested targets.")

                except Exception as result_err:
                    logger.error(f"Failed to find or click search result: {result_err}")
                    await page.screenshot(path=os.path.join(debug_dir, "error_result.png"))

            except Exception as e:
                logger.error(f"Browser Agent Failed: {e}")
                await page.screenshot(path=os.path.join(debug_dir, "error.png"))
            finally:
                await browser.close()

if __name__ == "__main__":
    crawler = RealBrowserCrawler()
    asyncio.run(crawler.run())
