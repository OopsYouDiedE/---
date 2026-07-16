# -*- coding: utf-8 -*-
"""禁引扫描：用《禁引与存疑台账.md》的特征串扫正文章节。

用法（章节定稿或渲染前）：
    python check_banned.py            # 扫全部章节
    python check_banned.py 射_一_强身健体.md   # 只扫指定文件

命中即打印 文件:行号:特征串，并以退出码 1 结束；无命中退出码 0。
特征串是辅助网：命中不等于违规（需人工看该处引用），未命中不等于合规。
"""
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LEDGER = ROOT / "禁引与存疑台账.md"
CHAPTER_PREFIXES = ("总序", "射_", "御_", "礼_", "书_", "乐_", "数_", "终章")


def load_patterns():
    text = LEDGER.read_text(encoding="utf-8")
    m = re.search(r"```banned-patterns\n(.*?)```", text, re.S)
    if not m:
        print("错误：台账中找不到 ```banned-patterns``` 代码块", file=sys.stderr)
        sys.exit(2)
    return [ln.strip() for ln in m.group(1).splitlines() if ln.strip()]


def chapter_files(args):
    if args:
        return [ROOT / a for a in args]
    return sorted(
        p for p in ROOT.glob("*.md")
        if p.name.startswith(CHAPTER_PREFIXES)
    )


def main():
    patterns = load_patterns()
    hits = 0
    for path in chapter_files(sys.argv[1:]):
        if not path.exists():
            print(f"跳过（不存在）：{path.name}", file=sys.stderr)
            continue
        for lineno, line in enumerate(
            io.open(path, encoding="utf-8"), start=1
        ):
            for pat in patterns:
                if pat in line:
                    hits += 1
                    print(f"{path.name}:{lineno}: 命中「{pat}」")
    if hits:
        print(f"\n共 {hits} 处命中——逐处核对是否违反《禁引与存疑台账》。")
        sys.exit(1)
    print("未命中任何禁引特征串。")


if __name__ == "__main__":
    main()
