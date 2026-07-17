# -*- coding: utf-8 -*-
"""生成《叶子小节字数排序.md》。

口径（与 2026-07 首版一致）：
- 叶子小节 = 没有下级 # 的最小标题；正文 = 标题到下一个任意级标题之间。
- 非叶子标题（如章题 H1）名下直挂的文字不计。
- 章末书目节（引用/引用文献/参考来源/参考文献/参考资料）整体剥离。
- 计数 = CJK 汉字数；HTML 注释（配图标记等）剥离；代码块内标题不算标题。
- ▽薄 < 193，▲厚 > 772（固定阈值，保持跨轮可比）。

用法：python leaf_stats.py [--check]   （--check 只打印各章合计不写文件）
"""
import io
import re
import statistics
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "叶子小节字数排序.md"
THIN, THICK = 193, 772
BIBLIO = re.compile(r"^(引用|引用文献|参考来源|参考文献|参考资料)\s*$")
CJK = re.compile(r"[〇㐀-䶿一-鿿]")
COMMENT = re.compile(r"<!--.*?-->", re.S)

CHAPTERS = [
    "总序.md",
    "射_一_强身健体.md", "射_二_保卫自我.md", "射_三_军事基础.md", "射_四_应急预案.md",
    "御_一_骑行与载具安全.md", "御_二_移动的德行.md", "御_三_组织物流运输.md", "御_四_安全搬运与人力协作.md",
    "礼_一_方便他人的技巧.md", "礼_二_为少数群体提供便利.md", "礼_三_公平契约.md", "礼_四_礼节.md", "礼_五_组织怎么运行.md",
    "数_一_数论.md", "数_二_微积分与线性代数.md", "数_三_概率论.md", "数_四_拓扑学.md",
    "数_五_数学模拟.md", "数_六_神经网络与Transformer.md", "数_七_训练的数学.md",
    "书_一_准确地描述一件事实.md", "书_二_书写论文.md", "书_三_事实核验的原则.md", "书_四_识别汇报者的谎言.md",
    "书_五_交接的艺术.md",
    "终章_用你学会的来拆我.md",
]


def parse(path):
    text = COMMENT.sub("", (ROOT / path).read_text(encoding="utf-8"))
    heads = []  # (level, title, body_cjk_of_own_segment)
    fence = False
    cur = None
    bodies = []
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            fence = not fence
            bodies.append(line)
            continue
        m = None if fence else re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if m:
            if cur is not None:
                heads.append((cur[0], cur[1], len(CJK.findall("\n".join(bodies)))))
            cur = (len(m.group(1)), m.group(2))
            bodies = []
        else:
            bodies.append(line)
    if cur is not None:
        heads.append((cur[0], cur[1], len(CJK.findall("\n".join(bodies)))))
    # 叶子判定与面包屑
    leaves = []
    first_h1 = next((i for i, h in enumerate(heads) if h[0] == 1), None)
    for i, (lv, title, n) in enumerate(heads):
        is_leaf = True
        for lv2, _, _ in heads[i + 1:]:
            if lv2 <= lv:
                break
            is_leaf = False
            break
        if not is_leaf:
            continue
        # 面包屑：向前找各级祖先
        chain, want = [], lv - 1
        for j in range(i - 1, -1, -1):
            if heads[j][0] <= want:
                chain.append((j, heads[j][1]))
                want = heads[j][0] - 1
        chain.reverse()
        names = [t for j, t in chain if not (j == first_h1)] + [title]
        if i == first_h1:
            names = [title]
        if any(BIBLIO.match(t) for t in names):
            continue
        leaves.append({"n": n, "path": " › ".join(names), "lv": f"H{lv}"})
    return leaves


def fmt(n):
    return f"{n:,}"


def mark(n):
    return "▽薄" if n < THIN else ("▲厚" if n > THICK else "")


def main():
    check = "--check" in sys.argv
    per = []
    for ch in CHAPTERS:
        leaves = parse(ch)
        name = ch[:-3]
        sizes = [x["n"] for x in leaves]
        per.append({
            "name": name, "leaves": leaves, "total": sum(sizes), "cnt": len(sizes),
            "med": int(statistics.median(sizes)) if sizes else 0,
            "thin": sum(1 for s in sizes if s < THIN),
            "thick": sum(1 for s in sizes if s > THICK),
        })
    all_leaves = [dict(x, ch=c["name"]) for c in per for x in c["leaves"]]
    sizes = [x["n"] for x in all_leaves]
    total, cnt = sum(sizes), len(sizes)
    if check:
        for c in per:
            print(f"{c['name']}\t{c['total']}\t{c['cnt']}\t{c['med']}")
        print(f"合计\t{total}\t{cnt}\t中位{int(statistics.median(sizes))}\t均值{int(sum(sizes)/cnt)}")
        return

    L = []
    L.append(f"> ⚠️ **{date.today():%Y-%m-%d} 重算**：知识库两轮修复与正文引用体检后全量重新生成（引用格式修正、射_四书目去重、禁引数字改写等）。生成程序：`leaf_stats.py`。")
    L.append(f"> 口径变化：本轮起 HTML 注释（配图标记等）不再计入正文汉字——它们不是读者可见文字。旧口径总数 334,061 与本轮的差额约 1.1 万即来自于此，叶子数与叶子判定完全不变。")
    L.append("")
    L.append("# 叶子小节字数排序（明确到每一级最小标题）")
    L.append("")
    L.append("> **叶子小节**＝没有下级 `#` 的最小标题。**章末书目节**（引用/引用文献/参考来源）已剥离，不计入。")
    L.append("> 计数口径：正文**汉字数**（CJK），标题到下一标题之间。")
    L.append(f"> 全书共 **{cnt}** 个正文叶子；中位 **{int(statistics.median(sizes))}** 字，均值 **{int(sum(sizes)/cnt)}** 字，最薄 **{min(sizes)}**，最厚 **{max(sizes)}**。")
    L.append(f"> 标记：`▽薄`＝<{THIN}；`▲厚`＝>{THICK}。")
    L.append("")
    L.append("## 各章正文字数（已剥离书目）")
    L.append("")
    L.append("| 章 | 正文汉字 | 正文叶子数 | 叶子中位 | ▽薄 | ▲厚 |")
    L.append("|---|---:|---:|---:|---:|---:|")
    for c in per:
        L.append(f"| {c['name']} | {fmt(c['total'])} | {c['cnt']} | {c['med']} | {c['thin']} | {c['thick']} |")
    L.append(f"| **全书合计** | **{fmt(total)}** | **{cnt}** | — | — | — |")
    L.append("")
    L.append("## 全书最薄 25（最该补厚的）")
    L.append("")
    L.append("| 字数 | 章 | 路径 | 级 |")
    L.append("|---:|---|---|---|")
    for x in sorted(all_leaves, key=lambda x: x["n"])[:25]:
        L.append(f"| {x['n']} | {x['ch']} | {x['path']} | {x['lv']} |")
    L.append("")
    L.append("## 全书最厚 25（可考虑拆分）")
    L.append("")
    L.append("| 字数 | 章 | 路径 | 级 |")
    L.append("|---:|---|---|---|")
    for x in sorted(all_leaves, key=lambda x: -x["n"])[:25]:
        L.append(f"| {fmt(x['n'])} | {x['ch']} | {x['path']} | {x['lv']} |")
    L.append("")
    L.append("## 逐章叶子明细（章内按正文顺序）")
    L.append("")
    for c in per:
        L.append(f"### {c['name']}　（正文叶子 {c['cnt']} ｜ 正文 {fmt(c['total'])} 汉字 ｜ 中位 {c['med']}）")
        L.append("")
        L.append("| 字数 | 路径 | 级 | |")
        L.append("|---:|---|---|---|")
        for x in c["leaves"]:
            L.append(f"| {x['n']} | {x['path']} | {x['lv']} | {mark(x['n'])} |")
        L.append("")
    OUT.write_text("\n".join(L).rstrip() + "\n", encoding="utf-8", newline="\n")
    print(f"已写出 {OUT.name}：{cnt} 叶子 / {fmt(total)} 汉字")


if __name__ == "__main__":
    main()
