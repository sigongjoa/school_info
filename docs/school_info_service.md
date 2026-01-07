# School Info Service (School Alimi) Specification

## 1. Overview
The **School Info Service** (internally "School Alimi") is a specialized component within the Mathesis platform designed to aggregate, analyze, and present detailed educational data for Korean schools. It leverages the public "School Info" (학교알리미) data, provides AI-driven summaries, and generates high-fidelity PDF reports.

## 2. Architecture (Node Role)
Currently deployed as a module within **Node 1 (Logic Engine)**, this service operates as an autonomous logical unit.

- **Crawler Layer (`mathesis_core.crawlers`)**: Handles data acquisition from `schoolinfo.go.kr`. Supports both live scrapping and robust fallback data for protected specific targets (e.g., Dongdo Middle School).
  - *Features*: HTML parsing, simulated CAPTCHA bypass (Section 4-na), PDF generation for Teaching Plans (Section 4-ga).
- **Data Layer (`Postgres` + `Neo4j`)**: storage of structured school metadata, curriculum, and achievement statistics.
- **Analysis Layer (`SchoolRAGService`)**: Uses `Ollama` (Llama 3/Qwen) to generate qualitative summaries of academic trends from raw document text.
- **Export Layer (`TypstGenerator`)**: Produces professional-grade PDFs with correct Korean typography (`NanumGothic`) and dynamic layout.

## 3. Key Features
1.  **School Search**: Lookup schools by name or code.
2.  **Comprehensive Analytics**:
    -   Basic Info (Address, Founding Date).
    -   Curriculum Analysis (Subjects, Focus Areas).
    -   Achievement Statistics (Mean, Std Dev, Grade Distribution).
3.  **Document Library**:
    -   Download yearly "Teaching Plans" (2025).
    -   Access historical "Achievement Reports" (2024).
4.  **AI Summary Report**: A one-click PDF generation that combines strict data with AI insights.

## 4. API Reference
- `POST /api/v1/schools/{code}/analyze`: Triggers full crawler-ETL-analysis pipeline and returns PDF path.
- `GET /api/v1/schools/{code}/documents`: Lists available crawled/simulated documents.

## 5. Technology Stack
- **Languages**: Python 3.10+
- **Frameworks**: FastAPI (Node1), BeautifulSoup4 (Crawling)
- **PDF Engine**: Typst (via `mathesis_core`)
- **AI/LLM**: Ollama (Local Interference)
