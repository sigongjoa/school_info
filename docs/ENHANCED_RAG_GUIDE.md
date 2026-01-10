# Enhanced RAG System 사용 가이드

## 🎯 개요

교육 데이터(PDF)를 처리하여:
1. **로컬 LLM RAG 시스템**에서 질의응답
2. **웹 LLM**(Claude, GPT 등)에서 사용 가능한 **Enhanced JSON** 다운로드

---

## 📦 구성 요소

### 1. Enhanced JSON Generator
- PDF → Markdown → **계층 구조 JSON**
- `structured_data`: 숫자/비율 자동 추출
- `queryable_facts`: 자주 묻는 질문 Q&A 생성
- Parent-Child 관계 설정

### 2. Hierarchical Vector Store
- **Child Collection**: 작은 청크 (테이블, 섹션) - 검색용
- **Parent Collection**: 큰 문맥 (전체 섹션) - 생성용
- **Korean BM25**: 형태소 분석 기반 키워드 검색
- **Hybrid Search**: Vector + BM25 + RRF

### 3. Integrated RAG Pipeline
- PDF 색인 → 검색 → 답변 생성 → JSON Export

---

## 🚀 빠른 시작

### 의존성 설치

```bash
cd /mnt/d/progress/mathesis/node6_school_info

# 필수 패키지
pip install pdfplumber rank-bm25 chromadb

# 선택 (한국어 형태소 분석)
pip install konlpy python-mecab-ko
```

### Ollama 설치 및 실행 (로컬 RAG용)

```bash
# 1. Ollama 설치
curl -fsSL https://ollama.com/install.sh | sh

# 2. 임베딩 모델 다운로드
ollama pull nomic-embed-text:latest

# 3. 생성 모델 다운로드 (선택)
ollama pull llama3.1:8b

# 4. Ollama 서버 확인
curl http://localhost:11434/api/version
```

---

## 📝 사용 방법

### 방법 1: Python 스크립트

```python
from src.rag.integrated_pipeline import IntegratedRAGPipeline

# 1. 파이프라인 초기화
pipeline = IntegratedRAGPipeline(
    collection_name="school_info",
    ollama_base_url="http://localhost:11434",
    persist_dir="./chroma_hierarchical"
)

# 2. PDF 색인
metadata = {
    "school_code": "B100000662",
    "school_name": "동도중학교",
    "year": "2025",
    "grade": "1",
    "subject": "mathematics",
    "semester": "2"
}

result = pipeline.ingest_pdf("path/to/file.pdf", metadata)
print(f"Document ID: {result['document_id']}")
print(f"Enhanced JSON: {result['enhanced_json_path']}")

# 3. 질의 (로컬 RAG)
answer = pipeline.query("수학 수행평가 비율은?", k=3)
print(answer['answer'])

# 4. Enhanced JSON Export (웹 LLM용)
json_data = pipeline.export_json(result['document_id'])
# json_data를 Claude/GPT에 전달
```

### 방법 2: FastAPI 서버

```bash
# 1. 서버 시작
python main.py
# → http://localhost:8005

# 2. PDF 색인
curl -X POST "http://localhost:8005/rag/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_path": "downloads/B100000662/2025/teaching_plans/plan.pdf",
    "school_code": "B100000662",
    "school_name": "동도중학교",
    "year": "2025",
    "grade": "1",
    "subject": "mathematics",
    "semester": "2"
  }'

# 3. 질의 (로컬 RAG)
curl -X POST "http://localhost:8005/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "수학 수행평가 비율은?", "k": 3}'

# 4. Enhanced JSON 다운로드 (웹 LLM용)
curl "http://localhost:8005/rag/export/doc_B100000662_2025_1_mathematics_2" > output.json

# 5. 모든 문서 JSON 다운로드
curl "http://localhost:8005/rag/export-all" > all_docs.json
```

---

## 🌐 웹 LLM에서 사용하기

### Claude (claude.ai)

```
1. Enhanced JSON 다운로드:
   curl http://localhost:8005/rag/export-all > school_data.json

2. Claude Code에서 업로드:
   - Attachments로 school_data.json 첨부

3. 프롬프트:
   "첨부된 JSON은 학교 평가 계획 데이터입니다.

   질문: 동도중학교 1학년 수학 수행평가 비율은?

   답변 시 structured_data를 우선 참조하고,
   출처(section_title, table_id)를 명시하세요."
```

### GPT (ChatGPT Plus)

```
1. Enhanced JSON 다운로드 (위와 동일)

2. GPT에 파일 업로드

3. 프롬프트:
   "You are analyzing Korean school evaluation plans.
   The attached JSON contains structured data from PDFs.

   Question: What is the performance evaluation ratio for 1st grade math?

   Use 'structured_data' field for precise values.
   Cite sources using 'section_title' and 'table_id'."
```

---

## 📊 Enhanced JSON 구조

```json
{
  "document_metadata": {
    "document_id": "doc_B100000662_2025_1_mathematics_2",
    "school_code": "B100000662",
    "school_name": "동도중학교",
    "year": "2025",
    "grade": "1",
    "subject": "mathematics",
    "semester": "2",
    "extraction_method": "pdfplumber",
    "page_count": 1,
    "section_count": 3,
    "table_count": 3
  },

  "sections": [
    {
      "section_id": "sec_002",
      "section_title": "2. 평가 계획",
      "section_type": "mixed",
      "page_number": 1,
      "content": "...",
      "tables": [
        {
          "table_id": "tbl_002",
          "table_caption": "평가 시기 및 평가 종류 및 반영 비율",
          "headers": ["평가 시기", "평가 종류", "반영 비율", "평가 내용"],
          "rows": [
            {
              "평가 시기": "4월 말",
              "평가 종류": "지필평가",
              "반영 비율": "30%",
              "평가 내용": "선택형 및 서답형 혼합"
            },
            {
              "평가 시기": "상시",
              "평가 종류": "수행평가",
              "반영 비율": "40%",
              "평가 내용": "포트폴리오, 주제 탐구 보고서"
            }
          ],
          "structured_data": {
            "반영_비율": [30, 30, 40],
            "평가_종류_list": ["지필평가", "수행평가"]
          },
          "queryable_facts": [
            {
              "question": "반영 비율은 얼마인가요?",
              "answer": "30%",
              "source": "table",
              "confidence": 1.0
            }
          ],
          "markdown": "| 평가 시기 | ... |",
          "parent_section_id": "sec_002"
        }
      ]
    }
  ],

  "rag_optimization": {
    "chunk_strategy": "section_based",
    "parent_document_id": "doc_B100000662_2025_1_mathematics_2",
    "supports_hierarchical_retrieval": true
  }
}
```

---

## 🔍 검색 전략

### Hybrid Search (Vector + BM25)

```python
# 질문: "수학 수행평가 비율은?"

# 1. Vector Search (의미 기반)
   → "평가", "수행", "비율" 의미 이해
   → "40%" 포함된 테이블 검색

# 2. BM25 Search (키워드 기반)
   → "수행평가" 형태소 분석
   → 정확한 용어 매칭

# 3. RRF Fusion
   → 두 검색 결과 결합
   → 가장 관련성 높은 Child 청크 반환

# 4. Parent Context 반환
   → Child가 속한 Parent (전체 섹션) 반환
   → LLM이 풍부한 문맥으로 답변 생성
```

---

## 🛠️ 트러블슈팅

### Ollama 연결 실패

```bash
# Ollama 재시작
sudo systemctl restart ollama

# 포트 확인
curl http://localhost:11434/api/version

# 수동 실행
ollama serve
```

### PDF 파싱 오류

```python
# 로그 확인
logging.basicConfig(level=logging.DEBUG)

# 특정 페이지만 파싱
parser = PDFTableParser()
with pdfplumber.open("file.pdf") as pdf:
    page = pdf.pages[0]
    tables = page.extract_tables()
    print(tables)
```

### 한국어 토크나이저 없음

```python
# Korean BM25 비활성화
from mathesis_core.db.korean_tokenizer import KoreanBM25

# 형태소 분석 없이 사용
bm25 = KoreanBM25(use_morphs=False)  # 공백 기반 토큰화
```

---

## 📈 성능 최적화

### 1. 임베딩 모델 선택

```python
# 기본 (빠름, 정확도 낮음)
"nomic-embed-text:latest"

# 한국어 특화 (로컬)
pip install sentence-transformers
model = "jhgan/ko-sroberta-multitask"

# 프론티어 (정확, 비용 발생)
OpenAI "text-embedding-3-large"
```

### 2. 청크 크기 조정

```python
# enhanced_json_generator.py

# 테이블별 분리 (현재 기본)
→ 검색 정확도 ↑, 문맥 ↓

# 섹션별 분리
→ 검색 정확도 ↓, 문맥 ↑
```

---

## 📚 API 레퍼런스

### POST /rag/ingest
PDF를 RAG 시스템에 색인

**Request:**
```json
{
  "pdf_path": "path/to/file.pdf",
  "school_code": "B100000662",
  "school_name": "동도중학교",
  "year": "2025",
  "grade": "1",
  "subject": "mathematics",
  "semester": "2"
}
```

**Response:**
```json
{
  "document_id": "doc_B100000662_2025_1_mathematics_2",
  "enhanced_json_path": "enhanced_jsons/doc_....json",
  "chunks_added": 15
}
```

### POST /rag/query
질의응답

**Request:**
```json
{
  "question": "수학 수행평가 비율은?",
  "k": 3
}
```

**Response:**
```json
{
  "answer": "동도중학교 1학년 수학 수행평가 비율은 40%입니다.",
  "key_facts": ["수행평가 40%", "지필평가 60%"],
  "confidence": 0.95,
  "sources": [...]
}
```

### GET /rag/export/{document_id}
Enhanced JSON 다운로드 (웹 LLM용)

**Response:** Enhanced JSON 전체

### GET /rag/export-all
모든 문서의 Enhanced JSON 다운로드

**Response:**
```json
{
  "doc_B100000662_2025_1_mathematics_2": {...},
  "doc_B100000662_2025_2_mathematics_2": {...}
}
```

---

## 🎓 사용 예시

### 로컬 개발 워크플로우

```bash
# 1. Ollama 실행
ollama serve

# 2. PDF 색인
python test_enhanced_rag.py

# 3. FastAPI 서버 시작
python main.py

# 4. 로컬 RAG 질의
curl -X POST http://localhost:8005/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question": "평가 방법은?"}'

# 5. Enhanced JSON 다운로드 (웹 LLM용)
curl http://localhost:8005/rag/export-all > for_claude.json

# 6. Claude에서 사용
# - for_claude.json 업로드
# - 질문 입력
```

---

## 🔗 관련 링크

- **Ollama**: https://ollama.com
- **ChromaDB**: https://docs.trychroma.com
- **pdfplumber**: https://github.com/jsvine/pdfplumber
- **konlpy**: https://konlpy.org

---

## ✅ 완료!

이제 당신은:
- ✅ 로컬 LLM RAG 시스템 운영 가능
- ✅ 웹 LLM(Claude/GPT)용 Enhanced JSON 생성 가능
- ✅ Hierarchical Retrieval로 검색 품질 향상
- ✅ 한국어 교육 데이터 특화 처리

**다음 단계**: 실제 프론티어 모델(Claude API, GPT API) 연동을 위한 `AdaptiveLLMRouter` 구현 (선택사항)
