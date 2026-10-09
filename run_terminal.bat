@echo off
setlocal
cd /d "%~dp0"

echo =======================================================
echo   [MetalsTerminal] Daily Sync Engine
echo =======================================================
echo.

python -u "%~dp0pipeline.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Pipeline execution failed.
    pause
    exit /b 1
)

echo.
echo =======================================================
echo   [SUCCESS] Price, Scrap, and Reports updated!
echo =======================================================
echo.

git add data/ articles/ index.html price.html scrap.html pipeline.py TASK_HISTORY.md
git commit -m "Auto update MetalsTerminal data" > nul 2>&1

echo [INFO] Local Git commit completed.
echo.
pause
