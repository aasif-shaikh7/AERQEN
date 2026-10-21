@echo off
REM Start the AERQEN chat app. Double-click this file (or run it) and keep the
REM window open. It prints a link for this PC and a link for your phone (same WiFi).
cd /d "%~dp0"
".venv\Scripts\python.exe" -m app.web.server
pause
