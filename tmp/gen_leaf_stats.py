# -*- coding: utf-8 -*-
import re, os, statistics, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILES = [
    "总序",
    "礼_一_方便他人的技巧", "礼_二_为少数群体提供便利", "礼_三_公平契约", "礼_四_礼节", "礼_五_组织怎么运行",
    "射_一_强身健体", "射_二_保卫自我", "射_三_军事基础", "射_四_应急预案",
    "御_一_骑行与载具安全", "御_二_移动的德行", "御_三_组织物流运输", "御_四_安全搬运与人力协作",
    "书_一_准确地描述一件事实", "书_二_书写论文", "书_三_事实核验的原则", "书_四_识别汇报者的谎言",
    "终章_用你学会的来拆我",
]

BIB = {"引用", "引用文献", "参考来源"}
CJK = re.compile(r"[一-鿿]")
H = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
THIN, THICK = 193, 772

def count_cjk(s):
    return len(CJK.findall(s))

def med_int(vals):
    return int(statistics.median(vals))  # 与原表一致：偶数叶子取下整

def parse_file(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    heads, in_code = [], False
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("```"):
            in_code = not in_code; continue
        if in_code: continue
        m = H.match(ln)
        if m: heads.append((i, len(m.group(1)), m.group(2)))
    leaves = []
    for k, (ln, lvl, title) in enumerate(heads):
        nxt_ln = heads[k+1][0] if k+1 < len(heads) else len(lines)
        nxt_lvl = heads[k+1][1] if k+1 < len(heads) else 0
        if not ((k+1 >= len(heads)) or (nxt_lvl <= lvl)):
            continue
        body = "\n".join(lines[ln+1:nxt_ln])
        words = count_cjk(body)
        anc2, cur = [], lvl
        for j in range(k-1, -1, -1):
            if heads[j][1] < cur:
                if heads[j][1] >= 2: anc2.append(heads[j][2])
                cur = heads[j][1]
                if cur == 1: break
        anc2.reverse()
        segs = anc2 + [title]
        is_bib = (title.strip() in BIB) or any(a.strip() in BIB for a in anc2)
        leaves.append({"level": lvl, "title": title, "segs": segs,
                       "words": words, "is_bib": is_bib})
    return leaves

per_chapter, allrows = [], []
for name in FILES:
    lv = [x for x in parse_file(os.path.join(ROOT, name + ".md")) if not x["is_bib"]]
    per_chapter.append((name, lv))
    for x in lv:
        allrows.append((name, x))

all_words = [x["words"] for (_, x) in allrows]
n = len(all_words)
med = med_int(all_words)
mean = round(sum(all_words)/n)
mn, mx = min(all_words), max(all_words)
grand = sum(all_words)

def mark(w):
    return "▲厚" if w > THICK else ("▽薄" if w < THIN else "")

out = []
out.append("> ⚠️ **2026-07 全量重算**：射卷重构为四章（强身健体/保卫自我/军事基础/应急预案）并升级到职业手册深度；礼卷补入礼_三_公平契约、礼_四_礼节、礼_五_组织怎么运行，书卷补入书_一_准确地描述一件事实。本表按当前全部成稿重新生成。")
out.append("")
out.append("# 叶子小节字数排序（明确到每一级最小标题）")
out.append("")
out.append("> **叶子小节**＝没有下级 `#` 的最小标题。**章末书目节**（引用/引用文献/参考来源）已剥离，不计入。")
out.append("> 计数口径：正文**汉字数**（CJK），标题到下一标题之间。")
out.append(f"> 全书共 **{n}** 个正文叶子；中位 **{med}** 字，均值 **{mean}** 字，最薄 **{mn}**，最厚 **{mx}**。")
out.append(f"> 标记：`▽薄`＝<{THIN}；`▲厚`＝>{THICK}。")
out.append("")
out.append("## 各章正文字数（已剥离书目）")
out.append("")
out.append("| 章 | 正文汉字 | 正文叶子数 | 叶子中位 | ▽薄 | ▲厚 |")
out.append("|---|---:|---:|---:|---:|---:|")
for name, leaves in per_chapter:
    ws = [x["words"] for x in leaves]
    thin_c = sum(1 for w in ws if w < THIN)
    thick_c = sum(1 for w in ws if w > THICK)
    out.append(f"| {name} | {sum(ws):,} | {len(ws)} | {med_int(ws)} | {thin_c} | {thick_c} |")
out.append(f"| **全书合计** | **{grand:,}** | **{n}** | — | — | — |")
out.append("")

# 最薄/最厚 25，稳定按文档顺序
idxrows = list(enumerate(allrows))  # (docorder, (name, leaf))
thin25 = sorted(idxrows, key=lambda t: (t[1][1]["words"], t[0]))[:25]
thick25 = sorted(idxrows, key=lambda t: (-t[1][1]["words"], t[0]))[:25]

out.append("## 全书最薄 25（最该补厚的）")
out.append("")
out.append("| 字数 | 章 | 路径 | 级 |")
out.append("|---:|---|---|---|")
for _, (name, x) in thin25:
    out.append(f"| {x['words']:,} | {name} | {' › '.join(x['segs'])} | H{x['level']} |")
out.append("")
out.append("## 全书最厚 25（可考虑拆分）")
out.append("")
out.append("| 字数 | 章 | 路径 | 级 |")
out.append("|---:|---|---|---|")
for _, (name, x) in thick25:
    out.append(f"| {x['words']:,} | {name} | {' › '.join(x['segs'])} | H{x['level']} |")
out.append("")

out.append("## 逐章叶子明细（章内按正文顺序）")
out.append("")
for name, leaves in per_chapter:
    ws = [x["words"] for x in leaves]
    out.append(f"### {name}　（正文叶子 {len(ws)} ｜ 正文 {sum(ws):,} 汉字 ｜ 中位 {med_int(ws)}）")
    out.append("")
    out.append("| 字数 | 路径 | 级 | |")
    out.append("|---:|---|---|---|")
    for x in leaves:
        out.append(f"| {x['words']:,} | {' › '.join(x['segs'])} | H{x['level']} | {mark(x['words'])} |")
    out.append("")

text = "\n".join(out) + "\n"  # 末尾保留一行空行，与原表一致
dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "tmp", "leaf_new.md")
open(dest, "w", encoding="utf-8", newline="\n").write(text)
print("written", dest, "bytes", len(text))
