Create a clean, professional, simple but still  technical, pretty presentation-ready ppt that includes a system architecture diagram based on the information given below:

Problem Statement : Dynamic ETL Pipeline for Unstructured Data
Challenge: Given unstructured scraped data that evolves over time, develop an ETL (Extract, Transform, Load) pipeline that can generate dynamic schemas on-the-fly.
Key Requirements:
* Handle completely unstructured input data
* Adapt to data that changes multiple times
* Generate schemas dynamically as data evolves
* Address the challenge of storing data when structure is unknown upfront
Use Case: This simulates real-world scenarios where data sources are unpredictable and constantly changing, making static schema definitions impractical.

6-Layer Architecture:

    API Gateway
    FastAPI Framework
    RESTful Endpoints
    Request Validation
    Async Processing
    Ingestion
    PDF Parser + OCR
    Text Parser
    Markdown Parser
    File Validation
    Parsing
    Fragment Detection
    Type Inference
    Data Cleaning
    Field Extraction
    Schema
    Dynamic Generation
    Version Control
    Evolution Engine
    Migration Manager
    Query
    LLM Integration
    NL to SQL
    Query Execution
    Result Formatting
    Storage
    PostgreSQL
    MongoDB
    Redis Cache
    MinIO/S3

    Overview Modern data comes in unpredictable formats — PDFs, Markdown files, text logs, emails, semi-structured blocks, and mixed patterns within a single file. Traditional ETL pipelines struggle because they require fixed schemas and break when the structure changes. This project solves that problem. It automatically:
    accepts different file types (TXT, MD, PDF),
    extracts useful structured data,
    cleans and normalizes it,
    infers field types,
    generates and versions schemas,
    stores data in both SQL and NoSQL databases,

    and supports natural-language querying powered by an LLM.
    This document explains the architecture in a simple, progressive manner while staying technically solid.
    Core Idea (The Crux) This system behaves like a smart factory for unstructured files.
    Files arrive → TXT, PDF, MD
    Parsers read the content
    Detectors find structured patterns inside the raw text
    Extractors convert those patterns into fields
    Cleaner standardizes values and types
    Schema generator builds/upgrades the schema
    Data stored in SQL + NoSQL

    Queries run via SQL or natural language through an LLM translator
    This makes the system adaptable, self-evolving, and user-friendly.

    High-Level Architecture Diagram

                 ┌───────────────────────────┐
                 │         Client / UI        │
                 │  curl, Postman, frontend   │
                 └───────────────┬───────────┘
                                 │
                        HTTP Requests
                                 │
                 ┌───────────────▼────────────────┐
                 │          FastAPI API Gateway     │
                 │  /upload   /schema   /query      │
                 └───────────────┬─────────────────┘
                                 │
                    File Bytes + Source ID
                                 │
                 ┌───────────────▼────────────────┐
                 │        Ingestion Layer          │
                 │  - PDF parser (pypdf)           │
                 │  - TXT/MD decoder               │
                 └───────────────┬────────────────┘
                                 │
                            Extracted Text
                                 │
                 ┌───────────────▼────────────────┐
                 │        Parsing Engine           │
                 │  - Fragment detector            │
                 │  - Field extractor              │
                 │  - Type inference               │
                 │  - Data cleaner                 │
                 └───────────────┬────────────────┘
                                 │
                         Cleaned Records
                                 │
                 ┌───────────────▼────────────────┐
                 │         Schema Layer            │
                 │  - Schema generator             │
                 │  - Schema versioning            │
                 │  - Evolution diffs              │
                 └───────────────┬────────────────┘
                                 │
                       (Schema + Records)
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
    ┌────────────▼──────────┐  ┌────▼────────────┐  ┌──▼──────────────┐
    │ PostgreSQL (SQL store) │  │ MongoDB (docs)  │  │  MinIO/S3 (raw) │
    │ - Structured tables    │  │ - Parsed docs   │  │ - Raw files     │
    │ - Schema versions      │  │ - Query results │  │ - Backups       │
    └────────────────────────┘  └─────────────────┘  └──────────────────┘
              │                  │
              └──────────┬──────┘
                         │
                  Querying Layer
                         │
      ┌──────────────────▼──────────────────┐
      │         LLM Query Translator         │
      │     (NL → SQL → Safe Execution)      │
      └──────────────────────────────────────┘
    Key Components Explained Simply 4.1 API Gateway (FastAPI) This is the entry point where clients interact with the system. Endpoints:
    POST /upload → Upload any file
    GET /schema → View current schema
    GET /schema/history → View schema evolution
    POST /query → Natural language → SQL
    GET /records → Fetch parsed data or query results Why FastAPI?
    asynchronous = fast under load
    built-in validation
    automatic Swagger docs

4.2 Ingestion Layer (Parsers)
This layer opens files and extracts usable text.
File Type Method
TXT UTF-8 decode
MD UTF-8 decode (Markdown formatting ignored)
PDF pypdf: reads text from each page

4.3 Parsing Engine
The “brain” of the pipeline, made of four mini-modules:
(1) Fragment Detector
Finds bits of structured information:
* JSON objects ({ ... })
* Key-value lines (Age: 30)
* Patterns resembling tables
* Number-value pairs
(2) Field Extractor
Converts each detected fragment into:
{"age": "30", "name": "John Doe"}
(3) Type Inference
Guesses type of each value:
* "30" → integer
* "true" → boolean
* "2025-11-16" → date
* "john@example.com" → email (string)
(4) Data Cleaner
Normalizes values:
* trim whitespace
* lowercase emails
* convert types (string → number)
* standardize keys ("Employee ID" → employee_id)

4.4 Schema Layer
This is where the system “learns" structure.
How schema is built
After extraction, if fields are:
employee_id: integer
name: string
salary: integer
salary: integer
The schema becomes:
{
  "employee_id": {"type": "integer"},
  "name": {"type": "string"},
  "salary": {"type": "integer"}
}
If a new upload contains a new field (department), version increments:
* v1: employee_id, name, salary
* v2: employee_id, name, salary, department
Version changes are saved.

4.5 Storage Layer
PostgreSQL
* Stores schema versions
* Stores structured rows
* Each source gets a table: data_{source_id}
MongoDB
* Stores raw fragments
* Stores cleaned structured documents
* Stores query results (for async queries)
MinIO or S3
* Stores original uploaded files

4.6 Query Layer (LLM Powered)
User asks:
"Show me all employees older than 25"
The LLM translates this to SQL:
SELECT * FROM data_test1 WHERE age > 25;
The query is:
* validated
* executed
* results returned

    Full Workflow in 8 Steps Step 1 — User uploads a file FastAPI receives the file and source ID. Step 2 — Parsing PDF → text TXT/MD → decode Step 3 — Fragment detection Detects:
    JSON blocks
    Key/value pairs
    Tables
    Markdown patterns Step 4 — Field extraction + cleaning Extracts key-value pairs Infers types Cleans text Step 5 — Schema generation Compares extracted fields with latest schema version Creates new version if needed Step 6 — Data storage
    Structured → PostgreSQL
    Flexible → MongoDB
    Original file → S3/MinIO Step 7 — Response Returns file metadata and schema version. Step 8 — Querying LLM translates NL → SQL Execute → return results
    Why This Architecture Works Well ✔️ Automatically adapts to different data formats No manual schema design. ✔️ Handles schema evolution over time Old + new files both supported. ✔️ Supports natural language queries Super useful for non-technical users. ✔️ Uses strengths of SQL and NoSQL Best of both worlds. ✔️ Modular pipeline Easy to extend parsers, add more file types, or integrate OCR.

“Our system can take messy files — PDF, Markdown, or raw text — and automatically extract structured information from them. It then generates a schema on its own, detects when fields change, and versions the schema so the system evolves over time. Data is stored in both SQL and Mongo depending on its structure. Users can then query the data in plain English, and an LLM safely translates those questions into SQL.”
This clearly highlights:
* automation
* schema evolution
* hybrid storage
* natural language querying

Folder Structure:
dynamic-etl-pipeline/
├── README.md
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── .gitignore
├── setup.py
├── pytest.ini
├── alembic.ini
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── upload.py
│   │   │   ├── schema.py
│   │   │   ├── query.py
│   │   │   └── records.py
│   │   └── dependencies.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── ingestion/
│   │   │   ├── __init__.py
│   │   │   ├── file_handler.py
│   │   │   ├── pdf_parser.py
│   │   │   ├── text_parser.py
│   │   │   └── markdown_parser.py
│   │   ├── parsing/
│   │   │   ├── __init__.py
│   │   │   ├── fragment_detector.py
│   │   │   ├── type_inference.py
│   │   │   ├── field_extractor.py
│   │   │   └── data_cleaner.py
│   │   ├── schema/
│   │   │   ├── __init__.py
│   │   │   ├── generator.py
│   │   │   ├── versioning.py
│   │   │   ├── evolution.py
│   │   │   ├── compatibility.py
│   │   │   └── migration.py
│   │   └── query/
│   │       ├── __init__.py
│   │       ├── llm_translator.py
│   │       ├── query_executor.py
│   │       └── result_normalizer.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── schema_models.py
│   │   ├── source_models.py
│   │   └── query_models.py
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── postgres.py
│   │   ├── mongodb.py
│   │   ├── s3_handler.py
│   │   └── redis_cache.py
│   └── utils/
│       ├── __init__.py
│       ├── logging.py
│       ├── security.py
│       └── validators.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_ingestion.py
│   ├── test_parsing.py
│   ├── test_schema.py
│   ├── test_query.py
│   ├── test_api.py
│   └── test_data/
│       ├── tier_a/
│       ├── tier_b/
│       ├── tier_c/
│       └── tier_d/
├── scripts/
│   ├── init_db.py
│   ├── run_tests.py
│   └── generate_test_data.py
└── monitoring/
    ├── prometheus.yml
    └── grafana_dashboard.json