"""
分析筛选模块 - LLM 驱动的相关性评估与报告内容生成

支持两种模式:
1. API 模式: 直接调用 Claude API 进行分析
2. 手动模式: 输出结构化提示词，用户手动处理
"""

import json
import logging
import os
import re
from dataclasses import dataclass, field, asdict
from typing import Optional

logger = logging.getLogger(__name__)

# ============================================================
# 数据模型
# ============================================================

@dataclass
class AnalyzedItem:
    """分析后的单条结果"""
    result_id: str
    title: str
    title_cn: str = ""                     # 中文译名
    relevance_score: float = 0.0           # 相关性 0-100
    relevance_reason: str = ""             # 相关性判定理由
    key_findings: str = ""                 # 核心发现 (中文摘要)
    technical_highlights: list[str] = field(default_factory=list)  # 技术亮点
    category: str = ""                     # 分类: 专利/论文/综述/标准
    section_assign: str = ""               # 应归入报告的哪个章节
    novel_score: float = 0.0               # 新颖性 0-100
    credibility_score: float = 0.0         # 可信度 0-100
    raw_item: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ReportSection:
    """报告章节"""
    title: str                             # 章节标题
    content: str = ""                      # 章节正文 (Markdown)
    subsections: list["ReportSection"] = field(default_factory=list)
    referenced_ids: list[str] = field(default_factory=list)  # 引用的结果ID


@dataclass
class AnalyzedReport:
    """分析完成的完整报告结构"""
    topic: str
    topic_en: str
    sections: list[ReportSection] = field(default_factory=list)
    item_scores: list[AnalyzedItem] = field(default_factory=list)
    comparison_data: dict = field(default_factory=dict)  # 对比表数据
    image_suggestions: list[str] = field(default_factory=list)  # 建议插图说明


# ============================================================
# 相关性过滤
# ============================================================

def keyword_relevance_filter(
    items: list[dict],
    primary_topic: str,
    required_keywords: list[str] = None,
    exclude_keywords: list[str] = None,
) -> list[dict]:
    """
    基于关键词的初步相关性过滤 (无 LLM 依赖)

    Args:
        items: 原始检索结果 (dict 列表)
        primary_topic: 主主题
        required_keywords: 必须包含的关键词
        exclude_keywords: 排除关键词

    Returns:
        通过过滤的结果列表
    """
    topic_terms = set(primary_topic.lower().split())
    if required_keywords:
        required = [k.lower() for k in required_keywords]
    else:
        required = []
    if exclude_keywords:
        exclude = [k.lower() for k in exclude_keywords]
    else:
        exclude = []

    filtered = []
    for item in items:
        text = f"{item.get('title', '')} {item.get('abstract', '')}".lower()

        # 主题词匹配
        topic_match = sum(1 for t in topic_terms if t in text)
        if topic_match < 1 and required_keywords:
            continue

        # 必须关键词
        req_ok = all(r in text for r in required) if required else True

        # 排除关键词
        exc_ok = not any(e in text for e in exclude)

        if req_ok and exc_ok:
            score = min(100, topic_match * 15 + 40)
            item["_keyword_score"] = score
            filtered.append(item)

    # 按分数排序
    filtered.sort(key=lambda x: x.get("_keyword_score", 0), reverse=True)
    logger.info(f"Keyword filter: {len(filtered)}/{len(items)} items passed")
    return filtered


# ============================================================
# LLM 分析 (Claude API)
# ============================================================

def _get_claude_client(api_key: str = None):
    """获取 Claude API 客户端"""
    try:
        from anthropic import Anthropic
    except ImportError:
        logger.error("anthropic package not installed. Run: pip install anthropic")
        return None

    key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        logger.warning("No Claude API key found. Will use manual mode.")
        return None

    return Anthropic(api_key=key)


def analyze_with_claude(
    items: list[dict],
    topic: str,
    topic_en: str,
    api_key: str = None,
    model: str = "claude-sonnet-4-6",
) -> Optional[AnalyzedReport]:
    """
    使用 Claude API 深度分析检索结果

    Args:
        items: 检索结果列表
        topic: 中文主题
        topic_en: 英文主题
        api_key: Claude API key
        model: 模型名称

    Returns:
        AnalyzedReport 或 None (API不可用时)
    """
    client = _get_claude_client(api_key)
    if not client:
        return None

    # 构建输入
    items_text = _format_items_for_prompt(items)

    system_prompt = f"""你是一位资深科技调研分析师，专注于超导材料与工程领域。请对以下检索结果进行深度分析,生成一份结构化调研报告。

## 调研主题
中文: {topic}
英文: {topic_en}

## 分析要求
1. 对每条结果进行相关性打分 (0-100) 并说明理由
2. 提取核心技术发现和亮点
3. 将内容归类到以下章节:
   - 摘要: 整体概述
   - 技术背景与实例: 技术原理、发展历程、实际应用案例
   - 专利分析: 专利布局、关键技术路径、主要申请人和机构
   - 技术对比分析: 不同技术方案的优劣势对比
   - 图文技术介绍: 工艺流程、关键技术细节
   - 结论与展望: 总结与未来趋势

4. 生成技术对比表 (比较不同方法的指标参数)
5. 建议需要插入的图表类型
6. 输出完整的中文报告内容 (Markdown 格式)

IMPORTANT: 回复必须是严格的 JSON 格式，不要包含其他文字。"""

    user_prompt = f"""以下是检索到的 {len(items)} 条结果，请按上述要求进行分析:

{items_text}

请返回如下结构的 JSON:
{{
  "item_scores": [
    {{
      "result_id": "原始ID",
      "title_cn": "中文译名",
      "relevance_score": 85,
      "relevance_reason": "中文理由",
      "key_findings": "核心发现的中文摘要",
      "technical_highlights": ["亮点1", "亮点2"],
      "category": "专利/论文/综述",
      "section_assign": "应归入的章节名",
      "novel_score": 80,
      "credibility_score": 90
    }}
  ],
  "sections": [
    {{
      "title": "章节标题",
      "content": "章节完整正文 (Markdown)",
      "subsections": [{{"title": "子标题", "content": "正文"}}],
      "referenced_ids": ["引用的result_id"]
    }}
  ],
  "comparison_data": {{
    "headers": ["对比维度", "方案A", "方案B"],
    "rows": [["参数1", "值", "值"]]
  }},
  "image_suggestions": ["图表说明1", "图表说明2"]
}}"""

    try:
        response = client.messages.create(
            model=model,
            max_tokens=8192,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        content = response.content[0].text if response.content else ""

        # 提取 JSON
        json_match = re.search(r"\{[\s\S]*\}", content)
        if json_match:
            data = json.loads(json_match.group())
            return _parse_claude_response(data, items)
        else:
            logger.error("Failed to extract JSON from Claude response")
            logger.debug(f"Response: {content[:500]}")
            return None

    except Exception as e:
        logger.error(f"Claude API error: {e}")
        return None


def _format_items_for_prompt(items: list[dict], max_items: int = 30) -> str:
    """将检索结果格式化为提示词文本"""
    lines = []
    for i, item in enumerate(items[:max_items]):
        title = item.get("title", "无标题")
        abstract = item.get("abstract", "")[:400]
        year = item.get("year", "")
        source = item.get("source_name", "")
        url = item.get("source_url", "")
        authors = ", ".join(item.get("authors", [])[:3])
        patent_num = item.get("patent_number", "")

        entry = f"""--- 结果 {i+1} (ID: {item.get('id', i)}) ---
标题: {title}
{'专利号: ' + patent_num if patent_num else ''}
作者: {authors}
年份: {year}
来源: {source}
链接: {url}
摘要: {abstract}
"""
        lines.append(entry)

    return "\n".join(lines)


def _parse_claude_response(data: dict, raw_items: list[dict]) -> AnalyzedReport:
    """解析 Claude 返回的 JSON"""
    report = AnalyzedReport(
        topic=data.get("topic", ""),
        topic_en=data.get("topic_en", ""),
        image_suggestions=data.get("image_suggestions", []),
        comparison_data=data.get("comparison_data", {}),
    )

    # 解析 item_scores
    for score_data in data.get("item_scores", []):
        item = AnalyzedItem(
            result_id=score_data.get("result_id", ""),
            title=score_data.get("title", ""),
            title_cn=score_data.get("title_cn", ""),
            relevance_score=score_data.get("relevance_score", 0),
            relevance_reason=score_data.get("relevance_reason", ""),
            key_findings=score_data.get("key_findings", ""),
            technical_highlights=score_data.get("technical_highlights", []),
            category=score_data.get("category", ""),
            section_assign=score_data.get("section_assign", ""),
            novel_score=score_data.get("novel_score", 0),
            credibility_score=score_data.get("credibility_score", 0),
        )
        report.item_scores.append(item)

    # 解析 sections
    for section_data in data.get("sections", []):
        section = ReportSection(
            title=section_data.get("title", ""),
            content=section_data.get("content", ""),
            referenced_ids=section_data.get("referenced_ids", []),
        )
        for sub_data in section_data.get("subsections", []):
            sub = ReportSection(
                title=sub_data.get("title", ""),
                content=sub_data.get("content", ""),
            )
            section.subsections.append(sub)
        report.sections.append(section)

    return report


# ============================================================
# 手动模式 - 生成提示词
# ============================================================

def generate_manual_prompt(
    items: list[dict],
    topic: str,
    topic_en: str,
    output_path: str = None
) -> str:
    """
    生成结构化提示词，供用户手动粘贴到 Claude 中处理

    Returns:
        完整的提示词文本
    """
    items_text = _format_items_for_prompt(items)

    prompt = f"""# 科技调研报告生成任务

## 调研主题
- 中文: {topic}
- 英文: {topic_en}

## 检索结果 (共 {len(items)} 条)

{items_text}

---

## 请按以下步骤处理:

### 第1步: 相关性筛选
对每条结果打分 (0-100)，筛去低于 60 分的内容。

### 第2步: 提取核心信息
对保留的结果，提取:
- 核心技术发现
- 关键参数和数据
- 与其他方案的对比信息

### 第3步: 撰写报告
按以下结构生成完整中文报告:

#### 一、摘要
(200-300字概括调研主题和主要发现)

#### 二、技术背景与实例
- 技术原理简介 (非必要术语使用中文)
- 发展历程
- 典型应用实例

#### 三、专利分析
- 专利布局概况
- 主要专利权人
- 关键技术路径
- 地域分布

#### 四、技术对比分析
以表格形式对比不同技术方案的关键指标:

| 对比维度 | 方案A | 方案B | 方案C |
|---------|-------|-------|-------|

#### 五、图文技术介绍
- 工艺流程详细说明
- 关键参数和工艺窗口
- 常见问题与解决方案

#### 六、结论与展望
- 当前技术水平总结
- 未来发展趋势
- 推荐关注方向

#### 七、参考文献
列出所有引用的来源

---

请直接输出完整的报告内容 (Markdown 格式)，回复中不要包含本提示词。
"""

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(prompt)
        logger.info(f"Manual prompt saved to {output_path}")

    return prompt


# ============================================================
# 便捷分析函数
# ============================================================

def analyze_results(
    items: list[dict],
    topic: str,
    topic_en: str = "",
    config: dict = None,
) -> AnalyzedReport:
    """
    统一分析入口 - 自动选择 API 模式或手动模式

    Returns:
        AnalyzedReport 对象
    """
    # 先做关键词初筛
    if config:
        required = config.get("filter", {}).get("required_keywords", [])
        exclude = config.get("filter", {}).get("exclude_keywords", [])
        min_score = config.get("filter", {}).get("min_relevance_score", 60)
        items = keyword_relevance_filter(items, topic, required, exclude)
        items = [i for i in items if i.get("_keyword_score", 0) >= min_score]
    else:
        items = keyword_relevance_filter(items, topic)

    # 尝试 API 分析
    if config and config.get("claude_api", {}).get("api_key"):
        api_key = config["claude_api"]["api_key"]
        model = config["claude_api"].get("model", "claude-sonnet-4-6")
    else:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        model = "claude-sonnet-4-6"

    if api_key:
        report = analyze_with_claude(items, topic, topic_en, api_key, model)
        if report:
            return report

    # 降级为手动模式
    logger.info("Falling back to manual mode - generating prompt file")
    prompt_path = "manual_analysis_prompt.md"
    generate_manual_prompt(items, topic, topic_en, prompt_path)
    logger.info(f"Manual prompt written to {prompt_path}, paste into Claude for processing")

    return AnalyzedReport(topic=topic, topic_en=topic_en)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    # 测试: 加载搜索结果并分析
    test_items = [
        {
            "id": "test1",
            "title": "Fabrication of Flux-Free REBCO CC Joints by Hybridizing Ultrasonic Welding and Soldering",
            "abstract": "This paper presents a novel flux-free joint fabrication method for REBCO coated conductors...",
            "year": 2024,
            "source_name": "IEEE TAS",
            "authors": ["J. Kim", "S. Lee"],
            "source_url": "https://example.com/paper1",
        },
        {
            "id": "test2",
            "title": "A Novel Low-Resistance Solder-Free Copper Bonding Joint Using Warm Pressure Welding Method",
            "abstract": "We demonstrate a solder-free copper diffusion bonding technique achieving joint resistance of 16.8 nΩ·cm²...",
            "year": 2024,
            "source_name": "Supercond. Sci. Technol.",
            "authors": ["A. Smith", "B. Jones"],
            "source_url": "https://example.com/paper2",
        },
    ]

    prompt = generate_manual_prompt(test_items, "超导带材接头技术", "Superconducting Tape Joint Technology")
    print(prompt[:1500])
    print("\n... (prompt saved to file)")
