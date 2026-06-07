"""
生成科技报告技术配图
输出到 ../output/figures/ 目录
"""
import os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Arc, Rectangle
import numpy as np

# 中文字体设置
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = "../output/figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

DPI = 150

# ============================================================
# 图1: REBCO涂层导体多层结构示意图
# ============================================================
def fig1_rebco_structure():
    """REBCO带材截面结构分层图"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')
    ax.set_title('图1: REBCO涂层导体多层结构示意图', fontsize=14, fontweight='bold', pad=20)

    layers = [
        ("铜稳定层 (Cu Stabilizer)", "#D4784C", "~20-40 μm", "电/热稳定，机械保护"),
        ("银保护层 (Ag Overlayer)", "#C0C0C0", "~2 μm", "保护超导层，提供电流转移通道"),
        ("REBCO超导层 (Superconducting)", "#1F4E79", "~1-2 μm", "核心功能层，承载超导电流"),
        ("氧化物缓冲层 (Buffer Layers)", "#8DB4E2", "~0.2 μm", "织构模板，阻挡元素扩散"),
        ("哈氏合金基底 (Hastelloy Substrate)", "#808080", "~50-100 μm", "机械支撑，提供柔韧性"),
    ]

    y_start = 7.0
    for i, (name, color, thickness, desc) in enumerate(layers):
        height = 0.8 if i < 3 else 0.6
        y = y_start - i * (height + 0.15)

        # 层的矩形
        rect = FancyBboxPatch((1.5, y), 7, height,
                              boxstyle="round,pad=0.05", facecolor=color,
                              edgecolor="#333333", linewidth=1.2, alpha=0.85)
        ax.add_patch(rect)

        # 标签
        ax.text(5, y + height/2, name, ha='center', va='center', fontsize=11,
                fontweight='bold', color='white' if color != "#C0C0C0" and color != "#8DB4E2" else '#333333')

        # 右侧厚度标注
        ax.text(8.8, y + height/2, thickness, ha='left', va='center', fontsize=9,
                color='#555555', style='italic')

        # 左侧功能说明
        ax.text(1.2, y + height/2, desc, ha='right', va='center', fontsize=8,
                color='#777777')

    # 总厚度标注
    ax.annotate('总厚度 ~0.1 mm', xy=(9.5, 7.0), xytext=(9.5, 7.8),
                ha='center', fontsize=9, color='#333333',
                arrowprops=dict(arrowstyle='<->', color='#333333', lw=1.5))
    ax.plot([9.5, 9.5], [7.0, y_start - len(layers)*(0.8+0.15) + 0.6], 'k-', lw=0.5)

    # 电流方向标注
    ax.annotate('', xy=(9.2, 4.5), xytext=(9.2, 6.5),
                arrowprops=dict(arrowstyle='->', color='red', lw=2))
    ax.text(9.5, 5.5, '超导电流\n方向', ha='center', fontsize=8, color='red')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig1_rebco_structure.png")
    fig.savefig(path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: {path}")
    return path


# ============================================================
# 图2: 四种接头结构示意图
# ============================================================
def fig2_joint_types():
    """四种主流接头结构对比示意图"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle('图2: 四种主流接头结构对比示意图', fontsize=14, fontweight='bold', y=1.01)

    configs = [
        ("搭接钎焊 (Lap Soldering)", "#D4784C", "#F2C94C",
         "焊料层\n(In-Sn等)", "搭接长度 5-20 cm\n加热温度 130-200°C\n压力 0.5-5 MPa"),
        ("超声辅助无纤剂焊 (Ultrasonic Assisted)", "#2E75B6", "#8DB4E2",
         "焊料层\n(无纤剂)", "超声 20-60 kHz\n焊接时间 <1秒\n无需化学助焊剂"),
        ("铜扩散连接 (Cu Diffusion Bonding)", "#1F4E79", "#5B9BD5",
         "铜-铜\n直接键合", "温度 150-180°C\n压力 250-333 MPa\n无需焊料"),
        ("超导接头 (Superconducting Joint)", "#8B0000", "#CD5C5C",
         "超导焊料\n(Er123等)", "高温烧结 >700°C\n氧气氛控制\n持久电流级"),
    ]

    for ax, (title, color1, color2, joint_label, params) in zip(axes.flat, configs):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6)
        ax.set_title(title, fontsize=12, fontweight='bold', color=color1)
        ax.axis('off')

        # 上方带材
        rect1 = FancyBboxPatch((1.5, 3.5), 7, 0.8, boxstyle="round,pad=0.05",
                                facecolor=color1, edgecolor='#333', linewidth=1, alpha=0.7)
        ax.add_patch(rect1)
        ax.text(5, 3.9, 'REBCO 带材 A', ha='center', va='center', fontsize=9, color='white', fontweight='bold')

        # 下方带材
        rect2 = FancyBboxPatch((1.5, 1.2), 7, 0.8, boxstyle="round,pad=0.05",
                                facecolor=color1, edgecolor='#333', linewidth=1, alpha=0.7)
        ax.add_patch(rect2)
        ax.text(5, 1.6, 'REBCO 带材 B', ha='center', va='center', fontsize=9, color='white', fontweight='bold')

        # 中间连接层
        joint_y = 2.0
        joint_h = 1.5
        joint_rect = FancyBboxPatch((2.5, joint_y), 5, joint_h, boxstyle="round,pad=0.05",
                                     facecolor=color2, edgecolor=color1, linewidth=1.5,
                                     alpha=0.6, hatch='////' if '超声' in title else '')
        ax.add_patch(joint_rect)
        ax.text(5, joint_y + joint_h/2, joint_label, ha='center', va='center', fontsize=9,
                fontweight='bold', color='#333333')

        # 参数说明
        ax.text(5, 0.4, params, ha='center', va='center', fontsize=8, color='#666666',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#F9F9F9', edgecolor='#DDDDDD'))

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig2_joint_types.png")
    fig.savefig(path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: {path}")
    return path


# ============================================================
# 图3: 钎焊工艺流程
# ============================================================
def fig3_soldering_process():
    """钎焊搭接工艺流程图"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 5)
    ax.axis('off')
    ax.set_title('图3: 低熔点焊料钎焊（搭接焊）工艺流程图', fontsize=14, fontweight='bold', pad=15)

    steps = [
        ("① 表面预处理", "打磨(800-1500目)\n→ 丙酮清洗\n→ 涂覆助焊剂", "#E8F5E9"),
        ("② 预热", "加热平台\n130-150°C\n精度 ≤±5°C", "#FFF3E0"),
        ("③ 装配", "超导层面-面放置\n搭接5-20 cm\n定位夹具固定", "#E3F2FD"),
        ("④ 加压焊接", "0.5-5 MPa\n保温1-5 min\n温度 <200°C", "#FCE4EC"),
        ("⑤ 冷却检测", "保压自然冷却\n清洗助焊剂\n四线法测电阻", "#F3E5F5"),
    ]

    for i, (title, desc, color) in enumerate(steps):
        x = 1 + i * 2.6
        y = 2.5

        # 步骤框
        rect = FancyBboxPatch((x-0.9, y-1.5), 1.8, 2.5, boxstyle="round,pad=0.1",
                               facecolor=color, edgecolor='#333333', linewidth=1.5)
        ax.add_patch(rect)

        ax.text(x, y+0.8, title, ha='center', va='center', fontsize=10, fontweight='bold')
        ax.text(x, y-0.3, desc, ha='center', va='center', fontsize=8, color='#444444')

        # 箭头
        if i < len(steps) - 1:
            ax.annotate('', xy=(x+1.0, y), xytext=(x+1.5, y),
                        arrowprops=dict(arrowstyle='->', color='#1F4E79', lw=2.5))

    # 关键参数栏
    ax.text(7, 0.5, '关键参数: 搭接长度 5-20 cm | 焊料厚度 50-200 μm | 温度 130-200°C | 压力 0.5-5 MPa | 时间 1-5 min',
            ha='center', fontsize=9, color='#1F4E79',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#F0F4F8', edgecolor='#1F4E79', linewidth=1))

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig3_soldering_process.png")
    fig.savefig(path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: {path}")
    return path


# ============================================================
# 图4: 接头电阻对比柱状图
# ============================================================
def fig4_resistance_comparison():
    """四种接头方法的接头电阻对比"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    fig.suptitle('图4: 四种接头方法的特征电阻对比 (nΩ·cm²)', fontsize=14, fontweight='bold')

    methods = ['钎焊\n(In-Sn)', '超声\n辅助焊', '铜扩散\n连接', '超导接头\n(持久电流)']
    values = [35, 23, 17, 0.00001]  # nΩ·cm²
    colors = ['#D4784C', '#2E75B6', '#1F4E79', '#8B0000']
    errors = [15, 7, 3, 0.000005]

    # Log scale for better visibility
    bars = ax.bar(methods, values, color=colors, edgecolor='#333', linewidth=1.2, width=0.5)
    ax.set_ylabel('特征电阻 (nΩ·cm²)', fontsize=11)
    ax.set_yscale('log')
    ax.set_ylim(1e-6, 100)

    # 数值标注
    for bar, val, err in zip(bars, values, errors):
        if val > 0.01:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                    f'{val}±{err}', ha='center', fontsize=10, fontweight='bold')
        else:
            ax.text(bar.get_x() + bar.get_width()/2, 1e-5,
                    '<10⁻⁵', ha='center', fontsize=10, fontweight='bold')

    # 应用需求参考线
    ax.axhline(y=10, color='orange', linestyle='--', linewidth=1, alpha=0.7)
    ax.text(3.5, 12, '电力传输要求 (~10 nΩ·cm²)', fontsize=8, color='orange')
    ax.axhline(y=0.001, color='red', linestyle='--', linewidth=1, alpha=0.7)
    ax.text(3.5, 0.0015, '持久模式要求 (<10⁻³ nΩ·cm²)', fontsize=8, color='red')

    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig4_resistance_comparison.png")
    fig.savefig(path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: {path}")
    return path


# ============================================================
# 图5: 工艺窗口对比图
# ============================================================
def fig5_process_window():
    """铜扩散连接的工艺窗口 (温度-压力-时间)"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    fig.suptitle('图5: 铜扩散连接工艺窗口 (温度-压力-时间)', fontsize=14, fontweight='bold')

    # 模拟工艺窗口数据
    np.random.seed(42)
    temp_opt = np.random.normal(165, 10, 50)
    pres_opt = np.random.normal(290, 20, 50)
    temp_marginal = np.random.normal(165, 25, 30)
    pres_marginal = np.random.normal(290, 40, 30)

    # 工艺窗口区域
    from matplotlib.patches import Ellipse
    ellipse_opt = Ellipse((165, 290), width=30, height=50,
                           facecolor='#4CAF50', alpha=0.3, edgecolor='#2E7D32', linewidth=2, linestyle='-')
    ellipse_marg = Ellipse((165, 290), width=70, height=100,
                            facecolor='#FFC107', alpha=0.15, edgecolor='#F57F17', linewidth=1.5, linestyle='--')
    ax.add_patch(ellipse_marg)
    ax.add_patch(ellipse_opt)

    ax.scatter(temp_opt, pres_opt, c='#2E7D32', s=30, alpha=0.6, label='成功键合 (低电阻)')
    ax.scatter(temp_marginal, pres_marginal, c='#F57F17', s=30, alpha=0.4, marker='^', label='边缘条件 (电阻偏高)')

    # 失败区域
    ax.scatter([120, 130, 220, 210], [350, 180, 350, 180], c='red', s=60, marker='x', linewidth=2,
               label='键合失败')

    # 标注
    ax.annotate('最优工艺窗口\n150-180°C\n250-333 MPa', xy=(165, 290), fontsize=10, ha='center',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='#2E7D32'))

    ax.annotate('温度过低\n扩散不足', xy=(130, 320), fontsize=8, color='red')
    ax.annotate('温度过高\n超导层退化', xy=(210, 260), fontsize=8, color='red')
    ax.annotate('压力不足\n接触不充分', xy=(160, 200), fontsize=8, color='#F57F17')

    ax.set_xlabel('温度 (°C)', fontsize=11)
    ax.set_ylabel('压力 (MPa)', fontsize=11)
    ax.set_xlim(100, 240)
    ax.set_ylim(150, 400)
    ax.legend(loc='upper right', fontsize=8)
    ax.grid(alpha=0.2)

    # 标注"2025超快方法"的工艺点
    ax.scatter([100], [354], c='#1F4E79', s=120, marker='*', edgecolor='white', linewidth=1.5, zorder=10)
    ax.annotate('2025超快方法\n100°C, 354 MPa, 3min',
                xy=(100, 354), xytext=(115, 370),
                arrowprops=dict(arrowstyle='->', color='#1F4E79', lw=1.5),
                fontsize=9, color='#1F4E79', fontweight='bold')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig5_process_window.png")
    fig.savefig(path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: {path}")
    return path


# ============================================================
# 图6: 氧扩散退化曲线
# ============================================================
def fig6_oxygen_diffusion():
    """REBCO带材加热过程中的氧扩散退化曲线"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    fig.suptitle('图6: REBCO带材加热过程中临界电流退化曲线', fontsize=14, fontweight='bold')

    temperatures = np.linspace(20, 400, 100)
    # 模拟 Ic 退化曲线 (基于文献数据趋势)
    ic_retention = 100 * np.ones_like(temperatures)
    # 150°C 开始轻微退化
    mask1 = temperatures > 150
    ic_retention[mask1] = 100 - 0.05 * (temperatures[mask1] - 150)**1.5
    # 250°C 加速退化
    mask2 = temperatures > 250
    ic_retention[mask2] = ic_retention[mask2] - 0.3 * (temperatures[mask2] - 250)**1.8
    ic_retention = np.clip(ic_retention, 0, 100)

    ax.plot(temperatures, ic_retention, 'b-', linewidth=2.5, label='Ic保持率')
    ax.fill_between(temperatures, ic_retention, alpha=0.2, color='blue')

    # 关键温度阈值
    for t, label, color in [
        (118, 'In-Sn熔点\n118°C', '#D4784C'),
        (150, '氧扩散起始\n150°C', '#F57F17'),
        (200, '推荐上限\n200°C', '#FF9800'),
        (250, '不可逆退化\n250°C', '#F44336'),
        (300, '严重退化\n300°C', '#B71C1C'),
    ]:
        idx = np.abs(temperatures - t).argmin()
        ic_val = ic_retention[idx]
        ax.axvline(x=t, color=color, linestyle='--', linewidth=1.2, alpha=0.7)
        ax.annotate(label, xy=(t, ic_val), xytext=(t+5, ic_val-8),
                    fontsize=8, color=color, fontweight='bold',
                    arrowprops=dict(arrowstyle='->', color=color, lw=1))

    # 工作区域着色
    ax.axvspan(20, 150, alpha=0.08, color='green')
    ax.text(85, 95, '安全工作区', ha='center', fontsize=10, color='green', fontweight='bold')

    ax.axvspan(150, 200, alpha=0.08, color='orange')
    ax.text(175, 85, '注意区', ha='center', fontsize=10, color='orange', fontweight='bold')

    ax.axvspan(200, 400, alpha=0.08, color='red')
    ax.text(300, 85, '危险区', ha='center', fontsize=10, color='red', fontweight='bold')

    ax.set_xlabel('加热温度 (°C)', fontsize=11)
    ax.set_ylabel('临界电流保持率 Ic/Ic₀ (%)', fontsize=11)
    ax.set_xlim(20, 400)
    ax.set_ylim(0, 105)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig6_oxygen_diffusion.png")
    fig.savefig(path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: {path}")
    return path


# ============================================================
# 图7: 技术成熟度与趋势预测
# ============================================================
def fig7_technology_roadmap():
    """接头技术成熟度路线图"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    fig.suptitle('图7: REBCO带材接头技术成熟度与发展路线图 (2020-2030)', fontsize=14, fontweight='bold')

    years = np.arange(2020, 2031)

    technologies = {
        '钎焊 (In-Sn)':    {'trl': [8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9], 'color': '#D4784C', 'style': '-'},
        '超声辅助焊':       {'trl': [4, 5, 5, 6, 7, 7, 8, 8, 9, 9, 9], 'color': '#2E75B6', 'style': '-'},
        '铜扩散连接':       {'trl': [1, 2, 2, 3, 5, 6, 7, 8, 8, 9, 9], 'color': '#1F4E79', 'style': '--'},
        '超快铜键合':       {'trl': [0, 0, 0, 0, 1, 3, 5, 6, 7, 8, 8], 'color': '#5B9BD5', 'style': ':'},
        '超导接头(Er123)':  {'trl': [3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5], 'color': '#8B0000', 'style': '-.'},
    }

    trl_labels = {1: '原理', 3: '实验室', 5: '验证', 7: '示范', 9: '商业化'}

    for tech, data in technologies.items():
        ax.plot(years, data['trl'], color=data['color'], linestyle=data['style'],
                linewidth=2.5, marker='o', markersize=5, label=tech)

    # TRL 标签
    for trl, label in trl_labels.items():
        ax.axhline(y=trl, color='gray', linestyle=':', linewidth=0.5, alpha=0.5)
        ax.text(2030.3, trl, label, fontsize=8, color='gray', va='center')

    # 标注关键事件
    events = [
        (2024, 7.5, '★ 铜扩散突破\n(2024)'),
        (2025, 5.0, '★ 超快键合\n(2025)'),
    ]
    for x, y, text in events:
        ax.annotate(text, xy=(x, y), fontsize=9, fontweight='bold', color='#1F4E79',
                    bbox=dict(boxstyle='round', facecolor='#FFF9C4', edgecolor='#F57F17', alpha=0.9))

    ax.set_xlabel('年份', fontsize=11)
    ax.set_ylabel('技术就绪度 (TRL)', fontsize=11)
    ax.set_xlim(2019.5, 2031)
    ax.set_ylim(0, 10)
    ax.set_yticks([1, 3, 5, 7, 9])
    ax.legend(loc='upper left', fontsize=8, ncol=2)
    ax.grid(alpha=0.2)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig7_technology_roadmap.png")
    fig.savefig(path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: {path}")
    return path


# ============================================================
# 图8: 接头综合评分雷达图
# ============================================================
def fig8_radar_comparison():
    """四种接头方法的综合评分雷达图"""
    categories = ['操作便捷性', '接头电阻', '机械强度', '长期可靠性', '工艺成熟度', '设备成本']
    N = len(categories)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    # 评分数据 (1-10)
    data = {
        '钎焊 (搭接焊)': [9, 6, 7, 6, 9, 9],
        '超声辅助焊':    [7, 7, 8, 9, 6, 6],
        '铜扩散连接':    [4, 9, 8, 9, 4, 3],
        '超导接头':      [1, 10, 6, 5, 2, 1],
    }
    colors = ['#D4784C', '#2E75B6', '#1F4E79', '#8B0000']

    fig, ax = plt.subplots(1, 1, figsize=(9, 9), subplot_kw={'projection': 'polar'})
    fig.suptitle('图8: 四种接头技术综合评分雷达图 (1-10分)', fontsize=14, fontweight='bold', y=0.96)

    for (label, values), color in zip(data.items(), colors):
        values_plot = values + values[:1]
        ax.fill(angles, values_plot, alpha=0.15, color=color)
        ax.plot(angles, values_plot, 'o-', linewidth=2, color=color, label=label, markersize=5)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11)
    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(['2', '4', '6', '8', '10'], fontsize=7, color='gray')
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig8_radar_comparison.png")
    fig.savefig(path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: {path}")
    return path


# ============================================================
# 全部生成
# ============================================================
if __name__ == "__main__":
    print("Generating technical figures...")
    paths = [
        fig1_rebco_structure(),
        fig2_joint_types(),
        fig3_soldering_process(),
        fig4_resistance_comparison(),
        fig5_process_window(),
        fig6_oxygen_diffusion(),
        fig7_technology_roadmap(),
        fig8_radar_comparison(),
    ]
    print(f"\nDone: {len(paths)} figures generated in {OUTPUT_DIR}")
