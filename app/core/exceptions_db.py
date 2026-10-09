# Copyright 2026 Ihor Kozlitin
# SPDX-License-Identifier: Apache-2.0

import sqlite3
from pathlib import Path
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "exceptions.db"


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Initializes SQLite database and creates exceptions table if it does not exist.
    """
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS exceptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def get_all_exceptions() -> List[Dict[str, Any]]:
    """
    Retrieves all exception text fragments from SQLite database.
    """
    init_db()
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT id, text, created_at FROM exceptions ORDER BY id DESC")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def get_exception_texts() -> List[str]:
    """
    Retrieves all exception strings for fast matching during entity analysis.
    """
    init_db()
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT text FROM exceptions")
        return [r["text"] for r in cursor.fetchall()]


def add_exception(text: str) -> Dict[str, Any]:
    """
    Adds a new unique text fragment to exceptions database.
    """
    clean_text = text.strip()
    if not clean_text:
        raise ValueError("Текстовий фрагмент виключення не може бути порожнім.")

    init_db()
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO exceptions (text) VALUES (?)",
                (clean_text,)
            )
            conn.commit()
            exc_id = cursor.lastrowid
            
            # Fetch created item
            row = conn.execute("SELECT id, text, created_at FROM exceptions WHERE id = ?", (exc_id,)).fetchone()
            return dict(row)
    except sqlite3.IntegrityError:
        raise ValueError(f"Строка «{clean_text}» вже існує у списку виключень.")


def update_exception(exception_id: int, new_text: str) -> Dict[str, Any]:
    """
    Updates text fragment of an existing exception in SQLite database.
    """
    clean_text = new_text.strip()
    if not clean_text:
        raise ValueError("Текстовий фрагмент виключення не може бути порожнім.")

    init_db()
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "UPDATE exceptions SET text = ? WHERE id = ?",
                (clean_text, exception_id)
            )
            conn.commit()
            if cursor.rowcount == 0:
                raise KeyError(f"Виключення з ID {exception_id} не знайдено.")
            
            row = conn.execute("SELECT id, text, created_at FROM exceptions WHERE id = ?", (exception_id,)).fetchone()
            return dict(row)
    except sqlite3.IntegrityError:
        raise ValueError(f"Строка «{clean_text}» вже існує у списку виключень.")


def delete_exception(exception_id: int) -> bool:
    """
    Deletes an exception from SQLite database by ID.
    """
    init_db()
    with get_db_connection() as conn:
        cursor = conn.execute("DELETE FROM exceptions WHERE id = ?", (exception_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise KeyError(f"Виключення з ID {exception_id} не знайдено.")
        return True
