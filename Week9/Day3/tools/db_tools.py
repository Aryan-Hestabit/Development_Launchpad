import sqlite3
import pandas as pd
import os
from autogen_agentchat.agents import AssistantAgent
import settings
from autogen_core.tools import FunctionTool
from typing_extensions import Annotated

def describe_table(db_name: Annotated[str, "The name of the database"], table_name: Annotated[str, "The name of the table"]) -> dict:
    """Give summary for the database table structure, including columns, data types, and relationships."""
    db_path = os.path.join(settings.WORKSPACE_DIR, os.path.basename(db_name))

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()

            cursor.execute(f"PRAGMA foreign_key_list({table_name});")
            foreign_keys = cursor.fetchall()

            cursor.execute(f"PRAGMA index_list({table_name});")
            indexes = cursor.fetchall()

            return {
                "table": table_name,
                "columns": columns,
                "foreign_keys": foreign_keys,
                "indexes": indexes
            }

    except sqlite3.Error as e:
        return {"error": str(e)}

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
        return f"Conversion Error: {str(e)}"
    
csv_to_sqlite = FunctionTool(
    csv_to_sqlite,
    name="csv_to_sqlite",
    description="Converts a CSV file in the workspace to a SQLite table. Args: csv_name, db_name, table_name",
)
execute_sql = FunctionTool(
    execute_sql,
    name="execute_sql",
    description="Executes an SQL query on a specified SQLite database in the workspace. Args: db_name, query",
)
describe_table = FunctionTool(
    describe_table,
    name="describe_table",
    description="Describes the structure of a specified table in a SQLite database. Args: db_name, table_name",
)
    
db_agent = AssistantAgent(
    name="db_agent",
    model_client=settings.model_client,
    tools=[execute_sql, csv_to_sqlite, describe_table],
    description=("SQLite database specialist. Three tools: "
        "csv_to_sqlite(csv_name, db_name, table_name) to import CSV data into sqlite database file, "
        "describe_table(db_name, table_name) to inspect table schema, "
        "execute_sql(db_name, query) to run SQL queries. "
        "Cannot Convert Database file to CSV file."),
    max_tool_iterations=3,
    reflect_on_tool_use=True,
    system_message="""You are part of a Agentic AI team and You are the @db_agent, a specialist in managing and querying SQLite Databases.
    Tools: 3 Tools which can be used: 1.csv_to_sqlite 2.describe_table 3.execute_sql

    Rules:
    -always run describe_table before executing the execute_sql to understand the table structure and avoid errors.
    -You can only convert csv file to a database file but you cannot convert a database file to a csv file. 
    If asked to do so please respond with "I can only convert CSV files to SQLite databases, but I cannot convert databases back to CSV files.".
    - Always provide the exact filenames, database names, and the table names when using your tools. Do not say "use the previous file" — always specify the exact file.
    - If encountered any error while using the tools, analyze the error message carefully and pass the error in a string format to the @planner_agent.

    CRITICAL:
    - Never reply with an empty string. If you have no data to return, please return "No data to return." instead of an empty string.
    """
)
