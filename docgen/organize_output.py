"""整理输出文件到专题文件夹"""
import os, shutil

BASE = r"f:\桌面\AI Code\output"

# 创建专题文件夹
topic = input("专题文件夹名 (如 REBCO带材接头技术调研): ").strip()
if not topic:
    topic = "调研报告"
report_dir = os.path.join(BASE, topic)
os.makedirs(report_dir, exist_ok=True)

# 复制所有文件
copied = 0
for name in os.listdir(BASE):
    src = os.path.join(BASE, name)
    dst = os.path.join(report_dir, name)
    if os.path.isfile(src):
        shutil.copy2(src, dst)
        size_kb = os.path.getsize(dst) / 1024
        print(f"  {name} ({size_kb:.0f} KB)")
        copied += 1
    elif os.path.isdir(src) and name == "figures":
        if not os.path.exists(dst):
            shutil.copytree(src, dst)
        print(f"  figures/ ({len(os.listdir(dst))} images)")
        copied += 1

print(f"\nDone: {copied} items -> {report_dir}")
os.startfile(report_dir)
