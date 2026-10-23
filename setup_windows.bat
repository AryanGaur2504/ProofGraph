@echo off
setlocal
cd /d "%~dp0"
title ProofGraph - first-time setup

echo === AICTE ProofGraph (synthetic demonstration) - setup ===
echo Project root: %CD%
if not exist "backend\requirements.txt" (
  echo ERROR: Missing backend\requirements.txt. Extract the FULL ZIP before running this script.
  pause
  exit /b 1
)
if not exist "frontend\package.json" (
  echo ERROR: Missing frontend\package.json. Extract the FULL ZIP before running this script.
  pause
  exit /b 1
)
where npm >nul 2>&1
if errorlevel 1 (
  echo ERROR: Node.js/npm is not installed or not in PATH. Install Node.js 20+.
  pause
  exit /b 1
)
if not exist "backend\.venv\Scripts\python.exe" (
  echo Creating Python virtual environment...
  where py >nul 2>&1
  if errorlevel 1 (
    python -m venv "backend\.venv"
  ) else (
    py -3 -m venv "backend\.venv"
  )
  if errorlevel 1 goto :failed
)

echo Installing Python dependencies from backend\requirements.txt...
"backend\.venv\Scripts\python.exe" -m pip install -r "backend\requirements.txt"
if errorlevel 1 goto :failed

if not exist "backend\.env" copy /Y "backend\.env.example" "backend\.env" >nul
if not exist "frontend\.env.local" copy /Y "frontend\.env.example" "frontend\.env.local" >nul

echo Installing frontend dependencies...
pushd "frontend"
call npm install
if errorlevel 1 (
  popd
  goto :failed
)
popd

echo.
echo Setup completed. Now double-click start_windows.bat
pause
exit /b 0

:failed
echo.
echo SETUP FAILED. Review the error above, then run setup_windows.bat again.
pause
exit /b 1
