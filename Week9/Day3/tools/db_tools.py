import sqlite3
import pandas as pd
import os
from settings import WORKSPACE_DIR
from autogen_agentchat.agents import AssistantAgent
import settings
from autogen_ext.models.openai import OpenAIChatCompletionClient

# 1. Model Client
gemini_client = OpenAIChatCompletionClient(
    model=settings.MODEL_ID,
    api_key=settings.GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    model_info=settings.MODEL_INFO
)

from autogen_ext.models.ollama import OllamaChatCompletionClient

# Qwen 2.5 (7B or 14B) is highly recommended for coding tasks
qwen_client = OllamaChatCompletionClient(
    model="qwen2.5:7b",
    host="http://127.0.0.1:11434",
)


def execute_sql(db_name: str, query: str) -> str:
    """Executes SQL queries (SELECT or Modification) on a workspace DB."""
    db_path = os.path.join(WORKSPACE_DIR, os.path.basename(db_name))
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            if query.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                cols = [d[0] for d in cursor.description]
                return f"Columns: {cols}\nData: {rows}"
            conn.commit()
            return f"Success: {cursor.rowcount} rows affected."
    except Exception as e:
        return f"SQL Error: {str(e)}"

def csv_to_sqlite(csv_name: str, db_name: str, table_name: str) -> str:
    """Converts a workspace CSV into a SQLite table for analysis."""
    csv_path = os.path.join(WORKSPACE_DIR, os.path.basename(csv_name))
    db_path = os.path.join(WORKSPACE_DIR, os.path.basename(db_name))
    try:
        df = pd.read_csv(csv_path)
        with sqlite3.connect(db_path) as conn:
            df.to_sql(table_name, conn, if_exists='replace', index=False)
        return f"Created table '{table_name}' in '{db_name}' from {csv_name}."
    except Exception as e:
        return f"Conversion Error: {str(e)}"
    
db_agent = AssistantAgent(
    name="db_agent",
    model_client=gemini_client,
    tools=[execute_sql, csv_to_sqlite],
    description="I handle SQL tools.",
    system_message="""You are the @db_agent. 
    You specialize in converting CSV data to SQLite and querying it.
    - Use 'csv_to_sqlite' for initial data loading.
    - Use 'execute_sql' for analysis.
    - Provide a clear summary of the SQL results.
    - After finishing, return control to @primary_agent."""
)