
import sqlite3
import json

import os

DB_NAME = os.getenv("DATABASE_PATH", "fortebank.db")

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                result TEXT
            )
        """)


def save_job(job_id, status, result=None):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO jobs
            (job_id, status, result)
            VALUES (?, ?, ?)
            """,
            (
                job_id,
                status,
                json.dumps(result) if result is not None else None
            )
        )


def get_job_from_db(job_id):
    with sqlite3.connect(DB_NAME) as conn:
        row = conn.execute(
            """
            SELECT status, result
            FROM jobs
            WHERE job_id = ?
            """,
            (job_id,)
        ).fetchone()

    if row is None:
        return None

    status, result = row

    response = {
        "job_id": job_id,
        "status": status
    }

    if result is not None:
        response.update(json.loads(result))

    return response


def get_unfinished_jobs():
    """
    Получает все незавершённые задачи.
    """
    with sqlite3.connect(DB_NAME) as conn:
        rows = conn.execute(
            """
            SELECT job_id
            FROM jobs
            WHERE status = 'processing'
            """
        ).fetchall()

    return [row[0] for row in rows]
