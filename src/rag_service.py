
import logging
from typing import List, Dict, Any
import random
import time
from .doc_processor import DocumentProcessor
from .models import SchoolData

logger = logging.getLogger(__name__)

from .rag.engine import RAGEngine

class SchoolRAGService:
    """
    Service for RAG-based analysis of school documents.
    Uses RAGEngine for Retrieval and Generation.
    """
    def __init__(self):
        # We might want to persist the engine or collection per school?
        # For simplicity, we use one collection for now.
        self.rag_engine = RAGEngine(collection_name="school_info_v1")

    async def summarize_school(self, school_data: SchoolData, docs: List[str]) -> str:
        """
        Ingests docs and generates a comprehensive summary using RAG.
        Returns a JSON string (for compatibility with previous signature, though ideally should be Dict).
        """
        logger.info(f"Analyzing {len(docs)} documents for {school_data.school_name}...")
        
        # 1. Ingest Documents
        total_chunks = 0
        for doc_path in docs:
            # Check if file exists
            if not os.path.exists(doc_path):
                logger.warning(f"Document not found: {doc_path}")
                continue
                
            count = self.rag_engine.ingest_file(
                doc_path, 
                metadata={"school_name": school_data.school_name, "year": "2025"}
            )
            total_chunks += count
            
        logger.info(f"Ingested {total_chunks} chunks.")
        
        if total_chunks == 0:
            return json.dumps({"error": "No content indexed", "answer": "문서를 분석할 수 없습니다."})

        # 2. Query
        query_text = f"{school_data.school_name}의 2025학년도 교육 목표, 주요 수학 평가 계획, 자유학기제 운영 방식을 요약해줘."
        
        result = self.rag_engine.query(query_text, k=5)
        
        # 3. Return Result
        # API expects string, so we dump the JSON result
        return json.dumps(result, ensure_ascii=False, indent=2)
