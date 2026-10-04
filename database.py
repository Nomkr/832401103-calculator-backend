"""SQLite persistence layer for calculation history.

Exposes:
    init_db()              create the history table (idempotent)
    add_history(expr, r)   insert one record
    get_history()          list all records, newest first
    delete_history(id)     delete one record; returns whether it existed
    clear_history()        delete all records
"""

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime

# The database file lives next to this module unless CALCULATOR_DB_FILE
# points elsewhere (used on platforms with a persistent disk).
DB_FILE = os.getenv(
    "CALCULATOR_DB_FILE",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "calculator.db"),
)


def get_connection():
    """Open a connection to the database."""
    db_dir = os.path.dirname(os.path.abspath(DB_FILE))
    os.makedirs(db_dir, exist_ok=True)
    # A timeout avoids "database is locked" under concurrent writes.
    conn = sqlite3.connect(DB_FILE, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


@contextmanager
def db_session():
    """Yield a connection that commits on success and rolls back on error."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create the history table if it does not exist."""
    with db_session() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS calculation_history (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                expression TEXT NOT NULL,
                result     TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def add_history(expression, result):
    """Insert one calculation record with the current timestamp."""
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with db_session() as conn:
        conn.execute(
            "INSERT INTO calculation_history (expression, result, created_at) VALUES (?, ?, ?)",
            (expression, str(result), created_at),
        )


def get_history():
    """Return all records as dicts, newest first."""
    with db_session() as conn:
        rows = conn.execute(
            "SELECT id, expression, result, created_at FROM calculation_history ORDER BY id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def delete_history(history_id):
    """Delete one record; return True if it existed."""
    with db_session() as conn:
        cursor = conn.execute("DELETE FROM calculation_history WHERE id = ?", (history_id,))
        deleted = cursor.rowcount > 0
    return deleted


def clear_history():
    """Delete all records."""
    with db_session() as conn:
        conn.execute("DELETE FROM calculation_history")


if __name__ == "__main__":
    init_db()
    add_history("1+2", 3)
    add_history("(2+3)*4", 20)

    print("History (newest first):")
    for row in get_history():
        print(row)

    latest = get_history()[0]
    delete_history(latest["id"])
    print("After deleting the latest:")
    for row in get_history():
        print(row)
