@echo off
chcp 65001 > nul
echo ========================================================
echo   AlphaSpace (통계 확률분포 분석 도구) 단일 실행본 빌드 시작
echo ========================================================
echo.

set PYTHON_EXE=.venv\Scripts\python.exe
if not exist "%PYTHON_EXE%" (
    set PYTHON_EXE=python
)

echo [1/3] 앱 아이콘 리소스 확인...
if not exist "app_icon.ico" (
    echo 아이콘 생성 스크립트 실행 중...
    "%PYTHON_EXE%" -c "import create_icon; create_icon.create_app_icon()"
)

echo.
echo [2/3] PyInstaller 단일 독립 실행 파일 빌드 실행 중 (AlphaSpace.spec)...
echo 잠시만 기다려 주세요...
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
