

import re
import sys
from pathlib import Path

import sqlparse
from google import genai
from langchain_core.prompts import PromptTemplate

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config.settings import GEMINI_API_KEY, GEMINI_MODEL_SQL

if not GEMINI_API_KEY:
    sys.exit("GOOGLE_API_KEY not set in .env")

client = genai.Client(api_key=GEMINI_API_KEY)

# ── Prompt ────────────────────────────────────────────────────────────────────
SQL_PROMPT = PromptTemplate(
    input_variables=["schema", "question"],
    template="""You are an expert SQL assistant for SQLite databases.
Given the schema below, write a single valid SQLite SQL query to answer the question.

Rules:
- Return ONLY the SQL query, no explanation, no markdown, no backticks.
- Use only SELECT statements.
- Use only tables and columns that exist in the schema.
- End the query with a semicolon.

Schema:
{schema}

Question: {question}

SQL:"""
)

CORRECTION_PROMPT = PromptTemplate(
    input_variables=["schema", "question", "previous_sql", "error"],
    template="""The following SQL query is invalid.

Schema:
{schema}

User Question:
{question}

Generated SQL:
{previous_sql}

Validation Error:
{error}

Rewrite the SQL to fix the error.
Return ONLY the corrected SQL query.
Do not include explanations or markdown.
End with a semicolon.

Corrected SQL:"""
)

# ── Guard rail ────────────────────────────────────────────────────────────────
FORBIDDEN = {"drop", "delete", "update", "alter", "truncate", "insert", "replace", "create"}


def _check_guard_rail(sql: str) -> tuple[bool, str]:
    tokens = {t.lower() for t in re.findall(r"\b\w+\b", sql)}
    found  = tokens & FORBIDDEN
    if found:
        return False, f"Forbidden command(s) detected: {', '.join(found).upper()}"
    return True, ""


def _check_syntax(sql: str) -> tuple[bool, str]:
    parsed = sqlparse.parse(sql.strip())
    if not parsed or not parsed[0].tokens:
        return False, "SQL appears empty or unparseable."
    return True, ""

def _check_schema(sql: str, schema_meta: dict) -> tuple[bool, str]:

    sql_lower = sql.lower()
    known_tables = set(schema_meta.keys())

    # ----------------------------------------
    # 1. Allow safe PRAGMA table_info only
    # ----------------------------------------
    pragma_matches = re.findall(
        r"pragma_table_info\(\s*'([a-zA-Z_][a-zA-Z0-9_]*)'\s*\)",
        sql_lower
    )

    for table in pragma_matches:
        if table not in known_tables:
            return False, f"PRAGMA references unknown table '{table}'."

    # Block other PRAGMA usage
    if "pragma" in sql_lower and not pragma_matches:
        return False, "Only PRAGMA table_info() is allowed."

    # ----------------------------------------
    # 2. Validate normal table references
    # ----------------------------------------
    table_refs = re.findall(
        r"(?:from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        sql_lower
    )

    for t in table_refs:
        if t.startswith("pragma_table_info"):
            continue
        if t not in known_tables:
            return False, f"Table '{t}' does not exist in the database."

    # ----------------------------------------
    # 3. Validate column references
    # ----------------------------------------
    col_refs = re.findall(
        r"([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)",
        sql_lower
    )

    for tbl, col in col_refs:
        if tbl in known_tables and col not in schema_meta.get(tbl, []):
            return False, f"Column '{col}' does not exist in table '{tbl}'."

    return True, ""


def validate_sql(sql: str, schema_meta: dict) -> tuple[bool, str]:
    """
    Run all three validation layers.
    Returns (is_valid, error_message).
    """
    for check in [_check_guard_rail, _check_syntax]:
        ok, err = check(sql)
        if not ok:
            return False, err

    ok, err = _check_schema(sql, schema_meta)
    if not ok:
        return False, err

    return True, ""


def generate_sql(question: str, schema: str, schema_meta: dict) -> tuple[str, bool, str]:

    MAX_RETRIES = 3

    # Initial generation
    prompt = SQL_PROMPT.format(schema=schema, question=question)
    response = client.models.generate_content(
        model=GEMINI_MODEL_SQL,
        contents=prompt
    )

    sql = response.text.strip()
    sql = re.sub(r"```sql|```", "", sql).strip()

    for attempt in range(MAX_RETRIES):

        is_valid, error = validate_sql(sql, schema_meta)

        if is_valid:
            return sql, True, ""

        # Try correction
        correction_prompt = CORRECTION_PROMPT.format(
            schema=schema,
            question=question,
            previous_sql=sql,
            error=error
        )

        response = client.models.generate_content(
            model=GEMINI_MODEL_SQL,
            contents=correction_prompt
        )

        sql = response.text.strip()
        sql = re.sub(r"```sql|```", "", sql).strip()

    # If all retries fail
    return sql, False, error