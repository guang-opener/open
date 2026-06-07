$docxPath = Join-Path $PSScriptRoot "高温超导简介.docx"
if (Test-Path $docxPath) { Remove-Item $docxPath -Force }

# Create temp working directory
$tmpDir = Join-Path $env:TEMP "docx_build"
if (Test-Path $tmpDir) { Remove-Item $tmpDir -Recurse -Force }
New-Item -ItemType Directory -Path "$tmpDir\_rels" -Force | Out-Null
New-Item -ItemType Directory -Path "$tmpDir\word\_rels" -Force | Out-Null

# ---- [Content_Types].xml ----
@'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
'@ | Out-File -FilePath "$tmpDir\[Content_Types].xml" -Encoding UTF8

# ---- _rels/.rels ----
@'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
'@ | Out-File -FilePath "$tmpDir\_rels\.rels" -Encoding UTF8

# ---- Build word/document.xml ----
$paragraphs = @()

function Add-Paragraph($text, $style, $align, $fontName, $fontSize, $bold, $color, $spaceBefore, $spaceAfter, $indent) {
    $indentAttr = if ($indent) { "<w:ind w:firstLine=""$indent""/>" } else { "" }
    $boldAttr = if ($bold) { '<w:b/><w:bCs/>' } else { "" }
    return @"
<w:p>
  <w:pPr>
    <w:jc w:val="$align"/>
    <w:spacing w:before="$spaceBefore" w:after="$spaceAfter"/>
    $indentAttr
  </w:pPr>
  <w:r>
    <w:rPr>
      $boldAttr
      <w:rFonts w:eastAsia="$fontName" w:ascii="$fontName" w:hAnsi="$fontName"/>
      <w:sz w:val="$fontSize"/>
      <w:color w:val="$color"/>
    </w:rPr>
    <w:t xml:space="preserve">$text</w:t>
  </w:r>
</w:p>
"@
}

function Add-EmptyPara {
    return "<w:p><w:pPr><w:spacing w:before=""40"" w:after=""0""/></w:pPr></w:p>"
}

function Add-HeadingPara($text, $fontSize, $color, $spaceBefore) {
    return @"
<w:p>
  <w:pPr>
    <w:spacing w:before="$spaceBefore" w:after="100"/>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:b/><w:bCs/>
      <w:rFonts w:eastAsia="微软雅黑" w:ascii="微软雅黑" w:hAnsi="微软雅黑"/>
      <w:sz w:val="$fontSize"/>
      <w:color w:val="$color"/>
    </w:rPr>
    <w:t xml:space="preserve">$text</w:t>
  </w:r>
</w:p>
"@
}

function Add-BulletPara($text) {
    return @"
<w:p>
  <w:pPr>
    <w:ind w:left="720" w:hanging="360"/>
    <w:spacing w:before="20" w:after="20"/>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:rFonts w:eastAsia="宋体" w:ascii="宋体" w:hAnsi="宋体"/>
      <w:sz w:val="24"/>
    </w:rPr>
    <w:t xml:space="preserve">  $text</w:t>
  </w:r>
</w:p>
"@
}

function Add-BodyPara($text) {
    return @"
<w:p>
  <w:pPr>
    <w:spacing w:before="40" w:after="40"/>
    <w:ind w:firstLine="480"/>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:rFonts w:eastAsia="宋体" w:ascii="宋体" w:hAnsi="宋体"/>
      <w:sz w:val="24"/>
    </w:rPr>
    <w:t xml:space="preserve">$text</w:t>
  </w:r>
</w:p>
"@
}

# Build document XML
$docBody = @()
$docBody += Add-HeadingPara "高温超导简介" "52" "1F4E79" "600"
$docBody += Add-Paragraph "High-Temperature Superconductivity" "center" "Arial" "28" $false "888888" "60" "0" $false
$docBody += Add-Paragraph "—— 从发现到应用 ——" "center" "微软雅黑" "26" $false "999999" "40" "200" $false
$docBody += Add-Paragraph "2026年6月" "center" "微软雅黑" "24" $false "AAAAAA" "600" "0" $false

# Chapter 1
$docBody += Add-HeadingPara "一、什么是超导" "36" "1F4E79" "400"
$docBody += Add-BodyPara "超导（Superconductivity）是指某些材料在温度降低到某一临界温度（Tc）以下时，电阻突然消失为零，同时表现出完全抗磁性（迈斯纳效应）的物理现象。超导体具有三个基本临界参数："
$docBody += Add-BulletPara "临界温度（Tc）：材料进入超导态的最高温度"
$docBody += Add-BulletPara "临界磁场（Hc）：破坏超导态所需的最小磁场强度"
$docBody += Add-BulletPara "临界电流密度（Jc）：超导体所能承载的最大无阻电流密度"

# Chapter 2
$docBody += Add-HeadingPara "二、超导材料的发展历程" "36" "1F4E79" "400"
$docBody += Add-BodyPara "1911年 —— 荷兰物理学家昂内斯（H. K. Onnes）首次在汞（Hg）中发现了超导现象，临界温度为4.2 K（约-269C），开启了超导研究的百年历程。"
$docBody += Add-BodyPara "1950s-1970s —— 发展了NbTi（铌钛）和Nb3Sn（铌三锡）等低温超导材料，Tc分别为9.2 K和18 K。这类材料至今仍是MRI磁体和加速器磁体的主力。"
$docBody += Add-BodyPara "1986年 —— IBM苏黎世实验室的柏诺兹（Bednorz）和缪勒（Muller）发现了La-Ba-Cu-O超导体，Tc达到35 K，突破了此前认为的30 K上限，开启了高温超导时代。两人因此获得1987年诺贝尔物理学奖。"
$docBody += Add-BodyPara "1987年 —— 朱经武和吴茂昆团队发现了YBa2Cu3O7-x（YBCO，钇钡铜氧）超导体，Tc高达93 K，首次突破了液氮温度（77 K）大关，使得超导技术的冷却成本大幅降低。"
$docBody += Add-BodyPara "2000年代至今 —— REBCO涂层导体（第二代高温超导带材）、MgB2（二硼化镁，Tc=39 K）、铁基超导体（2008年发现）等新型材料相继涌现，超导应用技术不断走向成熟。"

# Chapter 3
$docBody += Add-HeadingPara "三、主要高温超导材料体系" "36" "1F4E79" "400"

# Simple table as formatted text
$docBody += Add-BodyPara "目前最主要的几类高温超导材料如下："
$docBody += Add-BulletPara "REBCO涂层导体 [Tc~93 K]：Y(Gd)Ba2Cu3O7-x，第二代高温超导带材主力，载流能力极强，广泛用于强磁场磁体、超导电缆等"
$docBody += Add-BulletPara "BSCCO铋系 [Tc~110 K]：Bi2Sr2Ca2Cu3O10，第一代高温超导带材，已商业化，用于限流器、储能等"
$docBody += Add-BulletPara "MgB2 [Tc~39 K]：成本低、结构简单，适合制冷机冷却，用于MRI磁体、输电等"
$docBody += Add-BulletPara "铁基超导体 [Tc~55 K]：2008年发现，上临界场极高（>100 T），有潜力用于超高场磁体"
$docBody += Add-BulletPara "YBCO块材 [Tc~93 K]：用于超导磁悬浮、飞轮储能、磁场屏蔽等"

# Chapter 4
$docBody += Add-HeadingPara "四、主要应用领域" "36" "1F4E79" "400"

$docBody += Add-Paragraph "1. 核磁共振成像（MRI）" "left" "微软雅黑" "26" $true "2E75B6" "160" "40" $false
$docBody += Add-BodyPara "MRI是超导技术目前最成功的商业化应用。超导磁体提供1.5~7 T的高均匀度磁场，用于人体无创成像诊断。全球已有超过5万台超导MRI设备在运行，主要使用NbTi低温超导线材。"

$docBody += Add-Paragraph "2. 高能物理加速器" "left" "微软雅黑" "26" $true "2E75B6" "120" "40" $false
$docBody += Add-BodyPara "大型强子对撞机（LHC）使用了约1200吨NbTi超导线材制造偏转磁体和聚焦磁体。未来环形对撞机（FCC）计划采用高温超导材料以实现更高场强。"

$docBody += Add-Paragraph "3. 磁约束核聚变" "left" "微软雅黑" "26" $true "2E75B6" "120" "40" $false
$docBody += Add-BodyPara "ITER（国际热核聚变实验堆）和SPARC等聚变装置需要强大的超导磁体来约束高温等离子体。REBCO高温超导带材可使聚变磁体工作于更高场强和更高温度，大幅缩小装置体积。"

$docBody += Add-Paragraph "4. 超导电力技术" "left" "微软雅黑" "26" $true "2E75B6" "120" "40" $false
$docBody += Add-BodyPara "包括超导电缆（低损耗大容量输电）、超导限流器（电网故障快速保护）、超导储能（SMES，高效电能储存）和超导变压器（体积小、效率高）。上海、深圳等城市已进行了超导电缆的挂网示范运行。"

$docBody += Add-Paragraph "5. 磁悬浮与交通运输" "left" "微软雅黑" "26" $true "2E75B6" "120" "40" $false
$docBody += Add-BodyPara "利用超导体的完全抗磁性实现无接触悬浮。日本山梨县的超导磁悬浮列车（SCMaglev）创造了603 km/h的地面轨道速度纪录。"

$docBody += Add-Paragraph "6. 前沿科学仪器" "left" "微软雅黑" "26" $true "2E75B6" "120" "40" $false
$docBody += Add-BodyPara "超导量子干涉仪（SQUID）可探测极微弱磁场（fT级），用于脑磁图、心磁图等生物磁场探测。超导单光子探测器在量子通信和深空光通信中扮演关键角色。"

# Chapter 5
$docBody += Add-HeadingPara "五、高温超导面临的技术挑战" "36" "1F4E79" "400"
$docBody += Add-BulletPara "材料制备成本高：REBCO涂层导体制造工艺复杂，价格昂贵（约100~500美元/米），是制约大规模应用的主要瓶颈。"
$docBody += Add-BulletPara "冷却系统复杂：尽管高温超导可使用液氮（77 K）冷却，但在强磁场应用中仍需更低温度（20~50 K），依赖昂贵的制冷机系统。"
$docBody += Add-BulletPara "机械脆性：陶瓷性质的高温超导材料脆性大，对应力敏感，在绕制磁体和线圈时容易损坏。"
$docBody += Add-BulletPara "接头技术：超导带材长度有限，高性能低电阻接头制备是工程化的关键难题。"
$docBody += Add-BulletPara "失超保护：高温超导材料失超传播速度比低温超导慢数百倍，局部热失控风险高，需要更复杂的保护系统。"

# Chapter 6
$docBody += Add-HeadingPara "六、未来展望" "36" "1F4E79" "400"
$docBody += Add-BodyPara "高温超导技术正处于从实验室向大规模工程应用跨越的关键阶段。未来5~10年的主要趋势包括："
$docBody += Add-BulletPara "材料成本持续下降：随着生产工艺改进和规模化生产，REBCO带材价格有望降至50美元/米以下。"
$docBody += Add-BulletPara "紧凑型聚变装置：SPARC等装置有望首次实现聚变能量增益（Q>1），成为高温超导最激动人心的应用。"
$docBody += Add-BulletPara "超导电力设备商业化：超导电缆、限流器将在城市电网中获得更多示范和商业部署。"
$docBody += Add-BulletPara "氢能超导混合传输：液氢冷却超导电缆概念将获得更多关注，实现能源与电力的协同传输。"
$docBody += Add-BulletPara "室温超导探索：室温超导仍是终极梦想——尽管近年来时有突破性宣称，但真正可重复、可实用的室温超导材料仍有待探索。"
$docBody += Add-BodyPara "高温超导作为21世纪最具变革性的技术之一，将在能源、医疗、交通、科学研究等领域持续释放巨大的应用潜力。随着材料科学和低温工程技术的不断进步，超导技术的春天正在加速到来。"

# References
$docBody += Add-HeadingPara "参考资料" "32" "1F4E79" "400"
$refs = @(
    'J. G. Bednorz and K. A. Muller, "Possible High Tc Superconductivity in the Ba-La-Cu-O System", Z. Phys. B, 1986',
    'M. K. Wu et al., "Superconductivity at 93 K in a New Mixed-Phase Y-Ba-Cu-O Compound System", Phys. Rev. Lett., 1987',
    'D. Larbalestier et al., "High-Tc Superconducting Materials for Electric Power Applications", Nature, 2001',
    'H. Kamihara et al., "Iron-Based Layered Superconductor La[O1-xFx]FeAs", J. Am. Chem. Soc., 2008',
    '中国超导电子学中长期发展规划研究报告，2023'
)
foreach ($ref in $refs) {
    $docBody += Add-Paragraph $ref "left" "宋体" "22" $false "555555" "20" "20" $false
}

# Assemble document.xml
$documentXml = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>
$($docBody -join "`n")
    <w:sectPr>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="1440" w:right="1800" w:bottom="1440" w:left="1800"/>
    </w:sectPr>
  </w:body>
</w:document>
"@
$documentXml | Out-File -FilePath "$tmpDir\word\document.xml" -Encoding UTF8

# ---- word/_rels/document.xml.rels ----
@'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
</Relationships>
'@ | Out-File -FilePath "$tmpDir\word\_rels\document.xml.rels" -Encoding UTF8

# ---- Create ZIP/.docx ----
Add-Type -AssemblyName System.IO.Compression.FileSystem
if (Test-Path $docxPath) { Remove-Item $docxPath -Force }
[System.IO.Compression.ZipFile]::CreateFromDirectory($tmpDir, $docxPath)

# Cleanup
Remove-Item $tmpDir -Recurse -Force

Write-Host "DONE: $docxPath"
Write-Host "Size: $((Get-Item $docxPath).Length) bytes"
