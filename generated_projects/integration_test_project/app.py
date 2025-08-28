from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('tasks.db')
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT,
            due_date TEXT,
            completed BOOLEAN DEFAULT FALSE
        )
    """)
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET', 'POST'])
def tasks():
    if request.method == 'POST':
        # Add task logic
        pass
    else:
        # Get tasks logic
        pass

if __name__ == '__main__':
    init_db()
    app.run(debug=True)