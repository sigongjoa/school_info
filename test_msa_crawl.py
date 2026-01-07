
import asyncio
import os
from src.crawler import SchoolInfoCrawler

async def main():
    print("=== Testing Node 5 MSA Service (Standalone) ===")
    crawler = SchoolInfoCrawler("https://www.schoolinfo.go.kr")
    year = 2025

    # 1. Test Dongdo Middle School
    code1 = "B100000662"
    print(f"\n[1/2] Crawling Dongdo Middle School ({code1})...")
    files1 = await crawler.download_teaching_plans(code1, year)
    print(f" -> Downloaded {len(files1)} files for Dongdo.")
    for f in files1:
        print(f"    - {os.path.basename(f)}")

    # 2. Test Neungin Middle School
    code2 = "D100000999"
    print(f"\n[2/2] Crawling Neungin Middle School ({code2})...")
    files2 = await crawler.download_teaching_plans(code2, year)
    print(f" -> Downloaded {len(files2)} files for Neungin.")
    
    # 3. Generate Organized AI Report (RAG)
    print("\n[3/3] Generating AI Organized Reports...")
    from src.rag_service import SchoolRAGService
    rag = SchoolRAGService()

    # Dongdo Report
    d_data = crawler._get_fallback_data(code1)
    d_report = await rag.summarize_school(d_data, files1)
    print(f"\n--- Dongdo Organized Report ---\n{d_report[:100]}...\n-------------------------------")

    # Neungin Report
    n_data = crawler._get_fallback_data(code2)
    n_report = await rag.summarize_school(n_data, files2)
    print(f"\n--- Neungin Organized Report ---\n{n_report[:100]}...\n--------------------------------")

if __name__ == "__main__":
    asyncio.run(main())
