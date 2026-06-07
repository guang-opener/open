Add-Type -AssemblyName System.IO.Compression.FileSystem

$scriptRoot = $PSScriptRoot

# Load content from JSON (UTF-8)
$jsonPath = Join-Path $scriptRoot "hts_data.json"
$jsonText = [System.IO.File]::ReadAllText($jsonPath, [System.Text.UTF8Encoding]::new($true))
$data = $jsonText | ConvertFrom-Json

$docxFilename = $data.outputFilename + ".docx"
$docxPath = Join-Path $scriptRoot $docxFilename
if (Test-Path $docxPath) { Remove-Item $docxPath -Force }

$tmpDir = Join-Path $env:TEMP "docx_build_hts"
if (Test-Path $tmpDir) { Remove-Item $tmpDir -Recurse -Force }
New-Item -ItemType Directory -Path "$tmpDir\_rels" -Force | Out-Null
New-Item -ItemType Directory -Path "$tmpDir\word\_rels" -Force | Out-Null

# Font definitions (using English names that render Chinese correctly)
$fontBody = "SimSun"
$fontTitle = "Microsoft YaHei"

# Helper: escape XML
function X($s) { return $s.Replace('&','&amp;').Replace('"','&quot;').Replace('<','&lt;').Replace('>','&gt;') }

function WmlPara($text, $font, $fs, $bold, $color, $align, $sb, $sa, $il, $ih, $fl) {
    $t = X $text
    $bTag = if ($bold) { "<w:b/><w:bCs/>" } else { "" }
    $indent = ""
    if ($il) { $indent += "<w:ind w:left=""$il"" w:hanging=""$ih"" w:firstLine=""$fl""/>" }
    return @"
  <w:p>
    <w:pPr><w:jc w:val="$align"/><w:spacing w:before="$sb" w:after="$sa"/>$indent</w:pPr>
    <w:r>
      <w:rPr>$bTag<w:rFonts w:eastAsia="$font" w:ascii="$font" w:hAnsi="$font"/><w:sz w:val="$fs"/><w:color w:val="$color"/></w:rPr>
      <w:t xml:space="preserve">$t</w:t>
    </w:r>
  </w:p>
"@
}

$bodyXml = @()

# Title page
$bodyXml += WmlPara $data.title $fontTitle "52" $true "1F4E79" "center" "600" "0" $false $false 0
$bodyXml += WmlPara $data.subtitle $fontTitle "28" $false "888888" "center" "60" "0" $false $false 0
$bodyXml += WmlPara $data.subtitle2 $fontTitle "26" $false "999999" "center" "40" "200" $false $false 0
$bodyXml += WmlPara $data.date $fontTitle "24" $false "AAAAAA" "center" "600" "0" $false $false 0

# Sections
foreach ($sec in $data.sections) {
    $bodyXml += WmlPara $sec.heading $fontTitle "36" $true "1F4E79" "left" "400" "100" $false $false 0

    foreach ($item in $sec.body) {
        $bodyXml += WmlPara $item $fontBody "24" $false "000000" "left" "40" "40" $false $false 480
    }

    if ($sec.subsections) {
        foreach ($sub in $sec.subsections) {
            $bodyXml += WmlPara $sub.title $fontTitle "26" $true "2E75B6" "left" "160" "40" $false $false 0
            $bodyXml += WmlPara $sub.text $fontBody "24" $false "000000" "left" "40" "40" $false $false 480
        }
    }
}

# Refs heading and entries
$bodyXml += WmlPara $data.refsHeading $fontTitle "32" $true "1F4E79" "left" "400" "100" $false $false 0
foreach ($ref in $data.refs) {
    $bodyXml += WmlPara $ref $fontBody "22" $false "555555" "left" "20" "20" $false $false 0
}

# Build document.xml
$documentXml = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>
$($bodyXml -join "`n")
    <w:sectPr>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="1440" w:right="1800" w:bottom="1440" w:left="1800"/>
    </w:sectPr>
  </w:body>
</w:document>
"@

# Write files
$documentXml | Out-File -FilePath "$tmpDir\word\document.xml" -Encoding UTF8

@'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
'@ | Out-File -LiteralPath "$tmpDir\[Content_Types].xml" -Encoding UTF8

@'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
'@ | Out-File -FilePath "$tmpDir\_rels\.rels" -Encoding UTF8

@'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
</Relationships>
'@ | Out-File -FilePath "$tmpDir\word\_rels\document.xml.rels" -Encoding UTF8

# Create ZIP as .docx
[System.IO.Compression.ZipFile]::CreateFromDirectory($tmpDir, $docxPath)
Remove-Item $tmpDir -Recurse -Force

Write-Host "DOCX: $docxPath"
Write-Host "SIZE: $((Get-Item $docxPath).Length) bytes"
