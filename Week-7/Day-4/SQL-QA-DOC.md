# SQL-QA System Documentation Overview 
The SQL Question Answering (SQL-QA) system converts natural language questions into safe, validated SQLite queries using Gemini, executes them securely, and summarizes results in natural language. 
It supports: 
- SQLite .db files 
- Automatic CSV → SQLite conversion 
- Schema-aware SQL generation 
- Guard rails + validation 
- Safe PRAGMA handling 
- Automatic SQL correction loop 
- Result summarization 

## Architecture 
```bash
User Question 
    ↓ 
Schema Loader 
    ↓ 
Gemini SQL Generation 
    ↓ 
Validation Layer 
    ↓ 
(If invalid → Correction Loop) 
    ↓ 
Safe SQL Execution 
    ↓ 
Result Preview 
    ↓ 
Gemini Natural Language Summary 
    ↓ 
Final Answer 
```
## Module Structure 
### 1️⃣ utils/schema_loader.py 
Responsible for: 
- Detecting database file 
- Extracting schema (tables + columns + sample rows) 
- Creating schema metadata dictionary 
- Providing structured schema context for LLM 
Output: 
- schema → Prompt-ready string 
- schema_meta → {table: [columns]} for validation 
### 2️⃣ generator/sql_generator.py 
Core SQL generation engine. 
Features: 
- Schema-aware prompt 
- Guard rail (blocks destructive commands) 
- Syntax validation (sqlparse) 
- Schema validation (tables & columns) 
- Safe PRAGMA table_info support 
- SQL correction loop (max 3 retries) 
Validation Layers: 
- Guard rail 
- Syntax check 
- Schema check 
- Controlled PRAGMA usage 
### 3️⃣ pipelines/sql_pipeline.py 
Orchestrates full workflow. 
Responsibilities: 
- Auto-detect .db 
- If absent → Convert .csv to temporary SQLite DB 
- Load schema 
- Generate SQL 
- Validate SQL 
- Execute safely 
- Display structured table preview 
- Summarize results with Gemini 

## Security Design 
The system enforces: 
- SELECT-only queries 
- Forbidden command blocking (DROP, DELETE, etc.) 
- Schema-aware validation 
- Controlled PRAGMA access (only pragma_table_info) 
- Execution only after validation 
- Limited result preview (50 rows for summary, 20 for display) 

## CSV Support 
If no .db is found: 
- All .csv files in DB_DIR are loaded. 
- Filenames are sanitized into safe table names. 
- A temporary SQLite database is created. 
- The pipeline proceeds normally. 
This ensures SQL-QA works on flat files without altering architecture. 

## SQL Correction Loop 
If generated SQL fails validation: 
1. Validation error is captured. 
2. Gemini is prompted with: 
    - Original question 
    - Schema 
    - Generated SQL 
    - Validation error 
3. SQL is regenerated (up to 3 attempts). 
This significantly reduces failure rates. 

## Workflow Example
User: 
```bash
Show total sales by artist for 2023. 
```
**System:** 
- Loads schema 
- Generates SQL 
- Validates SQL 
- Executes on SQLite 
- Fetches rows 
- Summarizes results 
- Returns natural language answer