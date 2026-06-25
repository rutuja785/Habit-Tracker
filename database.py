import sqlite3
import os
from datetime import date

DB_PATH = os.path.join(os.path.dirname(__file__), "habits.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS habits (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                name            TEXT    NOT NULL,
                description     TEXT    DEFAULT '',
                reminder_time   TEXT    DEFAULT NULL,
                target_streak   INTEGER DEFAULT 7,
                current_streak  INTEGER DEFAULT 0,
                longest_streak  INTEGER DEFAULT 0,
                created_at      TEXT    DEFAULT (date('now'))
            );

            CREATE TABLE IF NOT EXISTS habit_logs (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL REFERENCES habits(id) ON DELETE CASCADE,
                date     TEXT    NOT NULL,
                completed INTEGER DEFAULT 0,
                UNIQUE(habit_id, date)
            );
        """)


# ── Habits ────────────────────────────────────────────────────────────────────

def create_habit(name: str, description: str, reminder_time: str | None, target_streak: int) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO habits (name, description, reminder_time, target_streak) VALUES (?,?,?,?)",
            (name, description, reminder_time, target_streak),
        )
        return cur.lastrowid


def get_all_habits() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM habits ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]


def get_habit(habit_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM habits WHERE id=?", (habit_id,)).fetchone()
        return dict(row) if row else None


def update_habit(habit_id: int, name: str, description: str, reminder_time: str | None, target_streak: int):
    with get_connection() as conn:
        conn.execute(
            "UPDATE habits SET name=?, description=?, reminder_time=?, target_streak=? WHERE id=?",
            (name, description, reminder_time, target_streak, habit_id),
        )


def update_streaks(habit_id: int, current: int, longest: int):
    with get_connection() as conn:
        conn.execute(
            "UPDATE habits SET current_streak=?, longest_streak=? WHERE id=?",
            (current, longest, habit_id),
        )


def delete_habit(habit_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM habits WHERE id=?", (habit_id,))


# ── Logs ──────────────────────────────────────────────────────────────────────

def log_habit(habit_id: int, log_date: str, completed: bool):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO habit_logs (habit_id, date, completed) VALUES (?,?,?)
               ON CONFLICT(habit_id, date) DO UPDATE SET completed=excluded.completed""",
            (habit_id, log_date, int(completed)),
        )


def get_logs_for_habit(habit_id: int) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM habit_logs WHERE habit_id=? ORDER BY date DESC",
            (habit_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_log_for_date(habit_id: int, log_date: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM habit_logs WHERE habit_id=? AND date=?",
            (habit_id, log_date),
        ).fetchone()
        return dict(row) if row else None


def get_logs_date_range(habit_id: int, start: str, end: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM habit_logs WHERE habit_id=? AND date BETWEEN ? AND ? ORDER BY date",
            (habit_id, start, end),
        ).fetchall()
        return [dict(r) for r in rows]