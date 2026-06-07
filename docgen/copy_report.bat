@echo off
chcp 65001 >nul
set PYTHON=C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe
set BASE=f:\桌面\AI Code\output

echo.
echo  整理输出文件到专题文件夹
echo  ==========================================
echo.
set /p FOLDER="专题文件夹名: "

if "%FOLDER%"=="" set FOLDER=调研报告

set REPORT_DIR=%BASE%\%FOLDER%
mkdir "%REPORT_DIR%" 2>nul

echo.
echo 正在复制文件...

for %%f in ("%BASE%\*.docx" "%BASE%\*.json") do (
    copy "%%f" "%REPORT_DIR%\" >nul 2>nul
    echo   %%~nxf
)

if exist "%BASE%\figures" (
    xcopy "%BASE%\figures\*" "%REPORT_DIR%\figures\" /E /I /Q >nul 2>nul
    echo   figures\
)

echo.
echo ==========================================
echo  完成! 文件已保存到:
echo  %REPORT_DIR%
echo ==========================================
echo.

explorer "%REPORT_DIR%"
pause
