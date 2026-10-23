@echo off
setlocal
cd /d "%~dp0"
title AICTE ProofGraph (local demo)
if not exist "backend\.venv\Scripts\python.exe" (
  echo ERROR: Setup not done. Run setup_windows.bat first.
  pause
  exit /b 1
)
if not exist "frontend\node_modules\next" (
  echo ERROR: Frontend dependencies missing. Run setup_windows.bat first.
  pause
  exit /b 1
)
if not exist "backend\proofgraph.db" (
  echo Initializing the synthetic demo database...
  pushd "backend"
  ".venv\Scripts\python.exe" seed.py
  if errorlevel 1 (
    popd
    pause
    exit /b 1
  )
  popd
)
echo Starting services. Open http://127.0.0.1:3000/demo after login.
"backend\.venv\Scripts\python.exe" run.py
if errorlevel 1 pause
