"""
db.py — Работа с SQLite без SQLAlchemy.
Простая обёртка для выполнения запросов к БД.
"""
import sqlite3
import os
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")


@contextmanager
def get_db():
    """Контекстный менеджер для работы с БД."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Создаёт все таблицы БД."""
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'tutor',
            department TEXT,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            answers_json TEXT,
            is_complete INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id INTEGER NOT NULL REFERENCES tests(id),
            user_id INTEGER NOT NULL REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            burnout_level TEXT NOT NULL,
            scores_json TEXT NOT NULL,
            levels_json TEXT NOT NULL,
            fired_rules_json TEXT
        );

        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            result_id INTEGER NOT NULL REFERENCES results(id),
            user_id INTEGER NOT NULL REFERENCES users(id),
            rule_id TEXT,
            rule_name TEXT,
            recommendation_text TEXT,
            explanation_text TEXT,
            source_scale TEXT
        );

        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            department TEXT,
            period_year INTEGER,
            period_month INTEGER,
            count_low INTEGER DEFAULT 0,
            count_medium INTEGER DEFAULT 0,
            count_high INTEGER DEFAULT 0
        );
        """)
    logger.info("База данных инициализирована.")
