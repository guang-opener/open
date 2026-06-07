# 科技调研报告自动生成工具

自动从海内外专利网和科技期刊检索信息，经 LLM 智能筛选分析后，生成结构化 Word 文档。

## 工作流程

```
专利网/期刊 → 搜索聚合 → 相关性筛选 → 详细报告撰写 → .docx 输出
  (多源)       (去重)     (关键词+LLM)   (结构化章节)   (python-docx)
```

## 快速开始

### 1. 交互式模式 (最简单)

双击 `run.bat` 或在终端:

```bash
run.bat interactive
```

按提示输入调研主题、关键词，自动完成全流程。

### 2. 命令行模式

```bash
# 完整流水线 (需要 config.yaml)
run.bat full --config config.yaml

# 分步执行:
run.bat search --topic "超导接头" --queries "REBCO joint" "HTS soldering"
run.bat analyze --input search_results.json
run.bat write --input analysis_result.json --output report.docx
```

### 3. Python 直接调用

```python
from searcher import search_all, save_results
from writer import quick_report

# 检索
results = search_all(
    queries=["REBCO coated conductor joint"],
    sources=["semanticscholar", "arxiv"],
    max_per_source=10,
    patent_queries=["superconducting tape joint"],
)
save_results(results, "results.json")

# 生成文档 (适合已有内容)
quick_report(
    topic="超导带材接头技术调研",
    sections={"摘要": "...", "技术背景": "...", "结论": "..."},
    output_path="report.docx",
)
```

## 依赖

- Python 3.12+
- `python-docx` - Word 文档生成
- `docxtpl` - Word 模板引擎 (可选)
- `requests` - HTTP 请求
- `beautifulsoup4` + `lxml` - HTML/XML 解析
- `pyyaml` - 配置文件解析
- `anthropic` - Claude API (可选，也可手动模式)

第一次安装: `pip install python-docx docxtpl requests pyyaml beautifulsoup4 lxml anthropic`

## 文件结构

```
docgen/
├── config.yaml         # 配置文件 (调研主题/关键词/输出设置)
├── main.py             # 主控 CLI (full/search/analyze/write/interactive)
├── searcher.py         # 多源检索模块 (Semantic Scholar/arXiv/CrossRef/Google Patents)
├── analyzer.py         # LLM 分析筛选模块 (关键词过滤 + Claude API 深度分析)
├── writer.py           # Word 文档生成模块 (python-docx)
├── run.bat             # Windows 一键启动脚本
└── templates/          # docxtpl 模板目录 (可选)
output/                 # 输出目录 (自动创建)
```

## 支持的检索源

| 检索源 | 类型 | 需要 API Key | 说明 |
|--------|------|:---:|------|
| Semantic Scholar | 期刊/论文 | 否 | 覆盖面广，免费 |
| arXiv | 预印本 | 否 | 物理/材料学前沿 |
| CrossRef | 期刊 (DOI) | 否 | 全球最大 DOI 注册库 |
| Google Patents | 专利 | 否 | 全球专利检索 |

## 文档输出结构

生成的标准报告包含:

- **标题页**: 中英文标题、副标题、日期
- **摘要**: 调研主题和主要发现概述
- **技术背景与实例**: 原理、发展历程、应用案例
- **专利分析**: 专利布局、主要专利权人、技术路径
- **技术对比分析**: 不同技术方案的指标对比表
- **图文技术介绍**: 工艺流程、关键参数、常见问题
- **结论与展望**: 总结与未来趋势
- **参考文献**: 自动汇总引用来源

## 分析模式

### 自动模式 (需 Claude API Key)

在 `config.yaml` 中配置 API Key 或设置环境变量 `ANTHROPIC_API_KEY`:

```yaml
claude_api:
  api_key: "sk-ant-..."
  model: "claude-sonnet-4-6"
```

### 手动模式 (无需 API Key)

工具会生成结构化分析提示词文件，用户将内容粘贴到 Claude 中处理后，将结果保存为 JSON，再执行 `write` 命令生成文档。
