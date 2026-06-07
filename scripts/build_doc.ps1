# ============================================================
# 超导带材接头制作介绍文档生成脚本
# ============================================================

$outPath = "F:\桌面\AI Code\超导带材接头制作方法介绍.docx"

# 如果已存在则删除
if (Test-Path $outPath) { Remove-Item $outPath -Force }

$word = New-Object -ComObject Word.Application
$word.Visible = $false

$doc = $word.Documents.Add()

# ---- 页面设置 ----
$pageSetup = $doc.PageSetup
$pageSetup.TopMargin = 72       # 2.54 cm
$pageSetup.BottomMargin = 72
$pageSetup.LeftMargin = 90
$pageSetup.RightMargin = 90

# ---- 辅助函数 ----
function Add-Title($text, $align=1, $fontSize=22, $bold=$true, $color=0x1F4E79) {
    $rg = $doc.ActiveWindow.Selection
    $rg.EndKey(6)  # wdStory
    $rg.InsertParagraphAfter()
    $rg.Font.Name = "微软雅黑"
    $rg.Font.Size = $fontSize
    $rg.Font.Bold = $bold
    $rg.Font.Color = $color
    $rg.ParagraphFormat.Alignment = $align
    $rg.ParagraphFormat.SpaceBefore = 12
    $rg.ParagraphFormat.SpaceAfter = 6
    $rg.TypeText($text)
    $rg.InsertParagraphAfter()
}

function Add-Heading1($text) {
    $rg = $doc.ActiveWindow.Selection
    $rg.EndKey(6)
    $rg.InsertParagraphAfter()
    $rg.Font.Name = "微软雅黑"
    $rg.Font.Size = 18
    $rg.Font.Bold = $true
    $rg.Font.Color = 0x1F4E79
    $rg.ParagraphFormat.Alignment = 1   # left
    $rg.ParagraphFormat.SpaceBefore = 18
    $rg.ParagraphFormat.SpaceAfter = 8
    $rg.TypeText($text)
    $rg.InsertParagraphAfter()
}

function Add-Heading2($text) {
    $rg = $doc.ActiveWindow.Selection
    $rg.EndKey(6)
    $rg.InsertParagraphAfter()
    $rg.Font.Name = "微软雅黑"
    $rg.Font.Size = 15
    $rg.Font.Bold = $true
    $rg.Font.Color = 0x2E75B6
    $rg.ParagraphFormat.Alignment = 1
    $rg.ParagraphFormat.SpaceBefore = 14
    $rg.ParagraphFormat.SpaceAfter = 6
    $rg.TypeText($text)
    $rg.InsertParagraphAfter()
}

function Add-Heading3($text) {
    $rg = $doc.ActiveWindow.Selection
    $rg.EndKey(6)
    $rg.InsertParagraphAfter()
    $rg.Font.Name = "微软雅黑"
    $rg.Font.Size = 13
    $rg.Font.Bold = $true
    $rg.Font.Color = 0x3A8FD4
    $rg.ParagraphFormat.Alignment = 1
    $rg.ParagraphFormat.SpaceBefore = 10
    $rg.ParagraphFormat.SpaceAfter = 4
    $rg.TypeText($text)
    $rg.InsertParagraphAfter()
}

function Add-Body($text) {
    $rg = $doc.ActiveWindow.Selection
    $rg.EndKey(6)
    $rg.InsertParagraphAfter()
    $rg.Font.Name = "宋体"
    $rg.Font.Size = 12
    $rg.Font.Bold = $false
    $rg.Font.Color = 0x000000
    $rg.ParagraphFormat.Alignment = 1
    $rg.ParagraphFormat.FirstLineIndent = 24  # 两个字符缩进
    $rg.ParagraphFormat.LineSpacingRule = 1   # wdLineSpaceSingle
    $rg.ParagraphFormat.SpaceBefore = 3
    $rg.ParagraphFormat.SpaceAfter = 3
    $rg.TypeText($text)
    $rg.InsertParagraphAfter()
}

function Add-Bullet($text, $indent=0) {
    $rg = $doc.ActiveWindow.Selection
    $rg.EndKey(6)
    $rg.InsertParagraphAfter()
    $rg.Font.Name = "宋体"
    $rg.Font.Size = 12
    $rg.Font.Bold = $false
    $rg.Font.Color = 0x000000
    $rg.ParagraphFormat.Alignment = 1
    $rg.ParagraphFormat.LeftIndent = 36 + ($indent * 24)
    $rg.ParagraphFormat.FirstLineIndent = 0
    $rg.ParagraphFormat.SpaceBefore = 2
    $rg.ParagraphFormat.SpaceAfter = 2
    $rg.TypeText("• " + $text)
    $rg.InsertParagraphAfter()
}

function Add-TableRow($data, $isHeader=$false) {
    $rg = $doc.ActiveWindow.Selection
    $rg.EndKey(6)
    $rg.InsertParagraphAfter()
    $rg.Font.Name = "宋体"
    $rg.Font.Size = 11
    $rg.Font.Bold = $isHeader
    $rg.Font.Color = if ($isHeader) { 0xFFFFFF } else { 0x000000 }
    $rg.ParagraphFormat.Alignment = 1
    $rg.ParagraphFormat.SpaceBefore = 0
    $rg.ParagraphFormat.SpaceAfter = 0
    $rg.TypeText(($data -join " | "))
    $rg.InsertParagraphAfter()
}

# ============================================================
# 文档内容
# ============================================================

# ---- 封面标题 ----
Add-Title "超导带材接头制作方法介绍" 1 26 $true 0x1F4E79

$rg = $doc.ActiveWindow.Selection
$rg.EndKey(6)
$rg.InsertParagraphAfter()
$rg.Font.Name = "微软雅黑"
$rg.Font.Size = 14
$rg.Font.Bold = $false
$rg.Font.Color = 0x666666
$rg.ParagraphFormat.Alignment = 1
$rg.TypeText("—— 主流工艺、关键技术与实践指南 ——")
$rg.InsertParagraphAfter()
$rg.TypeText("（2026年6月）")
$rg.InsertParagraphAfter()

# ---- 第一章 ----
Add-Heading1 "一、引言"

Add-Body "超导材料因其零电阻和完全抗磁性的独特物理性质，在核磁共振成像（MRI）、高能物理加速器、磁约束核聚变、超导储能（SMES）以及高效电力传输等领域具有广泛的应用前景。超导带材作为第二代高温超导（2G-HTS）材料的典型代表，特别是基于REBCO（ReBa₂Cu₃O₇₋δ，稀土钡铜氧）的涂层导体（Coated Conductor, CC），凭借其高临界电流密度和优异的机械性能，已成为超导电力装置的核心材料。"

Add-Body "在实际工程应用中，超导带材的单根长度通常在数百米量级，而大型超导磁体或电力设备往往需要数十公里甚至更长的超导导体。因此，实现高性能、高可靠性的超导带材接头连接，是超导技术走向工程化的关键技术之一。理想的超导接头应当具有低电阻、高机械强度、良好的热稳定性和易于操作的特点。本文将围绕当前最主流的、工程上最容易实现的超导带材接头制作方法，从原理、工艺、关键参数到常见问题，进行系统性的介绍。"

# ---- 第二章 ----
Add-Heading1 "二、超导带材接头的基本概念与分类"

Add-Heading2 "2.1 接头的基本要求"

Add-Body "超导带材接头的核心指标是接头电阻（Joint Resistance）。根据应用场景的不同，对接头电阻的要求也各不相同："

Add-Bullet "持久模式运行（如NMR磁体）：要求接头电阻 < 10⁻¹³ Ω，实现近似"无阻"连接"
Add-Bullet "一般磁体应用（如MRI）：接头电阻 < 10⁻¹¹ Ω 即可满足要求"
Add-Bullet "电力传输应用（如超导电缆）：接头电阻在 nΩ·cm² 量级（10⁻⁹ Ω·cm²）通常可接受"
Add-Bullet "快速放电或脉冲应用：需要兼顾低电阻和高机械强度"

Add-Heading2 "2.2 接头结构的分类"

Add-Body "按照带材连接的结构形式，超导接头主要分为以下三种基本类型："

Add-Bullet "搭接接头（Lap Joint）：两根带材以一定长度重叠搭接，通过中间焊料层或直接冶金结合实现连接。这是目前最主流的结构形式，因为搭接面积大、载流能力强、制备工艺最为简单可靠。"
Add-Bullet "桥接接头（Bridge Joint）：通过中间连接片（焊料片或超导体桥）将两根带材间接连接。适用于空间受限或需要应力缓冲的场合。"
Add-Bullet "对接接头（Butt Joint）：两根带材端面对接。该形式接触面积有限，在实际工程中较少使用。"

Add-Heading2 "2.3 接头的功能分类"

Add-Body "按照接头的电学性能，可分为："

Add-Bullet "低阻接头（Low-Resistance Joint）：接头电阻通常在 10⁻⁸~10⁻¹¹ Ω 范围，是目前工程应用的主流选择，制备相对简单。"
Add-Bullet "无阻接头/超导接头（Persistent Current Joint / Superconducting Joint）：接头区域本身也具有超导性，电阻极低（< 10⁻¹³ Ω），可实现真正意义上的持久电流运行。制备工艺极为复杂，目前仍处于实验室研究和小批量应用阶段。"

# ---- 第三章 ----
Add-Heading1 "三、主流方法一：低熔点焊料钎焊（搭接焊）"

Add-Body "低熔点焊料钎焊是目前工程界使用最广泛、最成熟的超导带材接头制备方法。其基本原理是使用熔点较低的焊料合金（通常低于250°C）作为中间连接介质，通过加热使焊料熔化、润湿带材表面，冷却后形成冶金结合。该方法操作简便、设备要求低、可重复性好，特别适合现场施工和规模化应用。"

Add-Heading2 "3.1 常用焊料体系"

Add-Body "选择合适的焊料是钎焊工艺的核心。下表列出了超导带材接头中最常使用的焊料体系："

# 焊料表格 - 用格式化文本展示
Add-TableRow @("焊料体系", "典型成分", "熔点 (C)", "特点与应用") $true
Add-TableRow @("In-Sn共晶", "In52Sn48", "~118", "最常用，熔点低，润湿性好，对带材热损伤小")
Add-TableRow @("In-Sn-Ag", "In-Sn + 1~5 wt% Ag", "~120-130", "添加Ag提高机械强度和延展性，接头寿命更长")
Add-TableRow @("Pb-Sn", "Pb37Sn63", "~183", "传统焊料，熔点适中，成本低，但含铅环保性差")
Add-TableRow @("Pb-Bi", "Pb-Bi合金", "~125-200", "用于低温超导NbTi接头，可实现10^-14~10^-15量级电阻")
Add-TableRow @("SAC305", "Sn96.5Ag3.0Cu0.5", "~217-221", "无铅环保焊料，熔点较高，适用于高温工况")
Add-TableRow @("SAC0307", "Sn99.0Ag0.3Cu0.7", "~217-228", "无铅低成本替代方案")

Add-Heading2 "3.2 搭接焊接的详细工艺流程"

Add-Heading3 "步骤一：带材表面预处理"

Add-Body "表面预处理是影响接头质量最关键的步骤之一。REBCO带材通常具有多层结构，包括铜稳定层、银保护层、超导层和哈氏合金基底。焊接前必须对带材表面进行适当处理："

Add-Bullet "机械打磨：使用细砂纸（800~1500目）轻轻打磨带材表面的铜稳定层或银层，去除氧化层和表面污染物。注意控制打磨力度，避免损伤超导层。"
Add-Bullet "化学清洗：使用无水乙醇或丙酮擦拭打磨后的表面，去除油污和残留颗粒。部分工艺采用稀盐酸或稀硝酸进行酸洗活化处理（酸洗后须立即用去离子水冲洗并吹干）。"
Add-Bullet "助焊剂涂覆：在待焊接区域均匀涂覆适量助焊剂（Flux），以进一步去除氧化膜并改善焊料润湿性。对于要求严格的场合，可选用免清洗型助焊剂或无纤剂工艺（参见第四章）。"

Add-Heading3 "步骤二：焊接装置预热"

Add-Bullet "将焊接工装（加热平台或热压机）预热至焊料熔点以上约10~30°C。例如，使用In-Sn共晶焊料时，预热温度一般为130~150°C。"
Add-Bullet "预热温度不宜过高（一般不超过200°C），以免对REBCO超导层造成热退化。研究表明，REBCO带材在超过250°C的环境中会发生不可逆的性能衰减。"

Add-Heading3 "步骤三：焊料放置与带材装配"

Add-Bullet "将适量焊料片或焊料丝放置在预处理过的带材搭接区域之间。焊料量以熔化后能完全覆盖搭接面、略有溢出为宜。"
Add-Bullet "带材采用搭接方式对齐，典型搭接长度为5~20 cm。两根带材的超导层应面对面（Face-to-Face）放置，以最大化超导电流传输。"
Add-Bullet "使用定位夹具固定带材位置，保持搭接区域平整、无错位。"

Add-Heading3 "步骤四：加压加热焊接"

Add-Bullet "将装配好的带材置于加热平台上，施加0.5~5 MPa的均匀压力。压力的作用是：促进焊料与带材表面的紧密接触、排出多余焊料和气泡、形成致密的冶金结合层。"
Add-Bullet "保持加热温度和压力约1~5分钟，确保焊料充分熔化和润湿。焊接时间过长可能导致焊料过度氧化，过短则润湿不充分。"
Add-Bullet "对于较长的搭接接头，可采用分段加热或移动式加热夹具，保证整个搭接区域受热均匀。"

Add-Heading3 "步骤五：冷却与后处理"

Add-Bullet "关闭加热源，让接头在压力保持下缓慢冷却至室温。自然冷却即可，但需避免强制急冷（如吹冷风），因为不均匀的冷却速度可能导致接头内部产生热应力裂纹。"
Add-Bullet "冷却后移除夹具，使用无水乙醇清洗接头上残留的助焊剂。助焊剂残留物具有腐蚀性，若不清除会长期腐蚀接头，影响运行可靠性。"
Add-Bullet "目视检查接头外观：焊料应均匀覆盖搭接区域，无明显的虚焊、气孔或裂纹。"
Add-Bullet "使用万用表或四线法测量接头电阻，确保阻值在设计范围内。"

Add-Heading2 "3.3 搭接焊接的关键参数总结"

Add-TableRow @("参数", "推荐范围", "说明") $true
Add-TableRow @("搭接长度", "5~20 cm", "越长电阻越低，但超过20 cm后边际效益递减")
Add-TableRow @("焊料厚度", "50~200 um", "过厚增加电阻，过薄导致结合不充分")
Add-TableRow @("加热温度", "130~200 C", "高于焊料熔点10~30 C，不超过250 C")
Add-TableRow @("焊接压力", "0.5~5 MPa", "适度压力有利冶金结合，过高可能损伤带材")
Add-TableRow @("保温时间", "1~5 min", "确保焊料充分润湿和流动")
Add-TableRow @("冷却方式", "自然冷却", "避免强制急冷，防止热应力裂纹")

# ---- 第四章 ----
Add-Heading1 "四、主流方法二：无纤剂超声辅助焊接"

Add-Body "传统钎焊工艺需要使用助焊剂来去除氧化层、促进焊料润湿。但助焊剂残留物具有腐蚀性，长期运行可能导致接头性能退化。近年来，超声辅助焊接（Ultrasonic-Assisted Soldering / Ultrasonic Welding + Soldering Hybrid）作为一种免纤剂、高可靠性的接头制备方法，逐渐成为国际上的研究热点和工程发展趋势。"

Add-Heading2 "4.1 基本原理"

Add-Body "超声辅助焊接利用高频机械振动（通常20~60 kHz）在带材与焊料界面产生空化效应和摩擦热，从而机械性地去除表面氧化层，使焊料能够在无需化学助焊剂的情况下直接润湿洁净的金属表面。超声振动同时还能促进焊料在界面处的流动和填充，有助于消除气孔、提高接头致密度。"

Add-Heading2 "4.2 工艺流程"

Add-Bullet "带材表面机械打磨，去除明显氧化层（超声对重度氧化层去除效果有限）"
Add-Bullet "在搭接区域放置焊料片（通常为In-Sn系焊料）"
Add-Bullet "将超声焊头（Sonotrode）以一定压力压在焊接区域上"
Add-Bullet "启动超声振动，持续时间通常为0.5~3秒"
Add-Bullet "超声停止后保持压力1~2秒，自然冷却"
Add-Bullet "全程无需助焊剂，焊接后也无需清洗"

Add-Heading2 "4.3 优势与局限"

Add-TableRow @("优势", "局限") $true
Add-TableRow @("无纤剂，免清洗，无腐蚀风险", "设备成本高于传统焊接工装")
Add-TableRow @("焊接速度快（超声作用<1秒）", "对重度氧化表面的处理能力有限")
Add-TableRow @("接头机械强度略优于传统钎焊", "超声参数需针对不同带材优化")
Add-TableRow @("适合现场施工和规模化生产", "搭接长度受超声焊头尺寸限制")

# ---- 第五章 ----
Add-Heading1 "五、主流方法三：冷压焊"

Add-Body "冷压焊（Cold Pressure Welding）是一种在常温（或略高于常温）下，通过施加极高压力使金属界面发生塑性变形从而实现冶金结合的连接方法。该方法无需加热、无需焊料，特别适用于对热敏感的超导材料。在低温超导线材（如NbTi）的连接中已有长期成功应用，近年来也逐渐被探索用于REBCO带材的连接。"

Add-Heading2 "5.1 基本原理"

Add-Body "冷压焊的原理是基于金属的塑性流变。当两种金属表面在超高压力（通常在数百MPa甚至GPa量级）下紧密压合时，界面处的金属原子通过塑性流动和相互扩散形成金属键合。为了使冷压焊成功，需要待连接表面达到原子级清洁度，且材料在焊接压力下能够产生足够的塑性变形（通常要求变形量超过60%）。"

Add-Heading2 "5.2 工艺流程"

Add-Bullet "表面处理：对带材待连接区域进行彻底的机械和化学清洁，去除所有氧化层和污染物。部分工艺使用真空环境或惰性气体保护。"
Add-Bullet "装配定位：将带材以搭接形式精确对准，放入冷压焊模具中。"
Add-Bullet "加压焊接：使用液压机或机械压力机施加高压（通常200~400 MPa），保持压力数秒至数分钟。"
Add-Bullet "卸压与检查：缓慢卸除压力，取出接头。检查接头外观平整度和结合质量。"

Add-Heading2 "5.3 优势与局限"

Add-Body "冷压焊的最大优势是完全避免了高温对超导材料的热损伤，且接头电阻可以做到非常低（NbTi线材的冷压焊接头电阻可达<10⁻¹² Ω）。但该方法对表面清洁度要求极高，工艺窗口较窄，且在REBCO带材（具有脆性的陶瓷超导层）上的应用仍面临挑战——过高的压力可能导致超导层开裂。因此，冷压焊目前在REBCO带材上更适合用于铜稳定层之间的连接，而非超导层之间的直接连接。"

# ---- 第六章 ----
Add-Heading1 "六、主流方法四：铜扩散连接（温压焊）"

Add-Body "铜扩散连接（Copper Diffusion Bonding），也称温压焊（Warm Pressure Welding），是一种新兴的无焊料连接技术。该技术在中等温度（150~180°C）和较高压力（250~333 MPa）下进行，利用铜原子在界面处的扩散实现冶金结合。该方法在2024年左右取得了突破性进展，是当前国际学术界和工业界广泛关注的前沿技术之一。"

Add-Heading2 "6.1 基本原理与优势"

Add-Body "REBCO带材通常采用铜作为稳定层。铜扩散连接直接利用带材自身的铜稳定层作为连接介质，在温和温度（远低于铜的熔点1083°C）和高压下，通过铜原子的固态扩散和塑性变形实现连接。由于不使用任何中间焊料，避免了焊料电阻对整体接头电阻的贡献。"

Add-Body "研究数据表明，铜扩散连接的REBCO带材接头的特征电阻约为16.8 nΩ·cm²，比传统In-Sn焊料钎焊接头（约25 nΩ·cm²）低了约三分之一。同时其机械强度与焊料接头相当。"

Add-Heading2 "6.2 工艺流程要点"

Add-Bullet "带材表面认真清洁，重点去除铜稳定层表面的氧化层"
Add-Bullet "将带材以搭接方式装配，放入精密加压模具中"
Add-Bullet "加热至150~180°C，同时施加250~333 MPa压力"
Add-Bullet "保持温度和压力3~5分钟"
Add-Bullet "在保压条件下缓慢冷却至室温"

Add-Body "该方法虽然电阻性能优异，但目前对设备精度要求极高（需要同时精确控制温度和压力），工艺窗口较窄，尚未大规模推广。对于有一定设备条件和精度控制能力的研究机构或企业，这是一个值得投入的先进技术方向。"

# ---- 第七章 ----
Add-Heading1 "七、各方法综合对比"

Add-Body "下表从多个维度对上述四种主流接头制作方法进行综合对比，以便读者根据自身条件和应用需求选择合适的技术路线："

Add-TableRow @("对比维度", "钎焊（搭接焊）", "超声辅助焊", "冷压焊", "铜扩散连接") $true
Add-TableRow @("操作难度", "低", "中低", "中", "中高")
Add-TableRow @("设备成本", "低", "中", "中", "高")
Add-TableRow @("是否需要焊料", "是", "是", "否", "否")
Add-TableRow @("是否需要助焊剂", "通常需要", "不需要", "不需要", "不需要")
Add-TableRow @("焊接温度", "130~200 C", "常温~150 C", "常温", "150~180 C")
Add-TableRow @("接头电阻 (nO.cm2)", "~20-50", "~17-30", "10^-3~10^-1 nO (NbTi)", "~17")
Add-TableRow @("机械强度", "良好", "优良", "良好", "良好")
Add-TableRow @("工程成熟度", "高（工业标准）", "中高（快速发展）", "高（NbTi）/ 中（REBCO）", "中（前沿研究）")
Add-TableRow @("现场施工便利性", "方便", "较方便", "一般", "较差")
Add-TableRow @("推荐应用场景", "通用、首选方案", "高可靠性要求", "NbTi线材/特殊场景", "追求最低电阻")

# ---- 第八章 ----
Add-Heading1 "八、关键工艺参数与影响因素"

Add-Heading2 "8.1 焊接长度与接头电阻的关系"

Add-Body "接头电阻Rⱼ与搭接长度L之间存在近似反比关系：Rⱼ ≈ Rₛ / L，其中Rₛ为界面比电阻。这意味着增大搭接长度可以有效降低接头电阻。但这一关系的适用范围有限：当搭接长度超过15~20 cm后，电流在搭接区域内的转移已基本完成，继续增加长度带来的电阻降低效果不再明显（边际效益递减）。综合考虑材料利用率和空间限制，5~20 cm是推荐的最佳搭接长度范围。"

Add-Heading2 "8.2 焊料选择的核心权衡"

Add-Body "焊料的选择需要在多个因素之间权衡："

Add-Bullet "低熔点 vs. 高熔点：低熔点焊料（如In-Sn）对带材热损伤小，但接头电阻相对较高；高熔点焊料（如SAC系列）电阻更低，但焊接温度高，可能对超导层造成热退化。"
Add-Bullet "含铅 vs. 无铅：Pb-Sn和Pb-Bi焊料性能优异且工艺成熟，但含铅不符合RoHS环保要求。SAC系列为无铅替代方案。"
Add-Bullet "纯焊料 vs. 掺杂焊料：添加少量Ag、Cu等元素可改善焊料力学性能和抗疲劳特性，但可能略微提高电阻率。"

Add-Heading2 "8.3 表面处理质量"

Add-Body "表面处理质量直接决定焊料在带材表面的润湿性（Wettability）和实际有效接触面积。不良的表面处理（氧化层残留、表面粗糙度不均匀、污染物残留）是导致接头电阻偏高和机械强度不足的最常见原因。建议："

Add-Bullet "打磨后表面粗糙度Ra控制在1~5 um范围内"
Add-Bullet "打磨后30分钟内完成焊接，避免打磨面再次氧化"
Add-Bullet "化学酸洗活化后须立即（5分钟内）完成焊接"

Add-Heading2 "8.4 压力与温度的控制"

Add-Body "适度的压力是形成致密冶金结合的关键。压力过低会导致焊料填充不充分、界面气孔多；压力过高则可能将焊料过度挤出，导致焊料层过薄甚至"干焊"，或损伤带材的超导层。推荐的焊接压力范围通常为0.5~5 MPa，具体应根据焊料种类和带材结构进行优化。"

Add-Body "温度控制同样关键。一方面，焊接温度需高于焊料熔点以保证充分流动和润湿；另一方面，温度不能过高以免超导层热退化。对于REBCO带材，焊接温度一般不应超过200°C（使用In-Sn焊料时为130~150°C）。精度控制在±5°C以内的恒温加热平台是推荐的加热设备。"

# ---- 第九章 ----
Add-Heading1 "九、常见问题与解决方案"

Add-TableRow @("常见问题", "可能原因", "解决方案") $true
Add-TableRow @("接头电阻偏高", "表面处理不充分/焊料氧化/搭接长度不足", "优化打磨和清洗流程；使用新鲜焊料；增加搭接长度")
Add-TableRow @("虚焊（焊料未完全润湿）", "温度不足/助焊剂不足/表面有油污", "提高焊接温度5~10 C；增加助焊剂用量；加强表面清洗")
Add-TableRow @("焊料层气孔过多", "焊接时气体未排出/助焊剂过量沸腾", "优化压力使多余焊料和气体排出；控制助焊剂用量")
Add-TableRow @("超导层临界电流退化", "焊接温度过高/焊接时间过长", "降低焊接温度；缩短保温时间；使用更低熔点焊料")
Add-TableRow @("接头机械强度不足", "焊料层过厚或不均/压力不足", "优化焊料用量和均匀性；适当增大焊接压力")
Add-TableRow @("接头长期运行退化", "助焊剂残留腐蚀/热循环疲劳", "彻底清洗残留助焊剂；改用无纤剂超声焊接工艺")
Add-TableRow @("带材在接头处断裂", "急冷导致热应力集中/压力过大", "自然缓慢冷却；降低焊接压力；检查工装平整度")

# ---- 第十章 ----
Add-Heading1 "十、总结与工艺选择建议"

Add-Body "超导带材接头的制备是超导电力设备走向实际工程应用的关键环节。经过多年的技术发展，目前已形成以低熔点焊料钎焊为主流、超声辅助焊和铜扩散连接为前沿、冷压焊为补充的多元化技术体系。"

Add-Body "针对不同应用场景，提出以下工艺选择建议："

Add-Bullet "一般工程应用（超导电缆、故障限流器等）：优先选择传统的低熔点焊料搭接钎焊，操作简单、成熟可靠、成本最低。推荐使用In-Sn共晶焊料，搭接长度10~15 cm。"
Add-Bullet "高可靠性长寿命应用（MRI磁体、储能磁体等）：推荐采用超声辅助无纤剂焊接或铜扩散连接，避免助焊剂残留带来的长期退化风险。"
Add-Bullet "低温超导线材（NbTi）连接：冷压焊是经过充分验证的成熟选择，可实现10⁻¹² Ω以下的超低接头电阻。"
Add-Bullet "追求最低接头电阻（持久模式磁体）：需采用超导接头/无阻接头技术（如Ag扩散连接或熔融扩散法），但需认识到该技术目前工艺难度极大、重复性有限，仅限于有经验的实验室或专业厂家操作。"

Add-Body "未来发展趋势方面，免纤剂化、低温化、高可靠性和自动化是超导带材接头技术的发展方向。超声辅助焊接和铜扩散连接技术正在从实验室走向工程应用，有望在3~5年内成为新一代表征性主流工艺。同时，基于机器视觉的自动焊接设备和在线质量检测系统也将逐步普及，进一步提升超导接头的一致性和可靠性。"

Add-Body ""


# ============================================================
# 参考说明
# ============================================================
Add-Heading1 "参考资料说明"

Add-Body "本文档内容综合参考了以下来源的研究成果和专业资料："
Add-Bullet "常用超导材料接头技术研究进展，RMME，2024年第2期"
Add-Bullet "Fabrication of Flux-Free REBCO CC Joints by Hybridizing Ultrasonic Welding and Soldering，IEEE TAS，2024"
Add-Bullet "A Novel Low-Resistance Solder-Free Copper Bonding Joint Using Warm Pressure Welding Method for REBCO Coated Conductors，Supercond. Sci. Technol.，2024"
Add-Bullet "第二代高温超导REBCO带材超导接头的制备及性能研究，中国科学院大学博士学位论文，2021"
Add-Bullet "Ba122铁基超导带材焊接接头制备与性能研究，低温物理学报，2024"
Add-Bullet "低温超导材料NbTi连接方法相关综述文献"
Add-Bullet "国际磁体技术会议（MT）系列学术报告"

# ============================================================
# 保存文档
# ============================================================
$doc.SaveAs($outPath)
$doc.Close()
$word.Quit()

Write-Host "文档已生成：$outPath"

# 释放 COM 对象
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc) | Out-Null
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()
