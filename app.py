from flask import Flask, render_template, request, jsonify
import os
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "history.db")
MAX_CODE_LENGTH = 12000
TIMEOUT_SECONDS = 5


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS run_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                code TEXT NOT NULL,
                result TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)


def save_history(code, result, status):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO run_history (created_at, code, result, status) VALUES (?, ?, ?, ?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), code, result[:5000], status)
        )


def explain_error(result):
    if "SyntaxError" in result:
        return "Syntax error: check brackets, colons, quotes, and indentation."
    if "NameError" in result:
        return "Name error: you may have used a variable or function name that has not been defined."
    if "TypeError" in result:
        return "Type error: check whether the values and data types used by the operation are compatible."
    if "IndentationError" in result:
        return "Indentation error: check the spaces at the start of each line."
    if "ZeroDivisionError" in result:
        return "Zero division error: your code tried to divide a number by zero."
    if "Timeout" in result:
        return "Time limit reached: the program may contain an infinite loop or take too long."
    return ""


@app.route("/")
def index():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT id, created_at, code, result, status FROM run_history ORDER BY id DESC LIMIT 8"
        ).fetchall()
    history = [
        {"id": r[0], "created_at": r[1], "code": r[2], "result": r[3], "status": r[4]}
        for r in rows
    ]
    return render_template("index.html", history=history)


@app.route("/run", methods=["POST"])
def run_code():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")

    if not isinstance(code, str) or not code.strip():
        return jsonify({"ok": False, "output": "Please enter some Python code.", "explanation": ""}), 400
    if len(code) > MAX_CODE_LENGTH:
        return jsonify({"ok": False, "output": "Code is too long. Please keep it under 12,000 characters.", "explanation": ""}), 400

    # Local learning prototype only. Do not expose this endpoint publicly:
    # subprocess execution is not a secure sandbox for untrusted code.
    try:
        with tempfile.TemporaryDirectory(prefix="codesphere_") as temp_dir:
            script_path = os.path.join(temp_dir, "user_code.py")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code)

            completed = subprocess.run(
                [sys.executable, "-I", script_path],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS
            )
            output = completed.stdout
            if completed.stderr:
                output += ("\n" if output else "") + completed.stderr
            if not output.strip():
                output = "(Program finished with no output.)"
            status = "Success" if completed.returncode == 0 else "Error"
    except subprocess.TimeoutExpired:
        output = "Timeout: program ran for more than 5 seconds and was stopped."
        status = "Timeout"
    except Exception as exc:
        output = f"Could not run code: {type(exc).__name__}: {exc}"
        status = "Error"

    save_history(code, output, status)
    return jsonify({
        "ok": status == "Success",
        "output": output,
        "status": status,
        "explanation": explain_error(output)
    })


@app.route("/test", methods=["POST"])
def test_code():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    test_input = data.get("test_input", "")
    expected = data.get("expected", "")

    if not isinstance(code, str) or not code.strip():
        return jsonify({"ok": False, "message": "Enter Python code first."}), 400
    if len(code) > MAX_CODE_LENGTH:
        return jsonify({"ok": False, "message": "Code is too long."}), 400

    try:
        with tempfile.TemporaryDirectory(prefix="codesphere_test_") as temp_dir:
            script_path = os.path.join(temp_dir, "user_code.py")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code)
            completed = subprocess.run(
                [sys.executable, "-I", script_path],
                input=test_input,
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS
            )
            actual = completed.stdout.strip()
            if completed.returncode != 0:
                message = "Test could not run. Check the error shown in the output panel."
                return jsonify({"ok": False, "message": message, "actual": actual, "error": completed.stderr})
            passed = actual == expected.strip()
            return jsonify({
                "ok": passed,
                "message": "Test passed!" if passed else "Test failed. Compare the expected and actual output.",
                "actual": actual,
                "expected": expected.strip()
            })
    except subprocess.TimeoutExpired:
        return jsonify({"ok": False, "message": "Time limit reached. The test was stopped."})


@app.route("/history/clear", methods=["POST"])
def clear_history():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM run_history")
    return jsonify({"ok": True})


init_db()

if __name__ == "__main__":
    # Local-only development server.
    app.run(host="127.0.0.1", port=5000, debug=True)
