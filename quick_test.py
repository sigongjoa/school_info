#!/usr/bin/env python3
"""빠른 RAG 테스트"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "mathesis-common"))

from src.rag.integrated_pipeline import IntegratedRAGPipeline

print('=== 추가 질문 테스트 ===\n')

pipeline = IntegratedRAGPipeline(
    collection_name='school_info_test',
    persist_dir='./chroma_test'
)

questions = [
    '지필평가 비율은?',
    '프로젝트 학습을 하나요?',
    '자유학기제는 어떻게 평가하나요?'
]

for q in questions:
    answer = pipeline.query(q, k=2)
    print(f'Q: {q}')
    print(f'A: {answer.get("answer", "N/A")}')
    print(f'신뢰도: {answer.get("confidence", 0.0)}')
    if answer.get('key_facts'):
        print(f'핵심: {", ".join(answer["key_facts"][:2])}')
    print()
