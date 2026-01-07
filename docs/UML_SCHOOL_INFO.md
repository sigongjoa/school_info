# School Info Service UML Diagrams

## 1. Use Case Diagram
This diagram illustrates how users interact with the School Info Service.

```mermaid
graph LR
    subgraph Actors
        User["Parent/Student"]
        Admin["Administrator"]
    end

    subgraph "School Alimi Service"
        UC1("Search School")
        UC2("View School Details")
        UC3("Generate Analysis Report (PDF)")
        UC4("Download Teaching Plans")
        UC5("View Academic Trends (AI)")
    end

    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5

    Admin -- Batch Generation --> UC3
    
    style User fill:#f9f,stroke:#333,stroke-width:2px
    style Admin fill:#f9f,stroke:#333,stroke-width:2px
```

## 2. Sequence Diagram (Report Generation)
This diagram details the flow from the user request to the final generated PDF report.

```mermaid
sequenceDiagram
    participant U as User
    participant API as Node1 API
    participant C as SchoolInfoCrawler
    participant DB as Postgres/Neo4j
    participant AI as RAG Service (Ollama)
    participant PDF as TypstGenerator

    U->>API: POST /schools/{code}/analyze
    activate API
    
    API->>C: fetch_school_data(code)
    activate C
    C->>C: _get_basic_info()
    C->>C: download_teaching_plans() (Phase 11)
    C->>C: fetch_restricted_stats() (CAPTCHA Sim)
    C-->>API: SchoolData Object
    deactivate C

    API->>DB: Save/Update School Data
    
    API->>AI: summarize_school(SchoolData)
    activate AI
    AI->>AI: analyze_documents(docs)
    AI-->>API: Korean Summary Text
    deactivate AI

    API->>PDF: compile(template, data + summary)
    activate PDF
    PDF->>PDF: convert_latex_to_typst()
    PDF->>PDF: typst compile --font-path Nanum
    PDF-->>API: report_path.pdf
    deactivate PDF

    API-->>U: Return Download Link / Path
    deactivate API
```

## 3. Class Diagram (Core Components)
Structure of the key classes implementing specific crawler and analysis logic.

```mermaid
classDiagram
    class SchoolInfoCrawler {
        +fetch(school_code)
        +download_teaching_plans(year)
        +fetch_restricted_stats(year, captcha)
        -_verify_captcha(solution)
    }

    class TypstGenerator {
        +compile(template, data, out_path)
        -_discover_fonts()
    }

    class SchoolRAGService {
        +summarize_school(school_data)
        +analyze_documents(documents)
    }

    class SchoolData {
        +String school_code
        +String name
        +List~Curriculum~ curriculum
        +List~AchievementStat~ stats
    }

    SchoolInfoCrawler --> SchoolData : produces
    SchoolRAGService ..> SchoolData : reads
    TypstGenerator ..> SchoolData : renders
```
