# database.py
import sqlite3
import json
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        question TEXT,
        answer TEXT,
        method TEXT,
        created_at DATETIME DEFAULT (datetime('now'))
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS task_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        convo_id INTEGER,
        agent TEXT,
        tool TEXT,
        status TEXT,
        confidence REAL,
        meta TEXT,
        created_at DATETIME DEFAULT (datetime('now'))
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS reflection (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_log_id INTEGER,
        notes TEXT,
        created_at DATETIME DEFAULT (datetime('now'))
    )""")
    conn.commit()
    return conn

_db_conn = init_db()

def save_conversation(user, question, answer=None, method=None):
    cur = _db_conn.cursor()
    cur.execute(
        "INSERT INTO conversations (user, question, answer, method) VALUES (?, ?, ?, ?)",
        (user, question, answer, method)
    )
    _db_conn.commit()
    return cur.lastrowid


def update_conversation_answer(convo_id, answer, method):
    """
    Update the conversation record with the final answer and method.
    Converts dict answers to JSON strings automatically.
    """
    cur = _db_conn.cursor()

    # Convert dicts to JSON string
    if isinstance(answer, dict):
        answer = json.dumps(answer)

    cur.execute(
        "UPDATE conversations SET answer=?, method=? WHERE id=?",
        (answer, method, convo_id)
    )
    _db_conn.commit()


def save_task_log(convo_id, agent, tool, status, confidence, meta=None):
    cur = _db_conn.cursor()
    meta_json = json.dumps(meta or {})
    cur.execute(
        "INSERT INTO task_logs (convo_id, agent, tool, status, confidence, meta) VALUES (?, ?, ?, ?, ?, ?)",
        (convo_id, agent, tool, status, confidence, meta_json)
    )
    _db_conn.commit()
    return cur.lastrowid

def save_reflection(task_log_id, notes):
    cur = _db_conn.cursor()
    cur.execute("INSERT INTO reflection (task_log_id, notes) VALUES (?, ?)", (task_log_id, notes))
    _db_conn.commit()
    return cur.lastrowid
