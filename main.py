
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
import logging

from src.crawler import SchoolInfoCrawler
from src.exceptions import SchoolNotFoundError
from src.rag.integrated_pipeline import IntegratedRAGPipeline

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

# Service Instances
crawler = SchoolInfoCrawler("https://www.schoolinfo.go.kr")
rag_pipeline = IntegratedRAGPipeline(
    collection_name="school_info_v2",
    ollama_base_url="http://localhost:11434",
    persist_dir="./chroma_hierarchical"
)

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

# ============= RAG Endpoints =============

class IngestRequest(BaseModel):
    pdf_path: str
    school_code: str
    school_name: str
    year: str
    grade: Optional[str] = None
    subject: Optional[str] = "general"
    semester: Optional[str] = None

class QueryRequest(BaseModel):
    question: str
    k: int = 3

@app.post("/rag/ingest")
async def ingest_pdf(req: IngestRequest):
    """
    PDF를 RAG 시스템에 색인
    """
    try:
        metadata = {
            "school_code": req.school_code,
            "school_name": req.school_name,
            "year": req.year,
            "grade": req.grade,
            "subject": req.subject,
            "semester": req.semester
        }

        result = rag_pipeline.ingest_pdf(req.pdf_path, metadata)
        return result
    except Exception as e:
        logger.error(f"Ingest failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rag/query")
async def rag_query(req: QueryRequest):
    """
    RAG 시스템에 질문
    """
    try:
        answer = rag_pipeline.query(req.question, k=req.k)
        return answer
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rag/documents")
async def list_documents():
    """
    색인된 문서 목록
    """
    docs = rag_pipeline.list_documents()
    return {"documents": docs}

@app.get("/rag/export/{document_id}")
async def export_json(document_id: str):
    """
    웹 LLM용 Enhanced JSON 다운로드
    """
    json_data = rag_pipeline.export_json(document_id)
    if not json_data:
        raise HTTPException(status_code=404, detail="Document not found")

    return JSONResponse(content=json_data)

@app.get("/rag/export-all")
async def export_all_jsons():
    """
    모든 문서의 Enhanced JSON 다운로드 (웹 LLM용)
    """
    all_jsons = rag_pipeline.export_all_jsons()
    return JSONResponse(content=all_jsons)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=True)
