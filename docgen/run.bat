@echo off
REM ============================================================
REM 科技调研报告生成工具 - Windows 启动脚本
REM ============================================================

set PYTHON=C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe

if not exist "%PYTHON%" (
    echo Python not found at %PYTHON%
    echo Please install Python 3.12 or edit this script.
    pause
    exit /b 1
)

cd /d "%~dp0"

if "%1"=="" (
    echo.
    echo ==========================================================
    echo   科技调研报告自动生成工具
    echo ==========================================================
    echo.
    echo 用法:
    echo   run.bat full           完整流水线 (检索-分析-生成)
    echo   run.bat search         仅多源检索
    echo   run.bat analyze        仅分析筛选
    echo   run.bat write          仅生成文档
    echo   run.bat interactive    交互式引导
    echo.
    echo 示例:
    echo   run.bat full --config config.yaml
    echo   run.bat search --topic "超导接头" --queries "REBCO joint"
    echo   run.bat interactive
    echo.
    pause
    exit /b 0
)

"%PYTHON%" main.py %*
pause
