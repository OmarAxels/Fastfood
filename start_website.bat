@echo off
REM ——————————————
REM Frontend in its own window
REM ——————————————
start "Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

REM ——————————————
REM Backend in its own window
REM ——————————————
start "Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && python run_server.py"

exit