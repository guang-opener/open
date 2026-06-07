@echo off
chcp 65001 >nul
set PYTHON=C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe
cd /d "%~dp0"

echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║     科技调研报告自动生成工具 - 快速启动     ║
echo  ╚══════════════════════════════════════════════╝
echo.

if "%1"=="" (
    set /p TOPIC="▶ 请输入调研主题 (中文): "
) else (
    set TOPIC=%*
)

if "%TOPIC%"=="" (
    echo 主题不能为空
    pause
    exit /b 1
)

echo.
echo 调研主题: %TOPIC%
echo.
echo ── 第1步: 多源检索 (预计1-2分钟) ──
echo.

"%PYTHON%" -c "import yaml, json, sys; sys.path.insert(0,'.'); from searcher import search_all, save_results; cfg=yaml.safe_load(open('config_template.yaml','r',encoding='utf-8')); cfg['topic']='%TOPIC%'; qs=cfg.get('search',{}).get('journal_keywords',[]); ps=cfg.get('search',{}).get('patent_keywords',[]); r=search_all(queries=qs, sources=cfg['search'].get('sources',['semanticscholar','arxiv']), max_per_source=cfg['search'].get('max_results_per_source',10), year_from=cfg['search'].get('year_from'), year_to=cfg['search'].get('year_to'), patent_queries=ps); save_results(r,'../output/search_results.json'); print(f'检索完成: {len(r)} 条结果'); open('../output/_topic.txt','w',encoding='utf-8').write('%TOPIC%')" 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo 检索失败，请检查网络连接
    pause
    exit /b 1
)

echo.
echo ── 第2步: 请在当前 Claude 对话中说 ──
echo.
echo   "读取 output/search_results.json，分析后生成 analysis_result.json"
echo.
echo ── 第3步: 分析完成后运行 ──
echo.
echo   run.bat write --input output/analysis_result.json
echo.

pause
