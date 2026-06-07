"""
重建报告 - 第5章节图文混排版本
在"五、图文技术介绍"中嵌入技术配图，实现图文并茂
"""
import sys, os, json
sys.path.insert(0, ".")

from writer import ReportWriter
from analyzer import AnalyzedReport, ReportSection, AnalyzedItem
from datetime import datetime

FIG_DIR = "../output/figures"

# ============================================================
# 加载分析数据
# ============================================================
with open("../output/analysis_result.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# ============================================================
# 创建 Writer
# ============================================================
writer = ReportWriter()

# ============================================================
# 标题页
# ============================================================
writer.add_title_page(
    title=data["topic"],
    subtitle_en=data.get("topic_en", ""),
    subtitle_cn="—— 钎焊、超声焊接与铜扩散连接综合评述 ——",
    date=datetime.now().strftime("%Y年%m月"),
)

# ============================================================
# 章节渲染 (section 5 用自定义图文混排)
# ============================================================
SECTION_5_TITLE = "五、图文技术介绍"

for sec in data["sections"]:
    if sec["title"] == SECTION_5_TITLE:
        # ==========================================
        # 第5章: 图文混排 — 图片嵌入 + 文字叙述
        # ==========================================
        writer.add_heading1(sec["title"])

        # 5.1 带材结构 → 图1
        writer.add_heading2("5.1 REBCO涂层导体多层结构")
        writer.add_image(
            os.path.join(FIG_DIR, "fig1_rebco_structure.png"),
            width_cm=13.5,
            caption="图1: REBCO涂层导体多层结构示意图 — 从上至下依次为铜稳定层、银保护层、REBCO超导层、氧化物缓冲层和哈氏合金基底，总厚度约0.1 mm。超导电流沿超导层（蓝色层）传输。"
        )
        writer.add_body(
            "REBCO涂层导体采用多层薄膜结构，在高强度哈氏合金基底上通过离子束辅助沉积（IBAD）"
            "或轧制辅助双轴织构（RABiTS）工艺生长氧化物缓冲层，再通过金属有机物化学气相沉积（MOCVD）"
            "或脉冲激光沉积（PLD）制备REBCO超导层，最后沉积银保护层和电镀铜稳定层。"
        )
        writer.add_body(
            "铜稳定层（厚度约20-40 μm）不仅提供电气稳定和热稳定功能，"
            "在最新的铜扩散连接技术中，铜稳定层还直接作为键合介质，"
            "通过固态扩散实现无焊料连接。银保护层（约2 μm）位于超导层与铜之间，"
            "提供电流转移通道并防止铜与超导层发生有害反应。"
            "在实际接头制备中，通常需要将接头区域的铜层和银层部分去除或处理，"
            "以露出超导层或实现铜-铜直接接触。"
        )

        # 5.2 接头结构 → 图2
        writer.add_heading2("5.2 四种主流接头结构对比")
        writer.add_image(
            os.path.join(FIG_DIR, "fig2_joint_types.png"),
            width_cm=14.5,
            caption="图2: 四种主流接头结构对比 — (左上)搭接钎焊, (右上)超声辅助无纤剂焊, (左下)铜扩散连接, (右下)超导接头。中间连接层分别标注了焊料类型、工艺参数和关键特征。"
        )
        writer.add_body(
            "上图直观对比了四种接头结构的差异。搭接钎焊和超声辅助焊中间存在焊料层，"
            "区别在于是否使用化学助焊剂；铜扩散连接实现了无中间介质的直接铜-铜键合；"
            "超导接头通过高温烧结使接头区域本身恢复超导性。"
        )
        writer.add_body(
            "结构设计的关键考量为：超导层应采用面对面（Face-to-Face）配置"
            "以最大化超导电流传输距离，搭接长度5-20 cm，"
            "连接层（焊料或扩散层）厚度控制在50-200 μm范围内。"
        )

        # 5.3 工艺流程 → 图3
        writer.add_heading2("5.3 钎焊搭接详细工艺流程")
        writer.add_image(
            os.path.join(FIG_DIR, "fig3_soldering_process.png"),
            width_cm=15.0,
            caption="图3: 低熔点焊料钎焊（搭接焊）五步工艺流程图 — 从表面预处理到最终冷却检测的完整工序链。底部标注了各项关键参数的推荐范围。"
        )
        writer.add_body(
            "钎焊搭接工艺是当前工程应用最广泛的方法，其五步流程涵盖了从带材准备到质量检测的完整工序。"
            "其中表面预处理质量是最关键的变量——打磨后表面粗糙度Ra应控制在1-5 μm，"
            "打磨后30分钟内必须完成焊接，避免洁净表面再次氧化。"
        )
        writer.add_body(
            "步骤四的加压加热焊接是整个工艺的核心：温度高于焊料熔点10-30°C即可保证润湿，"
            "但绝不可超过200°C以免超导层退化；压力0.5-5 MPa需均匀施加于整个搭接区域；"
            "保温时间1-5分钟需根据搭接长度和焊料类型优化。"
            "步骤五的自然冷却同样关键——强制急冷会引入热应力裂纹，影响接头长期可靠性。"
        )

        # 5.4 电阻对比 → 图4
        writer.add_heading2("5.4 接头电阻性能对比")
        writer.add_image(
            os.path.join(FIG_DIR, "fig4_resistance_comparison.png"),
            width_cm=12.0,
            caption="图4: 四种接头方法的特征电阻对比（对数坐标）。虚线标注了电力传输应用和持久模式应用对电阻的不同要求。超导接头的电阻低于10⁻⁵ nΩ·cm²，满足持久电流运行要求。"
        )
        writer.add_body(
            "从上图可以清晰看出：传统钎焊接头的特征电阻在20-50 nΩ·cm²范围内，"
            "超声辅助焊接可将电阻降至17-30 nΩ·cm²，铜扩散连接进一步降至约17 nΩ·cm²，"
            "而超导接头（持久电流级）可将电阻做到10⁻⁵ nΩ·cm²量级以下。"
        )
        writer.add_body(
            "对于一般电力传输应用（如超导电缆），nΩ·cm²量级的电阻即可接受；"
            "但对于持久模式运行的磁体（如NMR、MRI），需要低于10⁻³ nΩ·cm²的极限低电阻，"
            "目前仅有超导接头技术能满足这一要求。"
            "值得关注的是，铜扩散连接在2024-2025年的突破使其电阻比传统焊料接头低了约三分之一，"
            "且无需焊料的设计避免了焊料层电阻对整体性能的贡献。"
        )

        # 5.5 工艺窗口 → 图5
        writer.add_heading2("5.5 铜扩散连接工艺窗口")
        writer.add_image(
            os.path.join(FIG_DIR, "fig5_process_window.png"),
            width_cm=12.0,
            caption="图5: 铜扩散连接（温压焊）工艺窗口。绿色椭圆为最优工艺区域（150-180°C, 250-333 MPa），黄色为边缘区域。红色标注了2025年新发展的超快铜键合方法的工艺点（100°C, 354 MPa, 仅需3分钟）。"
        )
        writer.add_body(
            "铜扩散连接的工艺窗口相对较窄，需要在温度、压力和时间三个维度上精确匹配。"
            "图5中绿色区域代表能实现低电阻（<20 nΩ·cm²）成功键合的工艺条件。"
            "温度过低（<130°C）时铜原子扩散速率不足，键合不充分；"
            "温度过高（>200°C）则面临超导层氧扩散退化的风险。"
            "压力过低（<200 MPa）导致铜层塑性变形不足，界面接触面积受限；"
            "压力过高（>350 MPa）可能损伤脆性的陶瓷超导层。"
        )
        writer.add_body(
            "2025年发展的超快铜键合方法（图中蓝色星标）在更低的温度（100°C）和更高的压力（354 MPa）"
            "条件下仅需3分钟即可完成键合，大幅缩短了传统方法的15分钟焊接时间，"
            "为工程化应用提供了更具吸引力的工艺窗口。"
        )

        # 5.6 氧扩散退化 → 图6
        writer.add_heading2("5.6 焊接热效应与超导层退化机理")
        writer.add_image(
            os.path.join(FIG_DIR, "fig6_oxygen_diffusion.png"),
            width_cm=12.0,
            caption="图6: REBCO带材在不同加热温度下的临界电流保持率曲线。150°C以下为安全工作区，150-200°C为注意区，200°C以上进入危险区。250°C发生不可逆退化，300°C以上临界电流急剧下降。"
        )
        writer.add_body(
            "上述退化曲线为接头工艺的温度上限设计提供了关键科学依据。"
            "REBCO超导层（REBa₂Cu₃O₇₋δ）中的氧含量对超导电性至关重要——"
            "氧空位浓度（δ值）直接影响临界温度Tc和临界电流密度Jc。"
            "加热过程中，超导层中的氧向周围层（银层、铜层）扩散逸出，"
            "导致局部氧空位浓度升高，超导性能随之退化。"
        )
        writer.add_body(
            "实验研究表明：150°C以下保温数小时对REBCO性能影响可忽略不计；"
            "200°C保温30分钟后Ic下降约5-10%，但冷却后可部分恢复；"
            "250°C以上退化为不可逆过程，晶格氧大量逸出导致超导相分解；"
            "300°C以上临界电流可在数分钟内降至原始值的50%以下。"
            "因此，所有接头工艺的温度控制均需将带材本体温度限制在200°C以下，"
            "并尽量缩短高温持续时间。这也是In-Sn共晶焊料（熔点118°C）广受欢迎的原因之一——"
            "其焊接温度窗口（130-150°C）完美避开了氧扩散退化的起始温度。"
        )

        # 5.7 技术路线图 → 图7
        writer.add_heading2("5.7 技术发展路线图 (2020-2030)")
        writer.add_image(
            os.path.join(FIG_DIR, "fig7_technology_roadmap.png"),
            width_cm=14.0,
            caption="图7: REBCO带材接头技术成熟度（TRL）发展路线图。钎焊技术已进入商业化阶段（TRL 9），超声辅助焊和铜扩散连接预计在2027-2029年达到商业化水平。超导接头（持久电流）仍处于实验室阶段。"
        )
        writer.add_body(
            "从上图的技术路线图可以清晰看出各工艺的成熟度差距和发展趋势："
            "传统钎焊技术（棕色线）早在2020年已达TRL 8-9，技术高度成熟，是当前工程实践的绝对主力；"
            "超声辅助焊接（蓝色线）在2024-2025年进入示范验证阶段（TRL 7-8），"
            "预计2027年前后实现商业化；"
            "铜扩散连接（深蓝虚线）在2024年取得关键突破后快速攀升，"
            "从TRL 3跃升至TRL 6-7，预计2028-2029年实现工程化；"
            "2025年新发展的超快铜键合方法（浅蓝点线）起点更高，"
            "有望在2028年达到TRL 8；"
            "超导接头（红色点划线）受制于工艺复杂度，"
            "预计在2030年前仍将停留在实验室阶段（TRL 5以下）。"
        )

        # 5.8 综合评分 → 图8
        writer.add_heading2("5.8 接头技术综合评分")
        writer.add_image(
            os.path.join(FIG_DIR, "fig8_radar_comparison.png"),
            width_cm=11.0,
            caption="图8: 四种接头技术六维综合评分雷达图。维度包括操作便捷性、接头电阻、机械强度、长期可靠性、工艺成熟度和设备成本。各维度1-10分制。"
        )
        writer.add_body(
            "雷达图从六个关键维度直观对比了四种接头技术的综合性能："
            "钎焊在操作便捷性和工艺成熟度方面领先，但长期可靠性受助焊剂残留问题制约；"
            "超声辅助焊在长期可靠性维度得分最高（9分），因为无纤剂设计彻底消除了腐蚀风险；"
            "铜扩散连接在接头电阻维度得分最高（9分），但设备成本和操作便捷性维度明显落后；"
            "超导接头虽然在电阻维度获得满分（10分），但其他五个维度均处于最低水平，"
            "表明其距离工程实用化仍有很长的路。"
        )

        # 5.9 常见问题
        writer.add_heading2("5.9 常见问题与解决方案")
        writer.add_body(
            "基于文献调研和工程实践，以下汇总了REBCO带材接头制备过程中的常见问题及其解决方案："
        )
        problems = [
            ("接头电阻偏高", "表面处理不充分/焊料氧化/搭接长度不足", "优化打磨清洗流程、使用新鲜焊料、适当增加搭接长度至15-20 cm"),
            ("虚焊（焊料未完全润湿）", "温度不足/助焊剂不足/表面有油污", "提高焊接温度5-10°C、增加助焊剂用量、使用丙酮或无水乙醇加强表面清洗"),
            ("焊料层气孔过多", "焊接时气体未排出/助焊剂过量沸腾", "优化压力使多余焊料和气体排出、控制助焊剂用量"),
            ("超导层临界电流退化", "焊接温度超过200°C或时间过长", "降低焊接温度至200°C以下、缩短保温时间、优先选用In-Sn共晶（118°C）低熔点焊料"),
            ("接头机械强度不足", "焊料层过厚或不均匀/压力不足", "优化焊料用量和均匀性（50-200 μm）、适当增大焊接压力至1-5 MPa"),
            ("接头长期运行退化", "助焊剂残留腐蚀/热循环疲劳积累", "彻底清洗残留助焊剂（超声波清洗+无水乙醇）、改用无纤剂超声焊接工艺"),
            ("带材在接头处断裂", "急冷导致热应力集中/压力过大", "自然缓慢冷却至室温、适当降低焊接压力、检查工装平整度"),
        ]
        for problem, cause, solution in problems:
            writer.add_bullet(f"{problem}：{cause} → {solution}")

    else:
        # ==========================================
        # 其他章节: 标准文本渲染
        # ==========================================
        writer.add_heading1(sec["title"])
        if sec.get("content"):
            writer.add_body_from_markdown(sec["content"])

        for sub in sec.get("subsections", []):
            writer.add_heading2(sub["title"])
            if sub.get("content"):
                writer.add_body_from_markdown(sub["content"])

# ============================================================
# 技术对比分析 (独立章节，含对比表)
# ============================================================
writer.add_heading1("技术对比分析")
comparison = data.get("comparison_data", {})
if comparison:
    writer.add_body(
        "下表从12个关键维度对四种主流REBCO带材接头技术进行综合对比，"
        "为不同应用场景的技术选择提供参考依据："
    )
    writer.add_table(
        headers=comparison.get("headers", []),
        rows=comparison.get("rows", []),
        caption="表1: REBCO带材接头技术综合对比表",
    )

# ============================================================
# 参考文献
# ============================================================
refs = []
for item_data in data.get("item_scores", []):
    title = item_data.get("title", "")
    raw = item_data.get("raw_item", {}) or {}
    relevance = item_data.get("relevance_score", 0)
    if relevance < 50 or not title:
        continue
    authors = ", ".join(raw.get("authors", [])[:3]) if raw.get("authors") else ""
    year = raw.get("year", "") or ""
    journal = raw.get("source_name", "") or raw.get("journal", "") or ""
    url = raw.get("source_url", "") or ""
    ref_text = f'{authors}. "{title}". {journal}, {year}.'
    if url:
        ref_text += f" {url}"
    refs.append(ref_text)

writer.add_references(refs)

# ============================================================
# 保存
# ============================================================
topic_dir = os.path.join("..", "output", data["topic"])
os.makedirs(topic_dir, exist_ok=True)
output_path = os.path.join(topic_dir, f"{data['topic']}_图文版.docx")
writer.save(output_path)

size_kb = os.path.getsize(output_path) / 1024
print(f"\nDone: {output_path}")
print(f"Size: {size_kb:.1f} KB")

# 统计
img_count = sum(1 for rel in writer.doc.part.rels.values() if "image" in rel.reltype)
para_count = len(writer.doc.paragraphs)
table_count = len(writer.doc.tables)
print(f"Content: {para_count} paragraphs, {table_count} tables, {img_count} images")
