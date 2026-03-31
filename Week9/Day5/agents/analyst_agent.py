import sqlite3
import pandas as pd
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_core.tools import FunctionTool
from Config import settings
from autogen_core.model_context import BufferedChatCompletionContext


# --- TOOLS FOR ANALYST ---

def csv_to_sqlite(csv_path: str, db_name: str) -> str:
    """Converts a CSV file into a SQLite table. Returns success message."""
    try:
        df = pd.read_csv(csv_path)
        # Clean column names for SQL compatibility
        df.columns = [c.replace(' ', '_').replace('.', '_') for c in df.columns]
        
        conn = sqlite3.connect(db_name)
        table_name = os.path.basename(csv_path).split('.')[0]
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.close()
        return f"Successfully converted {csv_path} to table '{table_name}' in {db_name}."
    except Exception as e:
        return f"Error converting CSV: {str(e)}"

def execute_sql(db_name: str, query: str) -> str:
    """Executes a SQL query on the specified database and returns results."""
    try:
        conn = sqlite3.connect(db_name)
        df = pd.read_sql_query(query, conn)
        conn.close()
        if df.empty:
            return "Query executed successfully, but no data was returned."
        return df.to_markdown()
    except Exception as e:
        return f"SQL Error: {str(e)}"
    
csv_tool = FunctionTool(csv_to_sqlite, description="Convert CSV files to SQL for analysis")
sql_tool = FunctionTool(execute_sql, description="Run SQL queries to get insights")

# --- ANALYST AGENT DEFINITION ---

ANALYST_PROMPT = """
You are the @analyst_agent of NEXUS AI. 
Your specialty is structured data analysis and strategic interpretation.

OPERATIONAL PROTOCOLS:
1. DATA INGESTION: Use 'csv_to_sqlite' if you are given a CSV file path.
2. SQL EXECUTION: Use 'execute_sql' to run queries. Do not speculate on data; verify it.
3. ANALYSIS PHASES:
   - Identify the schema and data types first.
   - Run specific queries to answer the @planner_agent's requirements.
   - Provide a 'Strategic Insight' explaining the real-world meaning of the numbers.
4. SELF-CORRECTION: If a SQL query fails, analyze the error, fix the syntax, and try again.

Output your findings in clean Markdown tables and bullet points.
"""

# 1. Model Client
gemini_client = OpenAIChatCompletionClient(
    model=settings.MODEL_ID,
    api_key=settings.GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    model_info=settings.MODEL_INFO
)

qwen_client = OllamaChatCompletionClient(
    model="qwen2.5:7b",
    host="http://127.0.0.1:11434",
)

analyst_agent = AssistantAgent(
    name="analyst_agent",
    model_client=gemini_client,
    system_message=ANALYST_PROMPT,
    tools=[csv_tool, sql_tool],
    model_context=BufferedChatCompletionContext(buffer_size=10),
    model_client_stream=True
)