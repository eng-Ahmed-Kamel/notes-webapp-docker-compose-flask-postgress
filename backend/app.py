from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "notesdb")
DB_USER = os.getenv("DB_USER", "notesuser")
DB_PASS = os.getenv("DB_PASS", "notespwd")

def connect_db():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )


@app.route("/api/notes", methods=["GET"])
def get_notes():

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT id, title, content, created_at FROM notes ORDER BY created_at DESC")

    rows = cur.fetchall()

    notes = []

    for r in rows:
        notes.append({
            "id": r[0],
            "title": r[1],
            "content": r[2],
            "createdAt": r[3].isoformat()
        })

    cur.close()
    conn.close()

    return jsonify(notes)


@app.route("/api/notes", methods=["POST"])
def add_note():

    data = request.json
    title = data["title"]
    content = data["content"]

    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO notes (title, content, created_at) VALUES (%s,%s,%s)",
        (title, content, datetime.utcnow())
    )

    conn.commit()

    cur.close()
    conn.close()

    return {"message": "note added"}


@app.route("/api/notes/<int:id>", methods=["DELETE"])
def delete_note(id):

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM notes WHERE id=%s", (id,))

    conn.commit()

    cur.close()
    conn.close()

    return {"message": "note deleted"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)
