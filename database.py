import sqlite3
from config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_type TEXT NOT NULL DEFAULT 'text',
                text_content TEXT,
                media_file_id TEXT,
                category TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def add_idea(content_type: str, category: str, text_content: str = None, media_file_id: str = None):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO ideas (content_type, text_content, media_file_id, category, status) VALUES (?, ?, ?, ?, 'new')",
            (content_type, text_content, media_file_id, category.strip())
        )
        conn.commit()

def get_random_idea(category: str = None):
    with get_connection() as conn:
        cursor = conn.cursor()
        if category:
            cursor.execute(
                "SELECT * FROM ideas WHERE status = 'new' AND category = ? ORDER BY RANDOM() LIMIT 1",
                (category,)
            )
        else:
            cursor.execute(
                "SELECT * FROM ideas WHERE status = 'new' ORDER BY RANDOM() LIMIT 1"
            )
        return cursor.fetchone()

def get_idea_by_id(idea_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ideas WHERE id = ?", (idea_id,))
        return cursor.fetchone()

def update_idea_status(idea_id: int, status: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE ideas SET status = ? WHERE id = ?", (status, idea_id))
        conn.commit()

def update_idea_content(idea_id: int, content_type: str, text_content: str = None, media_file_id: str = None):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE ideas SET content_type = ?, text_content = ?, media_file_id = ? WHERE id = ?",
            (content_type, text_content, media_file_id, idea_id)
        )
        conn.commit()

def update_idea_category(idea_id: int, new_category: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE ideas SET category = ? WHERE id = ?", (new_category.strip(), idea_id))
        conn.commit()

def delete_idea(idea_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ideas WHERE id = ?", (idea_id,))
        conn.commit()

def get_categories():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT category FROM ideas WHERE status = 'new' ORDER BY category"
        )
        return [row['category'] for row in cursor.fetchall()]

def get_ideas_by_status(status: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM ideas WHERE status = ? ORDER BY id DESC",
            (status,)
        )
        return cursor.fetchall()