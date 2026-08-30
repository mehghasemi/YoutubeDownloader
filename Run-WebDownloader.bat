@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>&1
if errorlevel 1 (
  echo Python was not found. Please install Python 3.10 or newer.
  pause
  exit /b 1
)
python -m pip install -r requirements-web.txt
if errorlevel 1 (
  echo Failed to install web dependencies.
  pause
  exit /b 1
)
start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:5000'"
python web_app.py
endlocal
