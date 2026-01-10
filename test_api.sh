#!/bin/bash
# FastAPI RAG 엔드포인트 테스트

echo "=== FastAPI RAG API 테스트 ==="
echo ""

BASE_URL="http://localhost:8005"

echo "1. Health Check"
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""

echo "2. 문서 목록 조회"
curl -s "$BASE_URL/rag/documents" | python3 -m json.tool
echo ""

echo "3. RAG 질의"
curl -s -X POST "$BASE_URL/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "수학 수행평가 비율은 얼마인가요?", "k": 2}' \
  | python3 -m json.tool | head -20
echo ""

echo "4. Enhanced JSON Export (웹 LLM용)"
DOC_ID="doc_B100000662_2025_1_mathematics_2"
echo "Exporting: $DOC_ID"
curl -s "$BASE_URL/rag/export/$DOC_ID" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"✓ 문서 ID: {data['document_metadata']['document_id']}\")
print(f\"✓ 학교: {data['document_metadata']['school_name']}\")
print(f\"✓ 섹션: {data['document_metadata']['section_count']}개\")
print(f\"✓ 테이블: {data['document_metadata']['table_count']}개\")
print(f\"✓ 크기: {len(json.dumps(data))} bytes\")
"
echo ""

echo "=== 테스트 완료 ==="
