# Mathesis MSA - Notion 워크스페이스 재설계

> MSA 아키텍처 기반 실제 운영/관리/유지보수 가능한 Notion 페이지 구조

**작성일**: 2026-01-08
**목적**: 기획서 중심 → 실무 운영 중심 구조로 전환

---

## 1. 설계 원칙

### 1.1 MSA 원칙 반영
- **Service Independence**: 각 서비스별 독립 페이지
- **Bounded Context**: 도메인별 명확한 경계
- **Database per Service**: DB 스키마 및 마이그레이션 관리
- **API Contract**: 서비스 간 인터페이스 명세
- **Observability**: 모니터링, 로깅, 장애 추적

### 1.2 실무 운영 중심
- **Issue Tracking**: 서비스별 버그/기능 요청 관리
- **Deployment Log**: 배포 이력 및 롤백 기록
- **API Documentation**: OpenAPI/Swagger 명세 연동
- **ADR (Architecture Decision Records)**: 기술 결정 이력
- **Runbook**: 장애 대응 매뉴얼

---

## 2. 재설계된 페이지 구조

```
📘 Mathesis Platform (Root)
│
├── 📊 Dashboard & Overview
│   ├── System Health Status
│   ├── Service Dependency Map
│   ├── Active Issues Summary
│   └── Deployment Timeline
│
├── 🏗️ MSA Architecture
│   ├── Architecture Overview (C4 Model)
│   ├── Service Map & Communication
│   ├── Data Flow & Integration
│   ├── Infrastructure & Deployment
│   └── ADR (Architecture Decision Records)
│       ├── ADR-001: MSA Adoption
│       ├── ADR-002: Common Library Strategy
│       └── ADR-003: Database per Service
│
├── 🔧 Services (각 서비스별 독립 관리)
│   │
│   ├── 🧠 Node 1: Logic Engine
│   │   ├── Service Overview
│   │   │   ├── Domain: 교육 이론 지식 그래프
│   │   │   ├── Tech Stack: Python, Neo4j, GROBID, Ollama
│   │   │   ├── Port: 8001
│   │   │   └── Status: ✅ Production
│   │   ├── API Documentation
│   │   │   ├── Swagger URL: http://localhost:8001/docs
│   │   │   ├── Endpoints List
│   │   │   └── Request/Response Examples
│   │   ├── Database
│   │   │   ├── Neo4j Schema (Nodes: Concept, Theory, Paper)
│   │   │   ├── PostgreSQL Schema (Metadata)
│   │   │   └── Migration History
│   │   ├── Dependencies
│   │   │   ├── External: Neo4j, PostgreSQL, Ollama
│   │   │   ├── Internal: mathesis-common
│   │   │   └── Consumed By: Q-DNA, Q-Metrics
│   │   ├── Issues & Tasks
│   │   │   └── Database: 버그, 기능 요청, 개선 사항
│   │   ├── Deployment
│   │   │   ├── Last Deployed: 2026-01-08
│   │   │   ├── Version: v1.2.3
│   │   │   ├── Environment: Development/Staging/Production
│   │   │   └── Rollback Procedure
│   │   └── Runbook
│   │       ├── Common Issues & Solutions
│   │       ├── Health Check: GET /health
│   │       └── Emergency Contacts
│   │
│   ├── 🧬 Node 2: Q-DNA
│   │   ├── Service Overview
│   │   │   ├── Domain: 지능형 문제 은행
│   │   │   ├── Tech Stack: Python, PostgreSQL, Tesseract, BKT/IRT
│   │   │   ├── Port: 8002
│   │   │   └── Status: ✅ Production
│   │   ├── API Documentation
│   │   ├── Database
│   │   │   ├── PostgreSQL Schema (ltree, JSONB)
│   │   │   └── Tables: questions, attempts, students, curriculum
│   │   ├── Dependencies
│   │   │   ├── External: PostgreSQL, Ollama
│   │   │   ├── Internal: mathesis-common
│   │   │   └── Calls: Logic Engine (개념 정보)
│   │   ├── Issues & Tasks
│   │   ├── Deployment
│   │   └── Runbook
│   │
│   ├── 📊 Node 5: Q-Metrics
│   │   ├── Service Overview
│   │   │   ├── Domain: 시험 분석
│   │   │   ├── Tech Stack: Python, Neo4j, Redis
│   │   │   ├── Port: 8005
│   │   │   └── Status: 🚧 Beta
│   │   ├── API Documentation
│   │   ├── Database
│   │   │   ├── Neo4j Schema (분석 그래프)
│   │   │   └── Redis (캐시)
│   │   ├── Dependencies
│   │   ├── Issues & Tasks
│   │   ├── Deployment
│   │   └── Runbook
│   │
│   ├── 🏫 Node 6: School Info
│   │   ├── Service Overview
│   │   │   ├── Domain: 학교 정보 RAG
│   │   │   ├── Tech Stack: Python, ChromaDB, Typst
│   │   │   ├── Port: 8006
│   │   │   └── Status: ✅ Production
│   │   ├── API Documentation
│   │   │   ├── POST /schools/{code}/teaching-plans
│   │   │   ├── POST /rag/ingest
│   │   │   ├── POST /rag/query
│   │   │   └── GET /rag/export/{doc_id}
│   │   ├── Database
│   │   │   ├── ChromaDB Collections
│   │   │   └── Vector Store Schema
│   │   ├── Dependencies
│   │   │   ├── External: ChromaDB, Ollama, Typst
│   │   │   ├── Internal: mathesis-common
│   │   │   └── Crawling: schoolinfo.go.kr
│   │   ├── Issues & Tasks
│   │   ├── Deployment
│   │   └── Runbook
│   │       ├── RAG 시스템 초기화
│   │       ├── 크롤링 실패 대응
│   │       └── Enhanced JSON Export
│   │
│   └── 📦 mathesis-common
│       ├── Package Overview
│       │   ├── Version: 0.1.0
│       │   ├── License: MIT
│       │   └── Dependencies: chromadb, ollama, pdfplumber
│       ├── Modules
│       │   ├── mathesis_core.llm (OllamaClient)
│       │   ├── mathesis_core.db (HierarchicalChromaStore)
│       │   ├── mathesis_core.crawlers (BaseCrawler)
│       │   └── mathesis_core.export (PDFGenerator, TypstWrapper)
│       ├── Breaking Changes Log
│       ├── Migration Guide
│       └── Consumers (Node 1, 2, 5, 6)
│
├── 📚 Shared Resources
│   ├── Databases
│   │   ├── PostgreSQL
│   │   │   ├── Host: localhost:5432
│   │   │   ├── Databases: logic_engine, q_dna
│   │   │   └── Backup Schedule
│   │   ├── Neo4j
│   │   │   ├── Host: localhost:7474
│   │   │   ├── Databases: logic_engine, q_metrics
│   │   │   └── Cypher Queries
│   │   └── Redis
│   │       └── Host: localhost:6379
│   ├── LLM Infrastructure
│   │   ├── Ollama Server
│   │   │   ├── Models: llama3, nomic-embed-text, llama3.2-vision
│   │   │   ├── Inference Time Monitoring
│   │   │   └── Model Update Schedule
│   │   └── API Rate Limits
│   └── External Dependencies
│       ├── schoolinfo.go.kr (크롤링 소스)
│       ├── GROBID (논문 파싱)
│       └── Typst (PDF 생성)
│
├── 🚀 Operations
│   ├── Quick Start Guide
│   │   ├── Prerequisites
│   │   ├── Docker Compose 실행
│   │   ├── 개별 서비스 실행
│   │   └── 기능 테스트
│   ├── Deployment
│   │   ├── Development Setup
│   │   ├── Staging Environment (계획)
│   │   ├── Production Checklist (계획)
│   │   └── CI/CD Pipeline (계획)
│   ├── Monitoring & Observability
│   │   ├── Health Checks (각 서비스 /health)
│   │   ├── Logging Strategy (계획: ELK)
│   │   ├── Metrics (계획: Prometheus + Grafana)
│   │   └── Distributed Tracing (계획: Jaeger)
│   └── Troubleshooting
│       ├── Common Issues
│       ├── Ollama 연결 실패
│       ├── Docker Compose 오류
│       ├── 포트 충돌
│       └── Database 초기화
│
├── 📋 Product & Planning
│   ├── Roadmap
│   │   ├── Phase 1: Core Services ✅
│   │   ├── Phase 2: Advanced Features 🚧
│   │   └── Phase 3: Production Ready 📋
│   ├── User Stories
│   │   ├── 학생 - 개인화 학습
│   │   ├── 교사 - 시험 분석
│   │   ├── 연구자 - 이론 탐색
│   │   └── 학부모 - 학교 정보 조회
│   ├── Requirements Analysis (기존 페이지 이동)
│   └── Feature Backlog
│
├── 📖 Knowledge Base
│   ├── 기획서 (Archive)
│   │   ├── 차세대 AI 교육 에코시스템
│   │   ├── RDF 온톨로지 기반 교육 논리 엔진
│   │   ├── 에듀 로직 엔진 데이터 수집 계획
│   │   └── Edu-Logic Lab 진단 엔진
│   ├── Technical Guides
│   │   ├── MSA Best Practices
│   │   ├── Domain-Driven Design
│   │   ├── GraphRAG 구현 가이드
│   │   └── BKT/IRT 알고리즘 설명
│   └── Research Papers
│       ├── 교육공학 논문 목록
│       └── 학습 이론 참고 자료
│
└── 🔗 External Links
    ├── GitHub Repository
    ├── Swagger UI (각 서비스)
    ├── Neo4j Browser
    └── 서브 시스템
        ├── StepWise (문제 실수 대응)
        └── Animal Forest Coding (게임 기반 코딩 교육)

```

---

## 3. Notion Database 설계

### 3.1 Services Database

| Property | Type | Description |
|----------|------|-------------|
| **Name** | Title | 서비스 이름 (Logic Engine, Q-DNA, ...) |
| **Port** | Number | 포트 번호 (8001, 8002, ...) |
| **Status** | Select | ✅ Production / 🚧 Beta / 📋 Planned |
| **Domain** | Text | 비즈니스 도메인 |
| **Tech Stack** | Multi-select | Python, FastAPI, Neo4j, ... |
| **Database** | Multi-select | PostgreSQL, Neo4j, ChromaDB, Redis |
| **Owner** | Person | 담당자 |
| **Last Deploy** | Date | 최근 배포일 |
| **Version** | Text | 현재 버전 (Semantic Versioning) |
| **API Docs** | URL | Swagger URL |
| **Repo Link** | URL | GitHub 서브디렉토리 링크 |
| **Dependencies** | Relation → Services | 의존하는 다른 서비스 |
| **Active Issues** | Rollup | Issues Database에서 개수 집계 |

### 3.2 Issues Database (서비스별 이슈 관리)

| Property | Type | Description |
|----------|------|-------------|
| **Title** | Title | 이슈 제목 |
| **Service** | Relation → Services | 관련 서비스 |
| **Type** | Select | 🐛 Bug / ✨ Feature / 🔧 Improvement / 🔥 Hotfix |
| **Priority** | Select | 🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low |
| **Status** | Select | 📋 Open / 🚧 In Progress / ✅ Resolved / 🚫 Closed |
| **Assignee** | Person | 담당자 |
| **Created** | Date | 생성일 |
| **Resolved** | Date | 해결일 |
| **Labels** | Multi-select | database, api, performance, ... |
| **Description** | Text | 상세 설명 |

### 3.3 Deployment Log Database

| Property | Type | Description |
|----------|------|-------------|
| **Service** | Relation → Services | 배포된 서비스 |
| **Version** | Text | 버전 번호 (v1.2.3) |
| **Environment** | Select | Development / Staging / Production |
| **Deploy Date** | Date | 배포 일시 |
| **Status** | Select | ✅ Success / ⚠️ Partial / ❌ Failed / ⏪ Rolled Back |
| **Deployed By** | Person | 배포자 |
| **Changes** | Text | 변경 사항 요약 |
| **Commit Hash** | Text | Git commit SHA |
| **Notes** | Text | 배포 노트 |

### 3.4 ADR (Architecture Decision Records) Database

| Property | Type | Description |
|----------|------|-------------|
| **ADR Number** | Title | ADR-001, ADR-002, ... |
| **Title** | Text | 결정 제목 |
| **Status** | Select | ✅ Accepted / 🚧 Proposed / 🚫 Rejected / ⏪ Superseded |
| **Date** | Date | 결정 날짜 |
| **Context** | Text | 배경 설명 |
| **Decision** | Text | 내린 결정 |
| **Consequences** | Text | 긍정적/부정적 결과 |
| **Related Services** | Relation → Services | 영향받는 서비스 |
| **Superseded By** | Relation → ADR | 이 결정을 대체한 ADR |

---

## 4. 마이그레이션 계획

### Phase 1: 구조 재편 (1일)
1. **Root 페이지 정리**
   - Dashboard & Overview 섹션 생성
   - MSA Architecture 섹션 생성
2. **Services 섹션 생성**
   - 각 Node별 독립 페이지 생성 (템플릿 기반)
   - mathesis-common 페이지 생성
3. **기존 Technical Overview 페이지 이동**
   - 각 서비스 페이지 하위로 이동

### Phase 2: Database 구축 (1일)
1. **Services Database 생성**
   - 4개 노드 + mathesis-common 데이터 입력
2. **Issues Database 생성** (템플릿 제공)
3. **Deployment Log Database 생성**
4. **ADR Database 생성**
   - ADR-001, 002, 003 마이그레이션

### Phase 3: 콘텐츠 마이그레이션 (2일)
1. **API Documentation**
   - 각 서비스별 Swagger 링크 연동
   - 주요 Endpoint 문서화
2. **Runbook 작성**
   - 각 서비스별 장애 대응 절차
3. **기획서 아카이브**
   - Knowledge Base > 기획서 섹션으로 이동
4. **Operations 섹션 채우기**
   - Quick Start, Deployment, Troubleshooting

### Phase 4: 자동화 (계획)
1. **GitHub Actions 연동**
   - 배포 시 Deployment Log 자동 생성
2. **Swagger → Notion 동기화**
   - API 문서 자동 업데이트
3. **Issue Sync**
   - GitHub Issues ↔ Notion Issues 양방향 동기화

---

## 5. 운영 워크플로우

### 5.1 일상적인 개발
```
1. Issue Database에 버그/기능 등록
2. 해당 서비스 페이지에서 작업 시작
3. 코드 변경 (Git)
4. 로컬 테스트
5. PR 생성 → 코드 리뷰
6. Merge → Deployment Log 기록
```

### 5.2 장애 대응
```
1. Services Database에서 상태 🔴 Critical 표시
2. 해당 서비스 Runbook 참조
3. Troubleshooting 절차 수행
4. Issues Database에 장애 원인 기록
5. 복구 후 상태 ✅ 변경
6. Post-Mortem 작성 (ADR로 기록)
```

### 5.3 아키텍처 변경
```
1. ADR Database에 제안 추가 (🚧 Proposed)
2. 관련 서비스 담당자와 논의
3. 승인 시 Status → ✅ Accepted
4. Migration Guide 작성
5. 각 서비스별 적용 (Issues 생성)
6. 완료 후 Architecture 문서 업데이트
```

---

## 6. 핵심 페이지 템플릿

### 6.1 Service Page Template

```markdown
# [Service Name]

## 📝 Overview
- **Domain**: [교육 이론 / 문제 은행 / ...]
- **Port**: [8001 / 8002 / ...]
- **Status**: ✅ Production / 🚧 Beta
- **Owner**: @[이름]
- **Last Updated**: 2026-01-08

## 🎯 Responsibilities
- [책임 1]
- [책임 2]

## 🛠️ Tech Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: [PostgreSQL / Neo4j / ChromaDB]
- **LLM**: Ollama

## 📚 API Endpoints
→ [Swagger UI](http://localhost:800X/docs)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| POST | /api/v1/... | ... |

## 🗄️ Database Schema
### PostgreSQL / Neo4j / ChromaDB
[스키마 다이어그램 또는 설명]

## 🔗 Dependencies
### External
- Database: [연결 정보]
- Ollama: http://localhost:11434

### Internal
- mathesis-common: v0.1.0

### Consumed By
- [다른 서비스 목록]

## 🐛 Active Issues
→ Database View (Service = this)

## 🚀 Latest Deployment
- **Version**: v1.2.3
- **Date**: 2026-01-08
- **Status**: ✅ Success
- **Changes**: [변경 사항]

## 📖 Runbook
### Health Check
\```bash
curl http://localhost:800X/health
\```

### Common Issues
1. **[이슈 제목]**
   - 증상: ...
   - 원인: ...
   - 해결: ...

### Emergency Contacts
- Owner: @[이름]
- On-call: @[이름]
```

---

## 7. 도구 연동 계획

### 7.1 Notion API
- Services Database CRUD
- Issues Database 자동 생성
- Deployment Log 기록

### 7.2 GitHub Actions
```yaml
# .github/workflows/deploy.yml
on:
  push:
    branches: [main]
jobs:
  deploy:
    steps:
      - name: Deploy to Production
      - name: Update Notion Deployment Log
        run: |
          curl -X POST https://api.notion.com/v1/pages \
            -d '{"parent": {"database_id": "..."}, ...}'
```

### 7.3 Slack/Discord 알림
- 배포 완료 시 알림
- Critical 이슈 발생 시 알림

---

## 8. 성공 지표

### 8.1 운영 효율성
- ✅ 서비스별 독립 배포 가능
- ✅ 장애 발생 시 Runbook 참조 시간 < 5분
- ✅ 신규 팀원 온보딩 시간 < 2시간

### 8.2 가시성
- ✅ 전체 서비스 상태 Dashboard에서 한눈에 확인
- ✅ 서비스 간 의존성 명확히 추적
- ✅ API 문서 최신 상태 유지

### 8.3 협업
- ✅ ADR로 기술 결정 이력 투명하게 공유
- ✅ Issue Database로 작업 우선순위 관리
- ✅ Deployment Log로 배포 이력 추적

---

**다음 단계**: Notion API를 통해 자동으로 페이지 구조 생성

