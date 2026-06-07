#!/usr/bin/env python3
"""
科技调研报告自动生成工具 - 主控脚本

用法:
    # 完整流水线
    python main.py full --config config.yaml

    # 仅检索
    python main.py search --topic "REBCO超导接头" --output results.json

    # 仅分析 (从已有检索结果)
    python main.py analyze --input results.json --output analysis.json

    # 仅生成文档 (从已有分析结果)
    python main.py write --input analysis.json --output report.docx

    # 交互式模式
    python main.py interactive
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml
from searcher import (
    search_all,
    save_results,
    load_results,
    SearchResult,
)
from analyzer import (
    keyword_relevance_filter,
    analyze_with_claude,
    generate_manual_prompt,
    AnalyzedReport,
    ReportSection,
    AnalyzedItem,
)
from writer import (
    ReportWriter,
    generate_report_from_analysis,
    quick_report,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("main")

PYTHON = r"C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe"


# ============================================================
# 配置加载
# ============================================================

def load_config(config_path: str) -> dict:
    """加载 YAML 配置"""
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    logger.info(f"Config loaded from {config_path}")
    return config


# ============================================================
# 命令: 检索
# ============================================================

def cmd_search(args):
    """执行多源检索"""
    print("\n" + "=" * 60)
    print("  阶段 1/3: 多源检索")
    print("=" * 60 + "\n")

    # 从配置文件或命令行获取参数
    if args.config:
        config = load_config(args.config)
        search_cfg = config.get("search", {})
        topic = config.get("topic", args.topic or "")
        topic_en = config.get("topic_en", args.topic_en or "")
        queries = args.queries or search_cfg.get("journal_keywords", [])
        sources = args.sources or search_cfg.get("sources", ["semanticscholar", "arxiv"])
        patent_queries = args.patent_queries or search_cfg.get("patent_keywords", [])
        max_per = args.max_results or search_cfg.get("max_results_per_source", 15)
        year_from = search_cfg.get("year_from")
        year_to = search_cfg.get("year_to")
    else:
        queries = args.queries or [args.topic]
        sources = args.sources or ["semanticscholar", "arxiv", "crossref"]
        patent_queries = args.patent_queries or []
        max_per = args.max_results or 15
        year_from = None
        year_to = None
        topic = args.topic or ""
        topic_en = args.topic_en or ""

    if not queries and not patent_queries:
        logger.error("No search queries provided. Use --queries or --config.")
        return None

    print(f"主题: {topic}")
    print(f"期刊检索关键词: {queries}")
    print(f"专利检索关键词: {patent_queries}")
    print(f"检索源: {sources}")
    print(f"每源最多: {max_per} 条\n")

    results = search_all(
        queries=queries,
        sources=sources,
        max_per_source=max_per,
        year_from=year_from,
        year_to=year_to,
        patent_queries=patent_queries,
    )

    output = args.output or "search_results.json"
    save_results(results, output)
    print(f"\n✓ 检索完成: {len(results)} 条结果 → {output}")

    return results


# ============================================================
# 命令: 分析
# ============================================================

def cmd_analyze(args):
    """执行分析筛选"""
    print("\n" + "=" * 60)
    print("  阶段 2/3: 分析与筛选")
    print("=" * 60 + "\n")

    # 加载检索结果
    input_file = args.input or "search_results.json"
    if not os.path.exists(input_file):
        logger.error(f"Input file not found: {input_file}")
        return None

    with open(input_file, "r", encoding="utf-8") as f:
        items = json.load(f)
    print(f"加载检索结果: {len(items)} 条\n")

    # 获取主题
    if args.config:
        config = load_config(args.config)
        topic = config.get("topic", args.topic or "")
        topic_en = config.get("topic_en", args.topic_en or "")
    else:
        topic = args.topic or ""
        topic_en = args.topic_en or ""

    if not topic:
        logger.error("Topic required. Use --topic or --config.")
        return None

    # 关键词初筛
    print("→ 执行关键词初筛...")
    filtered = keyword_relevance_filter(items, topic)
    filtered = [i for i in filtered if i.get("_keyword_score", 0) >= 50]
    print(f"  初筛后保留: {len(filtered)} 条\n")

    # LLM 分析
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if args.config:
        config = load_config(args.config)
        api_key = api_key or config.get("claude_api", {}).get("api_key", "")
        model = config.get("claude_api", {}).get("model", "claude-sonnet-4-6")
    else:
        model = "claude-sonnet-4-6"

    if api_key:
        print("→ 使用 Claude API 进行深度分析...")
        report = analyze_with_claude(filtered, topic, topic_en, api_key, model)
        if report:
            output = args.output or "analysis_result.json"
            _save_analysis(report, output)
            return report

    # 手动模式
    print("\n⚠ 未配置 Claude API Key，使用手动分析模式\n")
    print("→ 生成分析提示词...")
    prompt = generate_manual_prompt(filtered, topic, topic_en, "manual_analysis_prompt.md")
    print("✓ 提示词已保存到: manual_analysis_prompt.md")
    print("\n请将上述文件内容粘贴到 Claude 中进行处理，然后将结果保存为 analysis_result.json")
    print("分析完成后运行: python main.py write --input analysis_result.json\n")

    return None


def _save_analysis(report: AnalyzedReport, filepath: str):
    """保存分析结果"""
    data = {
        "topic": report.topic,
        "topic_en": report.topic_en,
        "sections": [
            {
                "title": s.title,
                "content": s.content,
                "subsections": [{"title": sub.title, "content": sub.content} for sub in s.subsections],
                "referenced_ids": s.referenced_ids,
            }
            for s in report.sections
        ],
        "item_scores": [item.to_dict() for item in report.item_scores],
        "comparison_data": report.comparison_data,
        "image_suggestions": report.image_suggestions,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"Analysis saved to {filepath}")


def _load_analysis(filepath: str) -> AnalyzedReport:
    """加载分析结果"""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    report = AnalyzedReport(
        topic=data.get("topic", ""),
        topic_en=data.get("topic_en", ""),
        image_suggestions=data.get("image_suggestions", []),
        comparison_data=data.get("comparison_data", {}),
    )

    for s_data in data.get("sections", []):
        section = ReportSection(
            title=s_data.get("title", ""),
            content=s_data.get("content", ""),
            referenced_ids=s_data.get("referenced_ids", []),
        )
        for sub_data in s_data.get("subsections", []):
            sub = ReportSection(
                title=sub_data.get("title", ""),
                content=sub_data.get("content", ""),
            )
            section.subsections.append(sub)
        report.sections.append(section)

    for item_data in data.get("item_scores", []):
        item = AnalyzedItem(**{k: v for k, v in item_data.items() if k in AnalyzedItem.__dataclass_fields__})
        report.item_scores.append(item)

    return report


# ============================================================
# 命令: 生成文档
# ============================================================

def cmd_write(args):
    """生成 Word 文档"""
    print("\n" + "=" * 60)
    print("  阶段 3/3: 生成 Word 文档")
    print("=" * 60 + "\n")

    # 加载配置
    config = {}
    if args.config:
        config = load_config(args.config)

    fmt_cfg = config.get("formatting", {})

    # 加载分析结果
    if args.input and os.path.exists(args.input):
        report = _load_analysis(args.input)
        print(f"加载分析结果: {args.input}")
    else:
        logger.error("No analysis input. Run 'analyze' first or provide --input.")
        return None

    # 确定输出路径
    output_dir = args.output_dir or config.get("output_dir", "../output")
    filename = config.get("output_filename", "调研报告")
    output = args.output or os.path.join(output_dir, f"{filename}.docx")

    # 确保输出目录
    Path(output).parent.mkdir(parents=True, exist_ok=True)

    # 日期
    date = datetime.now().strftime("%Y年%m月")
    topic_en = config.get("topic_en", report.topic_en)
    subtitle = config.get("subtitle", "")

    # 生成文档
    print(f"→ 生成文档: {output}")
    path = generate_report_from_analysis(
        report_data=report,
        output_path=output,
        styles=fmt_cfg if fmt_cfg else None,
        topic_en=topic_en,
        topic_subtitle=subtitle,
        date=date,
        comparison_data=report.comparison_data if report.comparison_data else None,
    )

    # 添加图片占位符建议
    if report.image_suggestions:
        writer = ReportWriter(fmt_cfg)
        for suggestion in report.image_suggestions:
            writer.add_image_placeholder(suggestion)
        writer.save(path)  # 重新保存 (追加了占位符)

    print(f"\n✓ 文档生成完成: {path}")
    print(f"  文件大小: {os.path.getsize(path):,} bytes")
    return path


# ============================================================
# 命令: 完整流水线
# ============================================================

def cmd_full(args):
    """执行完整流程: 检索 → 分析 → 生成文档"""
    print("\n" + "█" * 60)
    print("  科技调研报告自动生成工具")
    print("  调研 → 分析 → 报告")
    print("█" * 60 + "\n")

    config = load_config(args.config) if args.config else {}
    topic = config.get("topic", "")
    topic_en = config.get("topic_en", "")

    # 阶段 1: 检索
    search_output = os.path.join("output", "search_results.json")
    results = cmd_search(args)
    if not results:
        logger.error("检索阶段失败")
        return

    # 阶段 2: 分析
    api_key = os.environ.get("ANTHROPIC_API_KEY") or config.get("claude_api", {}).get("api_key", "")
    if api_key:
        analyze_args = argparse.Namespace(
            config=args.config,
            input=search_output,
            output=os.path.join("output", "analysis_result.json"),
            topic=topic,
            topic_en=topic_en,
        )
        cmd_analyze(analyze_args)

    # 阶段 3: 生成文档
    write_args = argparse.Namespace(
        config=args.config,
        input=os.path.join("output", "analysis_result.json"),
        output=args.output,
        output_dir=None,
    )
    cmd_write(write_args)

    print("\n" + "█" * 60)
    print("  全部完成!")
    print("█" * 60 + "\n")


# ============================================================
# 命令: 交互式
# ============================================================

def cmd_interactive(args):
    """交互式引导模式"""
    print("\n" + "█" * 60)
    print("  科技调研报告生成工具 - 交互式模式")
    print("█" * 60 + "\n")

    # 步骤 1: 输入主题
    topic = input("▶ 调研主题 (中文): ").strip()
    if not topic:
        print("主题不能为空")
        return

    topic_en = input("▶ 英文主题 (可选): ").strip()

    # 步骤 2: 输入检索关键词 (逗号分隔)
    print("\n▶ 期刊检索关键词 (逗号分隔):")
    kw_input = input("  (默认: 由主题自动生成): ").strip()
    if kw_input:
        queries = [k.strip() for k in kw_input.split(",")]
    else:
        # 自动组合
        queries = [
            f"{topic_en} technology",
            f"{topic} 研究进展",
            f"{topic_en} fabrication method",
        ]

    print("\n▶ 专利检索关键词 (逗号分隔):")
    patent_input = input("  (默认: 同期刊关键词): ").strip()
    patent_queries = [k.strip() for k in patent_input.split(",")] if patent_input else queries

    # 步骤 3: 选择检索源
    print("\n▶ 期刊检索源 (多选用空格分隔):")
    print("  1. Semantic Scholar (免费)")
    print("  2. arXiv (免费)")
    print("  3. CrossRef (免费)")
    print("  4. 全部")
    source_choice = input("  选择 (1-4, 默认4): ").strip() or "4"
    source_map = {
        "1": ["semanticscholar"],
        "2": ["arxiv"],
        "3": ["crossref"],
        "4": ["semanticscholar", "arxiv", "crossref"],
    }
    sources = source_map.get(source_choice, ["semanticscholar", "arxiv", "crossref"])

    # 步骤 4: 检索
    max_results = int(input("\n▶ 每源最大结果数 (默认15): ").strip() or "15")

    print("\n→ 开始检索...")
    results = search_all(
        queries=queries,
        sources=sources,
        max_per_source=max_results,
        patent_queries=patent_queries,
    )

    search_path = os.path.join("output", "search_results.json")
    save_results(results, search_path)
    print(f"✓ 检索完成: {len(results)} 条结果 → {search_path}")

    # 步骤 5: 分析模式选择
    print("\n▶ 分析模式:")
    print("  1. 生成提示词 (手动粘贴到 Claude 处理)")
    print("  2. 直接调用 Claude API (需配置 API Key)")
    mode = input("  选择 (1-2, 默认1): ").strip() or "1"

    items = [r if isinstance(r, dict) else r.to_dict() for r in results]
    filtered = keyword_relevance_filter(items, topic)
    filtered = [i for i in filtered if i.get("_keyword_score", 0) >= 50]
    print(f"  初筛后保留: {len(filtered)} 条")

    if mode == "1":
        generate_manual_prompt(filtered, topic, topic_en, "manual_analysis_prompt.md")
        print("✓ 提示词已保存到: manual_analysis_prompt.md")
        print("\n请将内容粘贴到 Claude 处理，完成后:")
        print("  1. 将结果保存为 output/analysis_result.json")
        print("  2. 运行: python main.py write --input output/analysis_result.json")
    else:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            api_key = input("  请输入 Anthropic API Key: ").strip()
        if api_key:
            report = analyze_with_claude(filtered, topic, topic_en, api_key)
            if report:
                analysis_path = os.path.join("output", "analysis_result.json")
                _save_analysis(report, analysis_path)
                print(f"✓ 分析完成 → {analysis_path}")

                # 直接生成文档
                gen = input("\n▶ 是否立即生成 Word 文档? (y/n, 默认y): ").strip().lower() or "y"
                if gen == "y":
                    output_path = os.path.join("output", f"{topic}调研报告.docx")
                    generate_report_from_analysis(
                        report_data=report,
                        output_path=output_path,
                        topic_en=topic_en,
                        date=datetime.now().strftime("%Y年%m月"),
                    )
                    print(f"\n✓ 文档已生成: {output_path}")


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="科技调研报告自动生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py full --config config.yaml
  python main.py search --topic "超导接头" --queries "REBCO joint" "HTS soldering"
  python main.py write --input analysis.json --output report.docx
  python main.py interactive
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # full - 完整流水线
    full_parser = subparsers.add_parser("full", help="执行完整流水线")
    full_parser.add_argument("--config", "-c", help="YAML 配置文件路径")
    full_parser.add_argument("--output", "-o", help="输出文件路径")

    # search - 仅检索
    search_parser = subparsers.add_parser("search", help="多源专利/期刊检索")
    search_parser.add_argument("--config", "-c", help="YAML 配置文件路径")
    search_parser.add_argument("--topic", "-t", help="调研主题")
    search_parser.add_argument("--topic-en", help="英文主题")
    search_parser.add_argument("--queries", "-q", nargs="*", help="期刊检索关键词")
    search_parser.add_argument("--patent-queries", "-p", nargs="*", help="专利检索关键词")
    search_parser.add_argument("--sources", "-s", nargs="*", help="期刊检索源")
    search_parser.add_argument("--max-results", "-m", type=int, help="每源最大结果数")
    search_parser.add_argument("--output", "-o", help="输出 JSON 路径")

    # analyze - 仅分析
    analyze_parser = subparsers.add_parser("analyze", help="分析筛选检索结果")
    analyze_parser.add_argument("--config", "-c", help="YAML 配置文件路径")
    analyze_parser.add_argument("--input", "-i", help="检索结果 JSON", default="search_results.json")
    analyze_parser.add_argument("--topic", "-t", help="调研主题")
    analyze_parser.add_argument("--topic-en", help="英文主题")
    analyze_parser.add_argument("--output", "-o", help="分析结果输出 JSON")

    # write - 仅生成文档
    write_parser = subparsers.add_parser("write", help="生成 Word 文档")
    write_parser.add_argument("--config", "-c", help="YAML 配置文件路径")
    write_parser.add_argument("--input", "-i", help="分析结果 JSON")
    write_parser.add_argument("--output", "-o", help="输出 docx 路径")
    write_parser.add_argument("--output-dir", help="输出目录")

    # interactive - 交互式
    inter_parser = subparsers.add_parser("interactive", help="交互式引导模式")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    command_map = {
        "full": cmd_full,
        "search": cmd_search,
        "analyze": cmd_analyze,
        "write": cmd_write,
        "interactive": cmd_interactive,
    }

    func = command_map.get(args.command)
    if func:
        func(args)


if __name__ == "__main__":
    main()
