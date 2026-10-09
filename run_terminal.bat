@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ============================================================
echo   ⚡ MetalsTerminal 9시 정기 자동 동기화 엔진
echo ============================================================
echo.

cd /d "%~dp0"

echo [*] 파이썬 파이프라인 가동 (Price + Scrap + Report 동시 갱신)...
python pipeline.py
if errorlevel 1 (
    echo [경고] 파이프라인 실행 중 오류가 발생했습니다.
    pause
    exit /b 1
)

echo.
echo [*] Git 변경 사항 명시적 스테이징 및 커밋...
git add data/ articles/ index.html price.html scrap.html pipeline.py TASK_HISTORY.md
git commit -m "chore(auto): daily update for prices, scrap, and reports [%date%]"

echo.
echo ============================================================
echo   🎉 MetalsTerminal 일일 동기화가 성공적으로 완료되었습니다!
echo ============================================================
echo.
timeout /t 5
