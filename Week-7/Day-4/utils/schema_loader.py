import sqlite3
from pathlib import Path


def get_db_path(db_dir: Path) -> Path:
    dbs = list(db_dir.glob("*.db"))
    if not dbs:
        raise FileNotFoundError(f"No .db file found in {db_dir}")
    return dbs[0]


def load_schema(db_path: Path, sample_rows: int = 3) -> str:
    conn   = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row[0] for row in cursor.fetchall()]

    if not tables:
        conn.close()
        raise ValueError(f"No tables found in {db_path}")

    lines = [f"Database: {db_path.name}\n"]

    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()   # (cid, name, type, notnull, dflt, pk)

        col_defs = ", ".join(
            f"{col[1]} {col[2]}{'(PK)' if col[5] else ''}"
            for col in columns
        )
        lines.append(f"Table: {table}({col_defs})")

        cursor.execute(f"SELECT * FROM {table} LIMIT {sample_rows};")
        rows      = cursor.fetchall()
        col_names = [col[1] for col in columns]
        if rows:
            lines.append(f"  Sample rows ({', '.join(col_names)}):")
            for row in rows:
                lines.append(f"    {row}")

        lines.append("")

    conn.close()
    return "\n".join(lines)


def get_schema_metadata(db_path: Path) -> dict:
    """
    Returns {table_name: [col_name, ...]} (all lowercase) for schema validation.
    """
    conn   = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    schema = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        schema[table.lower()] = [col[1].lower() for col in cursor.fetchall()]

    conn.close()
    return schema