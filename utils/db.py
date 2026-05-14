import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", 5432),
        dbname=os.getenv("DB_NAME", "ocr_playground"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name VARCHAR(200),
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    # Job history table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS job_history (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            job_id VARCHAR(100) NOT NULL,
            doc_type VARCHAR(50),
            filename VARCHAR(300),
            status VARCHAR(50) DEFAULT 'fulfilled',
            result_json TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    # Safe to run every time — adds column if missing on existing DBs
    cur.execute("""
        ALTER TABLE job_history
        ADD COLUMN IF NOT EXISTS result_json TEXT;
    """)

    cur.execute("SELECT COUNT(*) FROM users;")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO users (username, password, full_name) VALUES ('admin', 'admin123', 'Admin User');"
        )

    conn.commit()
    cur.close()
    conn.close()


def verify_user(username: str, password: str):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM users WHERE username = %s;", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user and user["password"] == password:
        return user
    return None


def create_user(username: str, password: str, full_name: str = ""):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password, full_name) VALUES (%s, %s, %s);",
            (username, password, full_name),
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except psycopg2.errors.UniqueViolation:
        return False


def save_job(user_id: int, job_id: str, doc_type: str, filename: str, status: str = "fulfilled", result_json: str = None):
    """Save a completed job to history."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO job_history (user_id, job_id, doc_type, filename, status, result_json)
        VALUES (%s, %s, %s, %s, %s, %s);
        """,
        (user_id, job_id, doc_type, filename, status, result_json),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_user_history(user_id: int) -> list:
    """Fetch all jobs for a user, newest first."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        SELECT id, job_id, doc_type, filename, status, result_json, created_at
        FROM job_history
        WHERE user_id = %s
        ORDER BY created_at DESC;
        """,
        (user_id,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]


def delete_job(history_id: int, user_id: int):
    """Delete a job from history (only if it belongs to the user)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM job_history WHERE id = %s AND user_id = %s;",
        (history_id, user_id),
    )
    conn.commit()
    cur.close()
    conn.close()
