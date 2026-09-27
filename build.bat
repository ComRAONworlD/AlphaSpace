@echo off
chcp 65001 > nul
echo ========================================================
echo   AlphaSpace (통계 데이터 분석 & 확률분포 도구) 빌드 시작
echo ========================================================
echo.

set PYTHON_EXE=python
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe -m PyInstaller --version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_EXE=.venv\Scripts\python.exe
    )
)

echo [사용 Python 환경: %PYTHON_EXE%]
"%PYTHON_EXE%" --version
echo.

echo [1/3] 앱 아이콘 및 리소스 검증/생성...
if not exist "app_icon.ico" (
    echo 아이콘 생성 중...
    "%PYTHON_EXE%" create_icon.py
)

echo.
echo [2/3] PyInstaller 단일 독립 실행 파일 빌드 실행 중 (AlphaSpace.spec)...
echo 잠시만 기다려 주세요 (약 1~2분 소요)...
"%PYTHON_EXE%" -m PyInstaller --noconfirm --clean AlphaSpace.spec

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] 빌드 중 오류가 발생했습니다!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ========================================================
echo [3/3] 빌드 완료! 
echo 독립 실행 파일 위치: dist\AlphaSpace.exe
echo ========================================================
echo.
pause
