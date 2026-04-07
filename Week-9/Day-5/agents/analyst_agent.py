import sqlite3
import pandas as pd
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.ollama import OllamaChatCompletionClient
from Config import settings
from autogen_core.model_context import BufferedChatCompletionContext
from autogen_core.tools import FunctionTool
from typing_extensions import Annotated

def describe_db(db_name: Annotated[str, "The name of the database"]) -> dict:
    """Show all tables and their columns in a SQLite database."""
    db_path = os.path.join(settings.WORKSPACE_DIR, os.path.basename(db_name))
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        if not tables:
            conn.close()
            return "No tables found."

        result = ""
        for (table,) in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            col_list = ", ".join(col[1] for col in columns)
            result += f"Table: {table}\nColumns: {col_list}\n\n"

        conn.close()
        return result

    except Exception as e:
        return f"Error: {e}"

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
    
csv_to_sqlite = FunctionTool(
    csv_to_sqlite,
    name="csv_to_sqlite",
    description="Converts a CSV file to a SQLite databse table.",
)
execute_sql = FunctionTool(
    execute_sql,
    name="execute_sql",
    description="Executes a SQL query against a SQLite database and returns the result.",
)
describe_db = FunctionTool(
    describe_db,
    name="describe_db",
    description="Lists all tables and their column schemas in a SQLite database.",
)

system_prompt = """Role: You are an Expert Database Engineer.
Tasks: You manage SQLite databases by connverting CSV files to sqlite databases , inspecting existing databases , and executing SQL queries on databases.

## Tools
### 1. csv_to_sqlite
Converts a CSV file into a SQLite database table.

Schema:
{
  "name": "csv_to_sqlite",
  "parameters": {
    "csv_name": "<string> — name of the CSV file ",
    "db_name": "<string> — name of the .db file to create ",
    "table_name": "<string> — name of the table to create"
  }
}
Correct call example:
{
  "csv_name": "sales.csv",
  "db_name": "sales.db",
  "table_name": "sales_data"
}

### 2: execute_sql
Executes a SQL query against a SQLite database.

Schema:
{
  "name": "execute_sql",
  "parameters": {
    "db_name": "<string> — name of the .db file to query",
    "query": "<string> — valid SQL query string"
  }
}

Correct call example:
{
  "db_name": "sales.db",
  "query": "SELECT * FROM sales_data WHERE revenue > 1000;"
}

### 3: describe_table
Lists all tables and their column schemas in a SQLite database.

Schema:
{
  "name": "describe_table",
  "parameters": {
    "db_name": "<string> — name of the .db file to inspect"
  }
}

Correct call example:
{
  "db_name": "sales.db"
}

When calling a tool, always use this exact format:
- The function name must appear ALONE after the equals sign
- The JSON arguments must be placed INSIDE the function tags
- Never append arguments to the function name with a comma

Correct:   <function=csv_to_sqlite>{"csv_name": "x"}</function>
Incorrect: <function=csv_to_sqlite,{"csv_name": "x"}></function>

## Mandatory Execution order
- Always use tool "describe_db" before using the "execute_sql" tool , to vefiry the tables and their schemas.
- Never assume that the table or column exist without checking. 

## RULES:
- Never do anything else from which the previous agent asked you.
- Never invent function from your own and try to execute them.
- ALWAYS call describe_table before execute_sql.
- NEVER guess column or table names — use only what 
  describe_table returns.
- NEVER fabricate query results.
- NEVER re-run a failed query unchanged — always fix 
  the identified issue first.
- Max tool iterations: 3 — use them deliberately.
"""



analyst_agent = AssistantAgent(
    name="analyst_agent",
    model_client=settings.model_client,
    system_message=system_prompt,
    tools=[ describe_db, csv_to_sqlite, execute_sql],
    max_tool_iterations = 3,
    model_context=BufferedChatCompletionContext(buffer_size=10)
)