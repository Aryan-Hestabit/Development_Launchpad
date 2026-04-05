import json
import sqlite3
import sys
from pathlib import Path
import pandas as pd
from google import genai
from langchain_core.prompts import PromptTemplate

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config.settings import GEMINI_API_KEY, GEMINI_MODEL_SQL, DB_DIR
from utils.schema_loader import get_db_path, load_schema, get_schema_metadata
from generator.sql_generator import generate_sql

if not GEMINI_API_KEY:
    sys.exit("GOOGLE_API_KEY not set in .env")

client = genai.Client(api_key=GEMINI_API_KEY)

# ── Summarizer prompt ─────────────────────────────────────────────────────────
SUMMARY_PROMPT = PromptTemplate(
    input_variables=["question", "sql", "results"],
    template="""You are a data analyst. A user asked the following question and the SQL query below was executed against the database.

Question: {question}

SQL Executed:
{sql}

Query Results:
{results}

Write a clear, concise natural language answer to the question based on the results above.
Do not repeat the SQL. Just answer the question directly."""
)

# ── Safe executor ─────────────────────────────────────────────────────────────
def execute_sql(db_path: Path, sql: str) -> tuple[list[dict], str]:
    try:
        conn   = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows, ""
    except Exception as e:
        return [], str(e)


# ── Result summarizer ─────────────────────────────────────────────────────────
def summarize(question: str, sql: str, rows: list[dict]) -> str:
    if not rows:
        return "The query returned no results."

    # Truncate to 50 rows max to stay within token limits
    display_rows = rows[:50]
    results_str  = json.dumps(display_rows, indent=2)

    prompt = SUMMARY_PROMPT.format(question=question, sql=sql, results=results_str)
    return client.models.generate_content(model=GEMINI_MODEL_SQL, contents=prompt).text.strip()


# ── Display helpers ───────────────────────────────────────────────────────────
def show_table(rows: list[dict]):
    if not rows:
        return
    headers = list(rows[0].keys())
    col_w   = {h: max(len(h), max(len(str(r.get(h, ""))) for r in rows)) for h in headers}

    sep = "+" + "+".join("-" * (col_w[h] + 2) for h in headers) + "+"
    print(sep)
    print("|" + "|".join(f" {h:<{col_w[h]}} " for h in headers) + "|")
    print(sep)
    for row in rows[:20]:
        print("|" + "|".join(f" {str(row.get(h,'')):<{col_w[h]}} " for h in headers) + "|")
    print(sep)
    if len(rows) > 20:
        print(f"  ... and {len(rows) - 20} more rows.")


# ── Pipeline ──────────────────────────────────────────────────────────────────
def run_pipeline(question: str, db_path: Path, schema: str, schema_meta: dict):
    print(f"\n{'─'*65}")
    print(f"  Question : {question}")
    print(f"{'─'*65}")

    # 1. Generate + validate SQL
    sql, is_valid, error = generate_sql(question, schema, schema_meta)
    print(f"\n  Generated SQL:\n  {sql}\n")

    if not is_valid:
        print(f"  ❌ Validation failed: {error}")
        return

    print("  ✅ SQL validated.")

    # 2. Execute
    rows, exec_error = execute_sql(db_path, sql)
    if exec_error:
        print(f"  ❌ Execution failed: {exec_error}")
        return

    print(f"  ✅ Query returned {len(rows)} row(s).\n")
    show_table(rows)

    # 3. Summarize
    print(f"\n  💬 Answer:")
    print(f"  {summarize(question, sql, rows)}")
    print()


# ── CLI ───────────────────────────────────────────────────────────────────────
MENU = """
  SQL Question Answering        
  Type your question or 'q' to quit.      
"""

def main():

    # Step 1: Try to find .db file first
    db_files = list(DB_DIR.glob("*.db"))

    if db_files:
        db_path = db_files[0]

    else:
        # Step 2: If no .db found, check for CSV files
        csv_files = list(DB_DIR.glob("*.csv"))

        if not csv_files:
            sys.exit("No .db or .csv files found in DB_DIR.")

        print("No SQLite database found. Converting CSV files to temporary SQLite DB...")

        temp_db_path = DB_DIR / "temp_csv_database.db"

        conn = sqlite3.connect(temp_db_path)

        for csv_file in csv_files:
            table_name = csv_file.stem
            df = pd.read_csv(csv_file)
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f"  Loaded CSV → Table: {table_name}")

        conn.close()

        db_path = temp_db_path
        print(f"\nTemporary SQLite DB created: {temp_db_path.name}\n")

    # Step 3: Load schema normally (unchanged logic)
    schema = load_schema(db_path)
    schema_meta = get_schema_metadata(db_path)

    print(MENU)
    print(f"  Connected to: {db_path.name}")
    print(f"  Tables found: {', '.join(schema_meta.keys())}\n")

    while True:
        question = input("  Your question: ").strip()
        if question.lower() in {"q", "quit", "exit"}:
            print("  Goodbye! 👋")
            break
        if not question:
            continue
        run_pipeline(question, db_path, schema, schema_meta)


if __name__ == "__main__":
    main()