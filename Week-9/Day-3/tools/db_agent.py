import sqlite3
import pandas as pd
import os
from autogen_agentchat.agents import AssistantAgent
import settings
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

def execute_sql(db_name: Annotated[str, "The name of the database"], query: Annotated[str, "The SQL query to execute"]) -> str:
    """Executes SQL queries (SELECT or Modification) on a database file."""
    db_path = os.path.join(settings.WORKSPACE_DIR, os.path.basename(db_name))
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

def csv_to_sqlite(
        csv_name: Annotated[str, "The name of the CSV file"], 
        db_name: Annotated[str, "The name of the database"], 
        table_name: Annotated[str, "The name of the table"]
        ) -> str:
    """Converts a workspace CSV into a SQLite table for analysis."""
    csv_path = os.path.join(settings.WORKSPACE_DIR, os.path.basename(csv_name))
    db_path = os.path.join(settings.WORKSPACE_DIR, os.path.basename(db_name))
    try:
        df = pd.read_csv(csv_path)
        with sqlite3.connect(db_path) as conn:
            df.to_sql(table_name, conn, if_exists='replace', index=False)
        return f"Created table '{table_name}' in '{db_name}' from {csv_name}."
    except Exception as e:
        return f"Error: {str(e)}"
    
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

### 3: describe_db
Lists all tables and their column schemas in a SQLite database.

Schema:
{
  "name": "describe_db",
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
Never Generate this: <function=csv_to_sqlite,{"csv_name": "x"}></function>

## Mandatory Execution order
- Always use tool "describe_db" before using the "execute_sql" tool , to vefiry the tables and their schemas.
- Never assume that the table or column exist without checking. 

## HOW YOU THINK AND ACT
Thought1: I need to find the total number users in the user.db database file. let me first inspect the schema of user.db
Act1: decribe_table[user.db]
Observe1: The schemas of the tables in user.db
Thought2: if the table exists , generate a sql query to count the total number of rows in the database
Act2: execute_sql[query]
Observe2: what did the query returned , if it returned what was asked to you, summarize output based on the query asked to you.

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

db_agent = AssistantAgent(
    name="db_agent",
    model_client=settings.model_client,
    tools=[execute_sql, csv_to_sqlite, describe_db],
    description="Runs SQL queries on SQLite databases and imports CSV files into SQLite tables.",
    max_tool_iterations=3,
    reflect_on_tool_use=True,
    system_message= system_prompt,
    tool_call_summary_format="Tool: {tool_name}\nResult: {result}"
)