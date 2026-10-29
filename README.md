# CodeSphere Lite

A beginner-friendly local Python developer workspace built with Flask, HTML, CSS, JavaScript, and SQLite.

## Features

- Run Python code and view output
- Basic explanations for common Python errors
- Compare program output with expected output
- Keep a small local history of recent runs
- Responsive dark dashboard UI

## Requirements

- Python 3.10 or newer (Python 3.9 may work with a compatible Flask release)
- VS Code or another text editor

Java, Node.js, and a C/C++ compiler are not required for this first version.

## Windows setup

1. Extract `CodeSphere_Lite.zip`.
2. Open the extracted `CodeSphere_Lite` folder in VS Code.
3. Open **Terminal → New Terminal**.
4. (Recommended) Create a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, you can skip activation and run the install command below with `python -m pip`.

5. Install Flask:

   ```powershell
   python -m pip install -r requirements.txt
   ```

6. Start the app:

   ```powershell
   python app.py
   ```

7. Open this address in your browser:

   `http://127.0.0.1:5000`

## Important safety note

This is a learning prototype intended to run locally on your own computer. The code runner executes submitted Python code as a local process and is **not a secure sandbox**. Only run code you trust. Do not expose this app to the public internet or use it for untrusted users without proper operating-system/container isolation and resource limits.

## Suggested future improvements

- Add user-defined test cases and more detailed test reports
- Improve error explanations
- Add search/filter for run history
- Add Java, JavaScript, and C/C++ support after installing their runtimes/compilers
- Add authentication and a secure isolated execution environment before any public deployment
