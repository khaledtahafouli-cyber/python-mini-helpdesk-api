import os
import sqlite3
from datetime import datetime

from flask import Flask, jsonify, request

app = Flask(__name__)

DB_DIR = "data"
DB_FILE = os.path.join(DB_DIR, "tasks.db")


def get_db_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL DEFAULT 'Open',
            priority TEXT NOT NULL DEFAULT 'Medium',
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def validate_status(status):
    valid_statuses = ["Open", "In Progress", "Completed"]
    if status not in valid_statuses:
        raise ValueError(f"Status must be one of: {valid_statuses}")


def validate_priority(priority):
    valid_priorities = ["Low", "Medium", "High"]
    if priority not in valid_priorities:
        raise ValueError(f"Priority must be one of: {valid_priorities}")


@app.get("/")
def home():
    return jsonify({
        "message": "Mini Help Desk API",
        "endpoints": {
            "GET /tasks": "List all tasks",
            "POST /tasks": "Create a task",
            "GET /tasks/<id>": "Get a task by ID",
            "PUT /tasks/<id>": "Update a task",
            "DELETE /tasks/<id>": "Delete a task",
            "GET /health": "Health check",
        },
    })


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.get("/tasks")
def list_tasks():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM tasks ORDER BY id ASC").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows]), 200


@app.post("/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    status = (data.get("status") or "Open").strip()
    priority = (data.get("priority") or "Medium").strip()

    if not title:
        return jsonify({"error": "Title is required."}), 400

    try:
        validate_status(status)
        validate_priority(priority)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db_connection()
    cursor = conn.execute(
        """
        INSERT INTO tasks (title, description, status, priority, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (title, description, status, priority, created_at),
    )
    conn.commit()
    task_id = cursor.lastrowid
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()

    return jsonify(dict(task)), 201


@app.get("/tasks/<int:task_id>")
def get_task(task_id):
    conn = get_db_connection()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()

    if task is None:
        return jsonify({"error": "Task not found."}), 404

    return jsonify(dict(task)), 200


@app.put("/tasks/<int:task_id>")
def update_task(task_id):
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"error": "No JSON body provided."}), 400

    conn = get_db_connection()
    existing = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if existing is None:
        conn.close()
        return jsonify({"error": "Task not found."}), 404

    title = data.get("title", existing["title"])
    description = data.get("description", existing["description"])
    status = data.get("status", existing["status"])
    priority = data.get("priority", existing["priority"])

    try:
        validate_status(status)
        validate_priority(priority)
    except ValueError as exc:
        conn.close()
        return jsonify({"error": str(exc)}), 400

    title = str(title).strip()
    if not title:
        conn.close()
        return jsonify({"error": "Title cannot be empty."}), 400

    conn.execute(
        """
        UPDATE tasks
        SET title = ?, description = ?, status = ?, priority = ?
        WHERE id = ?
        """,
        (title, description, status, priority, task_id),
    )
    conn.commit()
    updated = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()

    return jsonify(dict(updated)), 200


@app.delete("/tasks/<int:task_id>")
def delete_task(task_id):
    conn = get_db_connection()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task is None:
        conn.close()
        return jsonify({"error": "Task not found."}), 404

    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Task {task_id} deleted."}), 200


init_db()

if __name__ == "__main__":
    app.run(debug=True)
