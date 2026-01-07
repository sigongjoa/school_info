
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import uvicorn
import os
import logging

from src.crawler import SchoolInfoCrawler
from src.exceptions import SchoolNotFoundError

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="School Info Service (Node5)",
    description="Independent Microservice for Scraping and PDF Generation of School Data",
    version="1.0.0"
)

# Request Models
class CrawlRequest(BaseModel):
    year: int = 2025

# Service Instance
crawler = SchoolInfoCrawler("https://www.schoolinfo.go.kr")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "node5_school_info"}

@app.post("/schools/{school_code}/teaching-plans")
async def fetch_teaching_plans(school_code: str, req: CrawlRequest):
    """
    Trigger the crawler to download teaching plans (generation via Typst).
    Returns list of downloaded filenames.
    """
    try:
        files = await crawler.download_teaching_plans(school_code, req.year)
        # Return relative paths for download
        return {"school_code": school_code, "files": [os.path.basename(f) for f in files]}
    except Exception as e:
        logger.error(f"Crawl failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/downloads/{school_code}/{year}/{filename}")
def download_file(school_code: str, year: str, filename: str):
    """
    Serve the downloaded PDF files.
    """
    # Security: In prod, validate paths to prevent traversal
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "downloads", school_code, year, "teaching_plans", filename)
    
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/pdf", filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=True)
