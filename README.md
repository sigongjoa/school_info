# Node6: School Info (학교 정보 RAG 시스템)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.4-FF6F00.svg)](https://www.trychroma.com/)

---

## 📋 Overview

**School Info Service**는 학교 정보를 크롤링하고, RAG (Retrieval-Augmented Generation) 시스템을 통해 지능형 질의응답을 제공하는 마이크로서비스입니다. schoolinfo.go.kr에서 학교 데이터를 수집하고, ChromaDB 기반 벡터 DB에 색인하여 자연어 질문에 정확한 답변을 제공합니다.

### 핵심 기능

1. **학교 데이터 크롤링**
   - schoolinfo.go.kr 자동 크롤링
   - 교육계획서 (Teaching Plans) PDF 다운로드
   - Playwright 기반 브라우저 자동화

2. **RAG 시스템**
   - ChromaDB 벡터 DB 기반 시맨틱 검색
   - 계층적 청크 분할 (Hierarchical Chunking)
   - Ollama LLM 통합 (로컬 실행)
   - 컨텍스트 기반 답변 생성

3. **웹 LLM 지원**
   - Enhanced JSON 내보내기
   - 웹 브라우저 내 LLM 실행 지원
   - 오프라인 질의응답 가능

4. **Mathesis Core 통합**
   - 공유 모델 및 유틸리티 사용
   - 표준화된 로깅 및 예외 처리
   - gRPC/MCP 통신 지원

### 기술적 차별점

- ✅ **자동화된 크롤링**: Playwright 기반 실시간 학교 데이터 수집
- ✅ **고급 RAG**: 계층적 청크 분할 및 메타데이터 필터링
- ✅ **로컬 LLM**: Ollama를 통한 완전 로컬 실행 (API 비용 $0)
- ✅ **웹 LLM 호환**: 브라우저 내 LLM 실행 지원
- ✅ **마이크로서비스 아키텍처**: RESTful API, gRPC, MCP 지원

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Client Application                         │
│         학교 정보 조회 → RAG 질의 → 답변 수신                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP REST API
┌───────────────────────────▼─────────────────────────────────────┐
│                   FastAPI Backend (Node6)                       │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────┐   │
│  │   Crawler      │→ │  PDF Parser    │→ │   RAG Engine    │   │
│  │ (Playwright)   │  │  (PyMuPDF)     │  │  (ChromaDB)     │   │
│  └────────────────┘  └────────────────┘  └─────────────────┘   │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────┐   │
│  │  LLM Service   │  │  JSON Export   │  │   gRPC/MCP      │   │
│  │   (Ollama)     │  │ (Web LLM)      │  │   (Optional)    │   │
│  └────────────────┘  └────────────────┘  └─────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────▼────────────┐
                │   Mathesis Core         │
                │  - Shared Models        │
                │  - Logging Utils        │
                │  - gRPC Proto Defs      │
                └─────────────────────────┘
```

**데이터 흐름**:
1. 클라이언트가 학교 코드로 크롤링 요청
2. Playwright로 schoolinfo.go.kr 크롤링
3. PDF 다운로드 및 파싱 (PyMuPDF)
4. 텍스트 청크 분할 및 임베딩 생성
5. ChromaDB에 벡터 저장
6. 자연어 질문 → 벡터 검색 → LLM 답변 생성
7. Enhanced JSON 내보내기 (웹 LLM용)

---

## 🚀 Quick Start

### 전제 조건

- Python 3.11+
- Ollama (로컬 LLM)
- Playwright (크롤링)
- ChromaDB (벡터 DB)

### 설치 및 실행

#### 1. 환경 변수 설정

```bash
cd /mnt/d/progress/mathesis/node6_school_info
```

`.env` 파일 생성:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8005
ENVIRONMENT=development

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# ChromaDB Configuration
CHROMA_PERSIST_DIR=./chroma_hierarchical
CHROMA_COLLECTION_NAME=school_info_v2

# Crawler Configuration
CRAWLER_BASE_URL=https://www.schoolinfo.go.kr
CRAWLER_TIMEOUT=30000
DOWNLOADS_DIR=./downloads

# RAG Configuration
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K=3

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

#### 2. Playwright 설치

```bash
# Playwright 및 브라우저 설치
pip install playwright
playwright install

# 또는 특정 브라우저만 설치
playwright install chromium
```

#### 3. Python 가상환경 및 패키지 설치

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

#### 4. Ollama 설치 및 모델 다운로드

```bash
# Ollama 설치 (Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Llama 3.1 8B 모델 다운로드
ollama pull llama3.1:8b

# Ollama 서버 시작
ollama serve
```

#### 5. Backend 서버 실행

```bash
# 개발 모드
python main.py

# 또는 uvicorn 직접 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8005
```

---

## 📡 API Endpoints

### School Crawling (학교 크롤링)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/schools/{school_code}/teaching-plans` | 학교 교육계획서 크롤링 및 다운로드 |
| GET | `/downloads/{school_code}/{year}/{filename}` | 다운로드된 PDF 파일 제공 |

**Example Request**:
```bash
curl -X POST "http://localhost:8005/schools/7001234/teaching-plans" \
  -H "Content-Type: application/json" \
  -d '{"year": 2025}'
```

**Example Response**:
```json
{
  "school_code": "7001234",
  "files": [
    "교육계획서_2025_1학기.pdf",
    "교육계획서_2025_2학기.pdf"
  ]
}
```

### RAG System (질의응답)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/rag/ingest` | PDF 문서를 RAG 시스템에 색인 |
| POST | `/rag/query` | RAG 시스템에 질문 |
| GET | `/rag/documents` | 색인된 문서 목록 조회 |
| GET | `/rag/export/{document_id}` | Enhanced JSON 다운로드 (웹 LLM용) |
| GET | `/rag/export-all` | 모든 문서의 Enhanced JSON 다운로드 |

**Example: Ingest PDF**
```bash
curl -X POST "http://localhost:8005/rag/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_path": "/path/to/document.pdf",
    "school_code": "7001234",
    "school_name": "서울고등학교",
    "year": "2025",
    "grade": "1",
    "subject": "mathematics",
    "semester": "1"
  }'
```

**Example: Query RAG**
```bash
curl -X POST "http://localhost:8005/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "1학년 1학기 수학 교육과정의 핵심 내용은?",
    "k": 3
  }'
```

**Example Response**:
```json
{
  "question": "1학년 1학기 수학 교육과정의 핵심 내용은?",
  "answer": "1학년 1학기 수학 교육과정의 핵심 내용은 다음과 같습니다:\n1. 집합과 명제\n2. 함수와 그래프\n3. 경우의 수",
  "sources": [
    {
      "content": "1학년 1학기 수학은 집합, 명제, 함수를 다룹니다...",
      "metadata": {
        "school_code": "7001234",
        "grade": "1",
        "semester": "1",
        "page": 15
      }
    }
  ],
  "confidence": 0.92
}
```

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | API 상태 확인 |

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.109.0
- **Vector DB**: ChromaDB 0.4
- **LLM**: Ollama (Llama 3.1 8B)
- **Crawler**: Playwright
- **PDF Parser**: PyMuPDF (fitz)
- **Embeddings**: sentence-transformers

### RAG Pipeline
- **Chunking**: Hierarchical (문단 → 문장)
- **Embedding**: paraphrase-multilingual-mpnet-base-v2
- **Retrieval**: ChromaDB 시맨틱 검색
- **Generation**: Ollama LLM

### Infrastructure
- **Container**: Docker (optional)
- **Logging**: Python logging

---

## 🧪 Testing

### RAG 파이프라인 테스트

```bash
# RAG 파이프라인 전체 테스트
python test_rag_pipeline.py

# Enhanced RAG 테스트
python test_enhanced_rag.py

# API 테스트
bash test_api.sh
```

### 크롤러 테스트

```bash
# MSA 크롤러 테스트
python test_msa_crawl.py
```

### 시각화

```bash
# RAG 결과 시각화
python visualize_result.py
```

---

## 📚 Documentation

| 문서 | 설명 |
|------|------|
| [Enhanced RAG 가이드](./docs/ENHANCED_RAG_GUIDE.md) | RAG 시스템 상세 가이드 |
| [School Info Service 명세](./docs/school_info_service.md) | 서비스 아키텍처 및 명세 |
| [Notion MSA 설계](./docs/NOTION_MSA_DESIGN.md) | 마이크로서비스 설계 문서 |
| [RAG README](./README_RAG.md) | RAG 시스템 개요 |
| [API 문서](http://localhost:8005/docs) | FastAPI 자동 생성 Swagger UI |

---

## 🔧 Troubleshooting

### Playwright 설치 오류

```bash
# 권한 오류 시
playwright install --with-deps

# 특정 브라우저만 설치
playwright install chromium

# 헤드리스 모드 테스트
python src/agent_crawler.py
```

### ChromaDB 초기화 오류

```bash
# ChromaDB 디렉토리 삭제 및 재생성
rm -rf chroma_hierarchical
python -c "from src.rag.integrated_pipeline import IntegratedRAGPipeline; IntegratedRAGPipeline()"
```

### Ollama 연결 오류

```bash
# Ollama 서버 상태 확인
curl http://localhost:11434/api/tags

# Ollama 재시작
killall ollama
ollama serve

# 모델 재다운로드
ollama pull llama3.1:8b
```

### PDF 파싱 오류

```bash
# PyMuPDF 재설치
pip uninstall pymupdf
pip install pymupdf

# PDF 파일 권한 확인
chmod 644 /path/to/document.pdf
```

더 많은 문제 해결: [GitHub Issues](https://github.com/your-repo/mathesis/issues)

---

## 📊 Development Status

| 구성 요소 | 상태 | 비고 |
|----------|------|------|
| 크롤러 (Playwright) | ✅ 완료 | 실시간 크롤링 |
| PDF 파싱 | ✅ 완료 | PyMuPDF 통합 |
| ChromaDB 통합 | ✅ 완료 | 벡터 DB |
| RAG 파이프라인 | ✅ 완료 | 계층적 청크 |
| Ollama LLM | ✅ 완료 | 로컬 실행 |
| Enhanced JSON | ✅ 완료 | 웹 LLM 지원 |
| REST API | ✅ 완료 | FastAPI |
| gRPC/MCP | 🚧 계획 | 마이크로서비스 통신 |

---

## 🤝 Contributing

이 프로젝트는 교육 기술 발전을 위한 오픈소스입니다. 기여를 환영합니다!

### 우선 순위 기여 영역

1. **크롤러 안정화** (Python)
   - 크롤링 오류 복구 로직
   - 다양한 학교 사이트 지원
   - 증분 업데이트 (Incremental Update)

2. **RAG 성능 개선** (Python)
   - Re-ranking 알고리즘
   - Query expansion
   - Hybrid search (벡터 + 키워드)

3. **웹 LLM 최적화** (JavaScript/TypeScript)
   - 클라이언트 사이드 LLM 통합
   - JSON 압축 및 최적화
   - 오프라인 모드 지원

---

## 📅 Roadmap

### Phase 1: 기본 기능 (완료)
- [x] 크롤러 구현 (Playwright)
- [x] PDF 파싱 및 텍스트 추출
- [x] ChromaDB 통합
- [x] 기본 RAG 파이프라인
- [x] Ollama LLM 통합

### Phase 2: 고도화 (진행 중)
- [x] 계층적 청크 분할
- [x] Enhanced JSON 내보내기
- [ ] gRPC/MCP 서버 구현
- [ ] Re-ranking 알고리즘
- [ ] 멀티모달 지원 (이미지)

### Phase 3: 확장 (계획)
- [ ] 다중 학교 동시 크롤링
- [ ] 실시간 업데이트 알림
- [ ] 대시보드 UI
- [ ] 클라우드 배포
- [ ] 웹 LLM 완전 통합

---

## 📖 Usage Examples

### 1. 학교 데이터 크롤링

```python
import requests

# 학교 교육계획서 크롤링
response = requests.post(
    "http://localhost:8005/schools/7001234/teaching-plans",
    json={"year": 2025}
)

result = response.json()
print(f"다운로드된 파일: {result['files']}")
```

### 2. PDF 색인 및 질의

```python
# PDF를 RAG 시스템에 색인
response = requests.post(
    "http://localhost:8005/rag/ingest",
    json={
        "pdf_path": "/path/to/document.pdf",
        "school_code": "7001234",
        "school_name": "서울고등학교",
        "year": "2025",
        "grade": "1",
        "subject": "mathematics",
        "semester": "1"
    }
)

# 질문
response = requests.post(
    "http://localhost:8005/rag/query",
    json={
        "question": "1학년 수학 교육목표는?",
        "k": 3
    }
)

answer = response.json()
print(f"답변: {answer['answer']}")
print(f"신뢰도: {answer['confidence']}")
```

### 3. 웹 LLM용 JSON 내보내기

```python
# 모든 문서를 Enhanced JSON으로 내보내기
response = requests.get("http://localhost:8005/rag/export-all")
enhanced_jsons = response.json()

# 웹 브라우저에서 사용
# <script src="web-llm.js"></script>
# <script>
#   const data = enhanced_jsons;
#   // 웹 LLM 초기화 및 질의
# </script>
```

---

## 📜 License

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 📞 Contact

- **프로젝트 관리자**: Mathesis Team
- **이슈 트래커**: [GitHub Issues](https://github.com/your-repo/mathesis/issues)
- **메인 프로젝트**: [Mathesis](../README.md)

---

## 🙏 Acknowledgments

이 프로젝트는 다음 오픈소스 프로젝트들을 기반으로 합니다:

- [ChromaDB](https://www.trychroma.com/) - 벡터 데이터베이스
- [Ollama](https://ollama.ai/) - 로컬 LLM
- [Playwright](https://playwright.dev/) - 브라우저 자동화
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF 파싱
- [FastAPI](https://fastapi.tiangolo.com/) - 웹 프레임워크
- [sentence-transformers](https://www.sbert.net/) - 텍스트 임베딩

---

**Last Updated**: 2026-01-10
**Version**: 1.0.0
**Node Type**: Microservice (Backend)
