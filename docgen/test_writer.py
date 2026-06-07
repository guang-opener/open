"""测试 writer 模块"""
import sys
sys.path.insert(0, ".")

from writer import quick_report

sections = {
    "一、摘要": (
        "本文系统调研了REBCO高温超导带材接头技术的最新进展。"
        "通过对Semantic Scholar、arXiv、CrossRef和Google Patents的多源检索，"
        "共筛选出高度相关专利和论文30余篇。报告重点分析了钎焊连接、超声辅助焊接"
        "和铜扩散连接三种主流工艺路线的技术特点与发展趋势。"
    ),
    "二、技术背景与实例": (
        "超导材料因其零电阻和完全抗磁性，在MRI、高能物理加速器、磁约束核聚变"
        "等领域具有广泛前景。REBCO涂层导体作为第二代高温超导带材的典型代表，"
        "凭借高临界电流密度和优异机械性能，已成为超导电力装置的核心材料。\n\n"
        "在实际应用中，单根带材长度约数百米，大型设备需数十公里导体。"
        "因此，高性能接头是超导技术工程化的关键环节。\n\n"
        "典型案例:\n"
        "- 上海超导电缆示范项目: 采用In-Sn焊料钎焊工艺，接头电阻控制在50 nO·cm2以内\n"
        "- SPARC聚变装置: MIT团队采用铜扩散连接技术实现超低电阻接头\n"
        "- 日本SCMaglev: 超导磁悬浮列车磁体采用精密焊接接头技术"
    ),
    "三、专利分析": (
        "共检索到相关专利15件，主要专利权人分布:\n\n"
        "- SuperPower (美国): 3件 - 聚焦钎焊工艺优化\n"
        "- 藤仓株式会社 (日本): 3件 - 超声辅助焊接方向\n"
        "- 上海超导 (中国): 3件 - 铜扩散连接技术\n"
        "- SuNAM (韩国): 2件 - 带材接头可靠性\n"
        "- 其他: 4件\n\n"
        "技术路径分析: 无纤剂化、低温连接和高可靠性是专利布局的三大方向。"
        "2023-2025年申请占比超过70%，表明该领域正处于技术密集爆发期。"
    ),
    "四、结论与展望": (
        "当前技术水平: 铜扩散连接接头电阻最低(约16.8 nO·cm2)，"
        "超声辅助焊接在免纤剂和高可靠性方面领先，传统钎焊仍是工程首选。\n\n"
        "发展趋势:\n"
        "- 2026-2028年: 铜扩散连接有望实现工程化验证\n"
        "- 超声辅助焊接设备价格预计下降30-50%\n"
        "- 机器视觉辅助自动化焊接将成为标配\n"
        "- 室温超导材料若突破将彻底改变接头技术格局"
    ),
}

quick_report(
    topic="REBCO高温超导带材接头技术调研报告",
    topic_en="A Survey of REBCO Coated Conductor Joint Technologies",
    subtitle="—— 钎焊、超声焊接与铜扩散连接综合评述 ——",
    sections=sections,
    output_path="../output/test_report.docx",
    tables=[
        {
            "headers": ["对比维度", "钎焊 (搭接焊)", "超声辅助焊", "铜扩散连接"],
            "rows": [
                ["操作难度", "低", "中低", "中高"],
                ["设备成本", "低", "中", "高"],
                ["接头电阻 (nO·cm2)", "20-50", "17-30", "~17"],
                ["是否需要焊料", "是", "是", "否"],
                ["是否需要助焊剂", "通常需要", "不需要", "不需要"],
                ["焊接温度 (C)", "130-200", "常温-150", "150-180"],
                ["工程成熟度", "高 (工业标准)", "中高 (快速发展)", "中 (前沿研究)"],
                ["推荐应用场景", "通用、首选方案", "高可靠性要求", "追求最低电阻"],
            ],
            "caption": "表1: REBCO带材接头技术综合对比",
        }
    ],
    references=[
        'J. Kim et al., "Flux-Free REBCO CC Joints by Ultrasonic Welding and Soldering", IEEE TAS, 2024.',
        'A. Smith et al., "Low-Resistance Solder-Free Copper Bonding Joint for REBCO CC", Supercond. Sci. Technol., 2024.',
        'Y. Zhang et al., "Superconducting Joint Technology for 2G-HTS Tapes", Physica C, 2023.',
        'SuperPower Inc., "Method for Soldering REBCO Coated Conductors", US Patent, 2024.',
        '藤仓株式会社, "超电导線材の接続方法", 特開2024, 2024.',
        '上海超导科技股份有限公司, "一种REBCO带材铜扩散连接方法", CN Patent, 2024.',
    ],
)

print("测试报告生成完毕: ../output/test_report.docx")
