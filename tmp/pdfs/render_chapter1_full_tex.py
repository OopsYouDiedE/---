from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "射_一_强健体魄.md"
ASSET_DIR = ROOT / "assets" / "chapter-01" / "full-render-v1"
OUT_DIR = ROOT / "output" / "pdf" / "ch01-full-render-v1"
BUILD_DIR = OUT_DIR / "build"
TEX = BUILD_DIR / "ch01-full-render-v1.tex"


FIGURES = [
    ("三级可用性标准", "ch01-03-three-level-standard-redesign.png", "三级可用性标准：自保、互救、持续有效行动"),
    ("拖拽测试示意图", "ch01-04-rescue-drag-posture.png", "拖拽测试：重心后移，髋部发力，手臂保持连接"),
    ("扶起流程四格", "ch01-05-assisted-stand-up.png", "扶起流程：侧卧、四肢着地、单膝跪、站立"),
    ("热身四阶段流程图", "ch01-06-warmup-flow.png", "训练前热身四阶段"),
    ("弓步加旋转", "ch01-06b-lunge-rotation.png", "弓步加旋转：迈步、手撑地、对侧上伸"),
    ("臀桥动作", "ch01-07-glute-bridge.png", "臀桥：肩、髋、膝形成稳定直线"),
    ("DOMS时间线图", "ch01-08-doms-timeline.png", "延迟性肌肉酸痛的出现、峰值与消退"),
    ("不同运动类型的关节冲击", "ch01-09-joint-impact-comparison-redesign.png", "不同运动类型的关节冲击比较"),
    ("女性深蹲膝关节", "ch01-10-female-squat-alignment.png", "深蹲膝关节对位：避免膝盖内扣"),
    ("深蹲架保护杠", "ch01-11-squat-rack-safety.png", "深蹲架保护杠设置"),
    ("4周训练计划周视图", "", ""),
    ("桌子反向划船", "ch01-13-table-inverted-row.png", "桌子反向划船：身体保持直线"),
    ("深蹲动作对比图", "ch01-14-squat-comparison.png", "深蹲动作对比：正确轨迹与常见错误"),
    ("辅助引体向上", "ch01-15-assisted-pull-up.png", "辅助引体向上：同伴托腿，主动背部发力"),
    ("双人平板击掌", "ch01-16-partner-plank-high-five.png", "双人平板击掌：核心稳定与同步配合"),
    ("伤员拖拽", "ch01-17-casualty-drag.png", "伤员拖拽：锁手、后移重心、腿部蹬地"),
    ("消防员搬运法", "ch01-18-fireman-carry.png", "消防员搬运法：接近、过肩、行进"),
    ("双人前后抬", "ch01-19-two-person-carry.png", "双人前后抬：头端锁手，足端托膝"),
]


CALLOUTS = [
    ("这套标准是长期训练的目标参照", "要点", "blue"),
    ("14岁以下青少年年龄修正", "注意", "red"),
    ("推荐的低冲击起点", "注意", "red"),
    ("初始训练强度", "注意", "red"),
    ("超重人群的进阶节奏", "注意", "red"),
    ("必须立即停训并就医", "注意", "red"),
    ("如果你属于上述情况", "注意", "red"),
    ("保持膝盖与脚尖方向一致", "要点", "blue"),
    ("相对重量原则", "要点", "blue"),
    ("用**空杠**", "注意", "red"),
    ("深蹲失败时的安全脱杠", "注意", "red"),
    ("每次训练都留2—3次余力", "注意", "red"),
    ("独自训练时", "注意", "red"),
    ("入门阶段的强度参照", "要点", "blue"),
    ("动作幅度完整优先于次数", "要点", "blue"),
    ("核心保持稳定是这个动作的关键", "要点", "blue"),
    ("沟通节奏比力量更关键", "要点", "blue"),
    ("团队的成绩，取最后一名到达或完成者的时间", "行动", "green"),
    ("样本任务", "行动", "green"),
]

SPECIAL_CALLOUT_BODIES = {
    "推荐的低冲击起点": "**推荐的低冲击起点：** 体重明显偏高时，先选低冲击运动建立习惯，再逐步过渡到跑步。",
    "超重人群的进阶节奏": "\n".join(
        [
            "**超重人群的进阶节奏：**",
            "- 0—8 周：以步行为主，每次 20—30 分钟，加入低冲击力量训练每周 2 次",
            "- 8—16 周：将总运动时间提升至 150 分钟/周，可引入骑行或游泳",
            "- 16 周后：体重有明显下降时，可以跑走交替方式引入低强度跑步",
        ]
    ),
}


def tex_escape(s: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in s)


def inline_md(s: str) -> str:
    parts = re.split(r"(\*\*.*?\*\*)", s)
    out = []
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            out.append(r"\textbf{" + tex_escape(part[2:-2]) + "}")
        else:
            chunks = re.split(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", part)
            for idx, chunk in enumerate(chunks):
                if idx % 2 == 1:
                    out.append(r"\emph{" + tex_escape(chunk) + "}")
                else:
                    out.append(tex_escape(chunk))
    return "".join(out)


def make_figure(filename: str, caption: str, hero: bool = False) -> str:
    if not filename:
        return ""
    max_h = "0.42\\textheight" if hero else "0.34\\textheight"
    return "\n".join(
        [
            r"\begin{figure}[H]",
            r"  \centering",
            rf"  \includegraphics[width=\linewidth,height={max_h},keepaspectratio]{{{filename}}}",
            rf"  \caption{{{tex_escape(caption)}}}",
            r"\end{figure}",
            "",
        ]
    )


def classify_callout(line: str) -> tuple[str, str] | None:
    for key, label, color in CALLOUTS:
        if key in line:
            return label, color
    return None


def make_callout(label: str, color: str, body: str) -> str:
    return "\n".join(
        [
            r"\Needspace{7\baselineskip}",
            rf"\begin{{BookCallout}}[colback={color}Back,colframe={color}Line,overlay={{\node[CalloutLabel,fill={color}Tag] at ([xshift=3.5mm,yshift=-0.4mm]frame.north west) {{{tex_escape(label)}}};}}]",
            render_callout_body(body),
            r"\end{BookCallout}",
            "",
        ]
    )


def render_callout_body(body: str) -> str:
    rendered: list[str] = []
    in_items = False
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            if in_items:
                rendered.append(r"\end{itemize}")
                in_items = False
            rendered.append(r"\vspace{0.15em}")
        elif line.startswith("- ") or line.startswith("* "):
            if not in_items:
                rendered.append(r"\begin{itemize}[leftmargin=1.8em,itemsep=0.08em,topsep=0.12em]")
                in_items = True
            rendered.append(r"\item " + inline_md(line[2:].strip()))
        else:
            if in_items:
                rendered.append(r"\end{itemize}")
                in_items = False
            rendered.append(inline_md(line))
    if in_items:
        rendered.append(r"\end{itemize}")
    return "\n".join(rendered)


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_separator_row(cells: list[str]) -> bool:
    return all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def render_table(lines: list[str]) -> str:
    rows = [split_table_row(line) for line in lines]
    rows = [row for row in rows if not is_separator_row(row)]
    if not rows:
        return ""
    cols = max(len(row) for row in rows)
    if len(rows) == 8 and rows[0] == ["天", "内容"]:
        return render_week_plan(rows[1:])
    colspec = "".join([r">{\RaggedRight\arraybackslash}X"] * cols)
    body = [
        r"\Needspace{9\baselineskip}",
        r"\begin{table}[H]",
        r"\centering",
        r"\footnotesize",
        r"\renewcommand{\arraystretch}{1.18}",
        rf"\begin{{tabularx}}{{\linewidth}}{{@{{}}{colspec}@{{}}}}",
        r"\toprule",
    ]
    for idx, row in enumerate(rows):
        padded = row + [""] * (cols - len(row))
        cells = [inline_md(cell) for cell in padded]
        if idx == 0:
            cells = [r"\textbf{" + cell + "}" for cell in cells]
        body.append(" & ".join(cells) + r" \\")
        if idx == 0:
            body.append(r"\midrule")
    body.extend([r"\bottomrule", r"\end{tabularx}", r"\end{table}", ""])
    return "\n".join(body)


def render_week_plan(rows: list[list[str]]) -> str:
    body = [
        r"\Needspace{12\baselineskip}",
        r"\begin{table}[H]",
        r"\centering",
        r"\footnotesize",
        r"\renewcommand{\arraystretch}{1.24}",
        r"\begin{tabularx}{\linewidth}{@{}>{\RaggedRight\arraybackslash}p{0.18\linewidth}>{\RaggedRight\arraybackslash}X@{}}",
        r"\toprule",
        r"\textbf{天} & \textbf{内容} \\",
        r"\midrule",
    ]
    for day, content in rows:
        body.append(inline_md(day) + " & " + inline_md(content) + r" \\")
    body.extend(
        [
            r"\bottomrule",
            r"\end{tabularx}",
            r"\end{table}",
            "",
        ]
    )
    return "\n".join(
        body
    )


def render_comment(line: str) -> str:
    for key, filename, caption in FIGURES:
        if key in line:
            return make_figure(filename, caption)
    return ""


def convert(markdown: str) -> str:
    out: list[str] = []
    lines = markdown.splitlines()
    i = 0
    in_items = False
    while i < len(lines):
        raw = lines[i].rstrip()
        line = raw.strip()

        if line.startswith("|") and "|" in line[1:]:
            if in_items:
                out.append(r"\end{itemize}")
                in_items = False
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].rstrip())
                i += 1
            out.append(render_table(table_lines))
            continue

        if in_items and not (line.startswith("- ") or line.startswith("* ")):
            out.append(r"\end{itemize}")
            in_items = False

        callout = classify_callout(line)

        if not line:
            out.append("")
        elif line.startswith("<!-- [配图]"):
            out.append(render_comment(line))
        elif line == "---":
            out.append(r"\vspace{0.35em}\noindent\textcolor{RuleInk}{\rule{\linewidth}{0.35pt}}\vspace{0.35em}")
        elif line.startswith("## "):
            title = line[3:].strip()
            if title.startswith("一、"):
                out.append(r"\section*{" + tex_escape(title) + "}")
                out.append(make_figure("ch01-01-hero-flood.png", "第一章主图：城市洪水中的互助与体能可用性", hero=True))
            elif title in {"引用", "参考文献"}:
                out.append(r"\section*{" + tex_escape(title) + "}")
                out.append(r"\footnotesize\setstretch{1.12}\setlength{\parskip}{0.06em}")
            else:
                out.append(r"\section*{" + tex_escape(title) + "}")
        elif line.startswith("### "):
            out.append(r"\Needspace{6\baselineskip}")
            out.append(r"\subsection*{" + tex_escape(line[4:].strip()) + "}")
        elif line.startswith("#### "):
            out.append(r"\Needspace{5\baselineskip}")
            out.append(r"\BookMinorTitle{" + tex_escape(line[5:].strip()) + "}")
            if "班组挑战" in line:
                out.append(make_figure("ch01-20-team-challenge.png", "班组挑战：按最后一名完成计时"))
        elif line.startswith("- ") or line.startswith("* "):
            if not in_items:
                out.append(r"\begin{itemize}[leftmargin=2.2em,itemsep=0.18em,topsep=0.2em]")
                in_items = True
            out.append(r"\item " + inline_md(line[2:].strip()))
        elif callout:
            label, color = callout
            body = line
            for key, special_body in SPECIAL_CALLOUT_BODIES.items():
                if key in line:
                    body = special_body
                    break
            if re.fullmatch(r"\*\*[^*]+?\*\*[:：]?", line) and i + 1 < len(lines):
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                nxt = lines[j].strip() if j < len(lines) else ""
                if nxt and not (
                    nxt.startswith("#")
                    or nxt.startswith("|")
                    or nxt.startswith("<!--")
                    or nxt == "---"
                    or nxt.startswith("- ")
                    or nxt.startswith("* ")
                ):
                    parts = [line, "", nxt]
                    j += 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    while j < len(lines) and (lines[j].strip().startswith("- ") or lines[j].strip().startswith("* ")):
                        parts.append(lines[j].strip())
                        j += 1
                    body = "\n".join(parts)
                    i = j - 1
                elif any(key in line for key in SPECIAL_CALLOUT_BODIES):
                    while j < len(lines) and (not lines[j].strip() or lines[j].strip().startswith("- ") or lines[j].strip().startswith("* ")):
                        i = j
                        j += 1
            out.append(make_callout(label, color, body))
        elif re.fullmatch(r"\*\*[^*]+?\*\*[:：]?", line):
            out.append(r"\Needspace{4\baselineskip}")
            out.append(r"\BookMinorTitle{" + tex_escape(line.strip("*：:")) + "}")
        else:
            out.append(inline_md(line))
        i += 1
    if in_items:
        out.append(r"\end{itemize}")
    return "\n".join(out)


PREAMBLE = r"""\documentclass[UTF8,zihao=-4,oneside]{ctexart}

\usepackage[a4paper,left=22mm,right=22mm,top=22mm,bottom=22mm]{geometry}
\usepackage{fontspec}
\usepackage{graphicx}
\usepackage{float}
\usepackage{caption}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{array}
\usepackage{ragged2e}
\usepackage{xcolor}
\usepackage{setspace}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage{hyperref}
\usepackage{xurl}
\usepackage[most]{tcolorbox}
\usepackage{needspace}

\setCJKmainfont{Noto Serif SC}[AutoFakeBold=2]
\setCJKsansfont{Noto Sans SC}[AutoFakeBold=2]
\setmainfont{Noto Serif SC}[AutoFakeBold=2]
\setsansfont{Noto Sans SC}[AutoFakeBold=2]

\definecolor{TitleInk}{HTML}{263238}
\definecolor{BodyInk}{HTML}{242A2D}
\definecolor{CaptionInk}{HTML}{66757B}
\definecolor{RuleInk}{HTML}{C9D0CE}
\definecolor{blueBack}{HTML}{EEF5F8}
\definecolor{blueLine}{HTML}{4E8798}
\definecolor{blueTag}{HTML}{356E7F}
\definecolor{tealBack}{HTML}{EEF7F3}
\definecolor{tealLine}{HTML}{4D9A82}
\definecolor{tealTag}{HTML}{337A66}
\definecolor{greenBack}{HTML}{F0F7EA}
\definecolor{greenLine}{HTML}{6F9A4B}
\definecolor{greenTag}{HTML}{527B36}
\definecolor{amberBack}{HTML}{FFF7E6}
\definecolor{amberLine}{HTML}{D79B33}
\definecolor{amberTag}{HTML}{A36F17}
\definecolor{redBack}{HTML}{FFF0ED}
\definecolor{redLine}{HTML}{C76A5A}
\definecolor{redTag}{HTML}{9B4638}

\hypersetup{
  colorlinks=true,
  linkcolor=TitleInk,
  urlcolor=TitleInk
}

\graphicspath{{""" + ASSET_DIR.as_posix() + r"""/}}

\setstretch{1.50}
\setlength{\parindent}{2em}
\setlength{\parskip}{0.38em}
\setlength{\tabcolsep}{5pt}
\sloppy

\pagestyle{fancy}
\setlength{\headheight}{14pt}
\fancyhf{}
\fancyhead[L]{\sffamily\small 新六艺}
\fancyhead[R]{\sffamily\small 强健体魄}
\fancyfoot[C]{\sffamily\small\thepage}
\renewcommand{\headrulewidth}{0.25pt}
\renewcommand{\footrulewidth}{0pt}

\captionsetup{
  font={small,sf},
  labelformat=empty,
  textfont={color=CaptionInk},
  skip=6pt
}

\tikzset{
  CalloutLabel/.style={
    anchor=north west,
    font=\sffamily\bfseries\footnotesize,
    text=white,
    rounded corners=1pt,
    inner xsep=5pt,
    inner ysep=2.5pt
  }
}

\newtcolorbox{BookCallout}[1][]{
  enhanced,
  sharp corners,
  boxrule=0.7pt,
  leftrule=2.4pt,
  left=4mm,
  right=4mm,
  top=5.5mm,
  bottom=3mm,
  before skip=0.65em,
  after skip=0.65em,
  fontupper=\small,
  #1
}

\newcommand{\BookMinorTitle}[1]{%
  \par\vspace{0.35em}{\sffamily\large\bfseries\color{TitleInk}#1}\par\vspace{0.15em}%
}

\newtcolorbox{PlanDay}[2]{
  enhanced,
  sharp corners,
  boxrule=0.55pt,
  colback=#1!10,
  colframe=#1,
  width=\linewidth,
  left=1mm,
  right=1mm,
  top=1.2mm,
  bottom=1.2mm,
  before skip=0pt,
  after skip=0pt,
  fontupper=\scriptsize\sffamily,
  overlay={\node[anchor=north west,font=\sffamily\bfseries\scriptsize,text=#1] at ([xshift=1.2mm,yshift=-1.2mm]frame.north west) {#2};}
}

\definecolor{PlanStrength}{HTML}{4E8798}
\definecolor{PlanCardio}{HTML}{6F9A4B}
\definecolor{PlanRecover}{HTML}{D79B33}
\definecolor{PlanRest}{HTML}{8A8F93}

\titleformat{\section}
  {\sffamily\Huge\bfseries\color{TitleInk}}
  {}{0pt}{}
\titleformat{\subsection}
  {\sffamily\LARGE\bfseries\color{TitleInk}}
  {}{0pt}{}
\titleformat{\subsubsection}
  {\sffamily\large\bfseries\color{TitleInk}}
  {}{0pt}{}
\titlespacing*{\section}{0pt}{0pt}{0.8em}
\titlespacing*{\subsection}{0pt}{1.1em}{0.45em}
\titlespacing*{\subsubsection}{0pt}{0.85em}{0.25em}

\begin{document}
\color{BodyInk}
"""

POSTAMBLE = "\n\\end{document}\n"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    markdown = SRC.read_text(encoding="utf-8")
    TEX.write_text(PREAMBLE + convert(markdown) + POSTAMBLE, encoding="utf-8")
    print(TEX)


if __name__ == "__main__":
    main()
