import logging
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from mathesis_core.db.hierarchical_chroma import HierarchicalChromaStore
from mathesis_core.llm.clients import OllamaClient

from .parser import PDFTableParser
from .enhanced_json_generator import EnhancedJSONGenerator

logger = logging.getLogger(__name__)

class IntegratedRAGPipeline:
    """
    통합 RAG 파이프라인:
    1. PDF → Enhanced JSON
    2. JSON → Hierarchical Vector Store
    3. 질문 → Parent Context 검색 → 답변 생성
    4. JSON Export (웹 LLM용)
    """

    def __init__(
        self,
        collection_name: str = "school_info_v2",
        ollama_base_url: str = "http://localhost:11434",
        ollama_model: str = "llama3:latest",
        persist_dir: str = "./chroma_hierarchical"
    ):
        # LLM 클라이언트
        self.ollama = OllamaClient(
            base_url=ollama_base_url,
            model=ollama_model
        )

        # Hierarchical Vector Store
        self.vector_store = HierarchicalChromaStore(
            collection_prefix=collection_name,
            ollama_client=self.ollama,
            persist_dir=persist_dir
        )

        # PDF Parser
        self.pdf_parser = PDFTableParser()

        # JSON Generator
        self.json_generator = EnhancedJSONGenerator()

        # Enhanced JSON 저장소 (export용)
        self.json_storage: Dict[str, dict] = {}

    def ingest_pdf(
        self,
        pdf_path: str,
        metadata: dict
    ) -> dict:
        """
        PDF 파일을 처리하여 RAG 시스템에 색인

        Args:
            pdf_path: PDF 파일 경로
            metadata: {school_code, school_name, year, grade, subject, semester}

        Returns:
            {
                "document_id": str,
                "enhanced_json_path": str,
                "chunks_added": int
            }
        """
        logger.info(f"Ingesting PDF: {pdf_path}")

        # 1. PDF → Markdown
        markdown_text = self.pdf_parser.parse(pdf_path)
        if not markdown_text:
            raise ValueError(f"Failed to parse PDF: {pdf_path}")

        # 2. Markdown → Enhanced JSON
        enhanced_json = self.json_generator.generate_from_markdown(
            markdown_text,
            metadata
        )

        doc_id = enhanced_json["document_metadata"]["document_id"]
        logger.info(f"Generated enhanced JSON for document: {doc_id}")

        # 3. Enhanced JSON 저장 (export용)
        self.json_storage[doc_id] = enhanced_json

        # 4. JSON 파일로 저장
        output_dir = Path("./enhanced_jsons")
        output_dir.mkdir(exist_ok=True)
        json_path = output_dir / f"{doc_id}.json"

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_json, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved enhanced JSON: {json_path}")

        # 5. Vector Store에 색인
        chunks_added = self.vector_store.add_hierarchical_document(enhanced_json)

        logger.info(f"Added {chunks_added} chunks to vector store")

        return {
            "document_id": doc_id,
            "enhanced_json_path": str(json_path),
            "chunks_added": chunks_added
        }

    def query(
        self,
        question: str,
        k: int = 3,
        filters: Optional[Dict[str, str]] = None
    ) -> dict:
        """
        질문에 대한 답변 생성 (Hierarchical Retrieval 사용)

        Args:
            question: 사용자 질문
            k: 검색할 문서 수
            filters: 메타데이터 필터 (예: {"year": "2025", "grade": "1"})

        Returns:
            {
                "answer": str,
                "sources": List[dict],
                "parent_contexts": List[str]
            }
        """
        # 1. Parent Context 검색
        search_result = self.vector_store.query_with_parent_context(
            question=question,
            k=k,
            use_hybrid=True
        )

        matched_children = search_result["matched_children"]
        parent_contexts = search_result["parent_contexts"]

        if not parent_contexts:
            return {
                "answer": "관련 정보를 찾을 수 없습니다.",
                "sources": [],
                "parent_contexts": []
            }

        # 2. Parent Context 결합
        context_str = "\n\n---\n\n".join([
            f"[출처: {p['metadata'].get('section_title', 'Unknown')}]\n{p['text']}"
            for p in parent_contexts
        ])

        # 3. LLM 답변 생성
        system_prompt = """당신은 교육 데이터 전문가입니다.
제공된 문맥을 바탕으로 학생/학부모가 이해하기 쉽게 답변하십시오.

**중요 규칙**:
1. 제공된 문맥에 있는 사실만 사용하십시오
2. 숫자나 비율은 정확히 인용하십시오
3. 출처를 명시하십시오 (예: "평가 계획에 따르면...")
4. 답변할 수 없으면 솔직히 "정보가 부족합니다"라고 하십시오

**답변 형식** (JSON):
{
  "answer": "한국어 답변",
  "key_facts": ["사실1", "사실2"],
  "confidence": 0.95
}"""

        user_prompt = f"""질문: {question}

참고 자료:
{context_str}"""

        try:
            response_text = self.ollama.generate(
                prompt=user_prompt,
                system=system_prompt,
                format="json",
                temperature=0.1
            )

            response_json = json.loads(response_text)
        except json.JSONDecodeError:
            response_json = {
                "answer": response_text,
                "key_facts": [],
                "confidence": 0.5
            }
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            response_json = {
                "answer": f"답변 생성 중 오류가 발생했습니다: {e}",
                "key_facts": [],
                "confidence": 0.0
            }

        # 4. 출처 정보 추가
        sources = [
            {
                "section_title": p["metadata"].get("section_title"),
                "school_name": p["metadata"].get("school_name"),
                "year": p["metadata"].get("year"),
                "document_id": p["metadata"].get("document_id")
            }
            for p in parent_contexts
        ]

        return {
            **response_json,
            "sources": sources,
            "parent_contexts": [p["text"][:200] + "..." for p in parent_contexts]
        }

    def export_json(self, document_id: str) -> Optional[dict]:
        """
        웹 LLM용 Enhanced JSON 내보내기

        Args:
            document_id: 문서 ID

        Returns:
            Enhanced JSON 딕셔너리
        """
        return self.json_storage.get(document_id)

    def export_all_jsons(self) -> Dict[str, dict]:
        """모든 문서의 Enhanced JSON 내보내기"""
        return self.json_storage.copy()

    def list_documents(self) -> List[dict]:
        """색인된 문서 목록"""
        docs = []
        for doc_id, json_data in self.json_storage.items():
            metadata = json_data["document_metadata"]
            docs.append({
                "document_id": doc_id,
                "school_name": metadata.get("school_name"),
                "year": metadata.get("year"),
                "grade": metadata.get("grade"),
                "subject": metadata.get("subject"),
                "section_count": metadata.get("section_count"),
                "table_count": metadata.get("table_count")
            })
        return docs
