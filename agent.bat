@echo off
REM AERQEN agent launcher. Usage (no quotes needed):
REM     agent remember my favourite colour is blue
REM     agent what is my favourite colour
REM Uses the project's own Python (.venv) and always runs in --agent mode.
"%~dp0.venv\Scripts\python.exe" -m app.entrypoint.cli --agent %*
