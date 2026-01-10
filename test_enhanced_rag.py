#!/usr/bin/env python3
"""
Enhanced RAG Pipeline 테스트 스크립트

사용법:
    python test_enhanced_rag.py
"""

import sys
import logging
from pathlib import Path

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# mathesis-common을 import path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "mathesis-common"))

from src.rag.integrated_pipeline import IntegratedRAGPipeline

def main():
    logger.info("=" * 60)
    logger.info("Enhanced RAG Pipeline 테스트")
    logger.info("=" * 60)

    # 1. 파이프라인 초기화
    logger.info("\n[1] RAG 파이프라인 초기화...")
    pipeline = IntegratedRAGPipeline(
        collection_name="school_info_test",
        ollama_base_url="http://localhost:11434",
        persist_dir="./chroma_test"
    )
    logger.info("✓ 파이프라인 초기화 완료")

    # 2. PDF 파일 찾기
    logger.info("\n[2] PDF 파일 검색...")
    pdf_dir = Path("downloads/B100000662/2025/teaching_plans")

    if not pdf_dir.exists():
        logger.warning(f"PDF 디렉토리 없음: {pdf_dir}")
        pdf_dir = Path("school_docs/B100000662/2025/teaching_plans")

    if not pdf_dir.exists():
        logger.error("PDF 파일을 찾을 수 없습니다!")
        logger.info("샘플 PDF를 다운로드하거나 경로를 확인하세요.")
        return

    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        logger.error("PDF 파일이 없습니다!")
        return

    logger.info(f"✓ {len(pdf_files)}개 PDF 파일 발견")

    # 3. PDF 색인 (첫 번째 파일만 테스트)
    test_pdf = pdf_files[0]
    logger.info(f"\n[3] PDF 색인: {test_pdf.name}")

    metadata = {
        "school_code": "B100000662",
        "school_name": "동도중학교",
        "year": "2025",
        "grade": "1",
        "subject": "mathematics",
        "semester": "2"
    }

    try:
        result = pipeline.ingest_pdf(str(test_pdf), metadata)
        logger.info(f"✓ 색인 완료:")
        logger.info(f"  - Document ID: {result['document_id']}")
        logger.info(f"  - Enhanced JSON: {result['enhanced_json_path']}")
        logger.info(f"  - Chunks Added: {result['chunks_added']}")
    except Exception as e:
        logger.error(f"색인 실패: {e}")
        import traceback
        traceback.print_exc()
        return

    # 4. 질문 테스트
    logger.info("\n[4] RAG 질문 테스트...")

    test_questions = [
        "수학 수행평가 비율은 얼마인가요?",
        "평가 시기는 언제인가요?",
        "교과 역량은 무엇인가요?"
    ]

    for idx, question in enumerate(test_questions, 1):
        logger.info(f"\n질문 {idx}: {question}")
        try:
            answer = pipeline.query(question, k=2)
            logger.info(f"답변: {answer.get('answer', 'N/A')}")
            logger.info(f"신뢰도: {answer.get('confidence', 0.0)}")
            if answer.get('key_facts'):
                logger.info(f"주요 사실: {answer['key_facts']}")
        except Exception as e:
            logger.error(f"질문 실패: {e}")

    # 5. Enhanced JSON Export 테스트
    logger.info("\n[5] Enhanced JSON Export 테스트...")
    doc_id = result['document_id']

    exported_json = pipeline.export_json(doc_id)
    if exported_json:
        logger.info(f"✓ Export 성공:")
        logger.info(f"  - Sections: {len(exported_json['sections'])}")
        logger.info(f"  - Tables: {exported_json['document_metadata']['table_count']}")

        # 샘플 테이블 출력
        if exported_json['sections']:
            first_section = exported_json['sections'][0]
            if first_section['tables']:
                first_table = first_section['tables'][0]
                logger.info(f"\n샘플 테이블:")
                logger.info(f"  제목: {first_table['table_caption']}")
                logger.info(f"  헤더: {first_table['headers']}")
                logger.info(f"  행 수: {len(first_table['rows'])}")
                if first_table['structured_data']:
                    logger.info(f"  구조화 데이터 키: {list(first_table['structured_data'].keys())}")

    else:
        logger.error("Export 실패")

    # 6. 문서 목록
    logger.info("\n[6] 색인된 문서 목록...")
    docs = pipeline.list_documents()
    logger.info(f"✓ 총 {len(docs)}개 문서")
    for doc in docs:
        logger.info(f"  - {doc['document_id']}: {doc['school_name']} ({doc['year']})")

    logger.info("\n" + "=" * 60)
    logger.info("테스트 완료!")
    logger.info("=" * 60)
    logger.info("\n웹 LLM에서 사용하려면:")
    logger.info(f"  GET http://localhost:8005/rag/export/{doc_id}")
    logger.info(f"  GET http://localhost:8005/rag/export-all")

if __name__ == "__main__":
    main()
