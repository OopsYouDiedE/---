from pathlib import Path
import re



ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "射_二_防卫意识与城市安全.md"
ASSET_DIR = ROOT / "assets" / "chapter-02" / "full-render-v3"
OUT_DIR = ROOT / "output" / "pdf" / "ch02-full-render-v1"
BUILD_DIR = OUT_DIR / "build"
TEX = BUILD_DIR / "ch02-full-render-v1.tex"



FIGURES = [
    ("四色警觉状态", "ch02-01-alertness-manual.png", "四色警觉状态：从无意识到行动状态"),
    ("五维评估速查卡", "ch02-02-threat-assessment-manual.png", "五维评估速查卡：任何一项劣势都优先拉开距离"),
    ("Tueller/现代研究距离", "ch02-03-distance-manual.png", "6.4米行动红线与9.1米有效反应预警线"),
    ("人体正面示意图", "ch02-04-body-targets-manual.png", "徒手拒止目标区域：只用于创造撤离窗口"),
    ("群体协调示意图", "ch02-05-group-coordination-manual.png", "群体协调：干扰、疏散、逼近三类功能"),
    ("Fruin密度分级", "ch02-06-crowd-density-manual.png", "人群密度关键节点：自主性丧失与压力波出现"),
]

CALLOUTS = [
    ("实践建议", "行动", "green"),
    ("结论", "要点", "blue"),
    ("增加距离是最直接有效的防卫手段", "要点", "blue"),
    ("格斗是在所有其他选项已经穷尽之后才考虑的最后手段", "注意", "red"),
    ("中国法律框架", "注意", "red"),
    ("重要限制", "注意", "red"),
    ("关于刀伤的特别医学警告", "注意", "red"),
    ("这一节的前提", "注意", "red"),
    ("密度是可以识别的早期信号", "要点", "blue"),
]



def tex_escape(s: str) -> str:
    s = (
        s.replace("①", "(1)")
        .replace("②", "(2)")
        .replace("③", "(3)")
        .replace("④", "(4)")
        .replace("⑤", "(5)")
    )
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
    s = s.replace("—", "——")
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


def make_figure(filename: str, caption: str) -> str:
    return "\n".join(
        [
            r"\begin{figure}[H]",
            r"  \centering",
            rf"  \includegraphics[width=\linewidth,height=0.35\textheight,keepaspectratio]{{{filename}}}",
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


def render_callout_body(body: str) -> str:
    rendered: list[str] = []
    in_items = False
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            if in_items:
                rendered.append(r"\end{itemize}")
                in_items = False
            rendered.append(r"\vspace{0.12em}")
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


def render_comment(line: str) -> str:
    for key, filename, caption in FIGURES:
        if key in line:
            return make_figure(filename, caption)
    return ""


def collect_following_block(lines: list[str], i: int) -> tuple[str, int]:
    parts = [lines[i].strip()]
    if "实践建议" in lines[i]:
        j = i + 1
        while j < len(lines):
            nxt = lines[j].strip()
            if nxt == "---" or nxt.startswith("#") or nxt.startswith("<!--") or nxt.startswith("|"):
                break
            parts.append(nxt)
            j += 1
        return "\n".join(parts).strip(), j - 1
    j = i + 1
    while j < len(lines) and not lines[j].strip():
        parts.append("")
        j += 1
    while j < len(lines) and (lines[j].strip().startswith("- ") or lines[j].strip().startswith("* ")):
        parts.append(lines[j].strip())
        j += 1
    return "\n".join(parts), j - 1


def render_code_block(lines: list[str]) -> str:
    items = [line.strip() for line in lines if line.strip()]
    body = [r"\Needspace{11\baselineskip}", r"\begin{BookCallout}[colback=greenBack,colframe=greenLine,overlay={\node[CalloutLabel,fill=greenTag] at ([xshift=3.5mm,yshift=-0.4mm]frame.north west) {行动};}]"]
    body.append(r"\begin{enumerate}[leftmargin=2em,itemsep=0.18em,topsep=0.1em]")
    for item in items:
        item = re.sub(r"^\d+\.\s*", "", item)
        body.append(r"\item " + inline_md(item))
    body.extend([r"\end{enumerate}", r"\end{BookCallout}", ""])
    return "\n".join(body)


def convert(markdown: str) -> str:
    out: list[str] = []
    lines = markdown.splitlines()
    i = 0
    in_items = False
    in_code = False
    code_lines: list[str] = []

    while i < len(lines):
        raw = lines[i].rstrip()
        line = raw.strip()

        if line.startswith("```"):
            if in_code:
                out.append(render_code_block(code_lines))
                code_lines = []
                in_code = False
            else:
                if in_items:
                    out.append(r"\end{itemize}")
                    in_items = False
                in_code = True
            i += 1
            continue
        if in_code:
            code_lines.append(line)
            i += 1
            continue

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
            out.append(r"\section*{" + tex_escape(title) + "}")
            if title in {"引用", "参考文献"}:
                out.append(r"\footnotesize\setstretch{1.12}\setlength{\parskip}{0.06em}")
        elif line.startswith("### "):
            out.append(r"\Needspace{7\baselineskip}")
            out.append(r"\subsection*{" + tex_escape(line[4:].strip()) + "}")
        elif line.startswith("#### "):
            out.append(r"\Needspace{5\baselineskip}")
            out.append(r"\BookMinorTitle{" + tex_escape(line[5:].strip()) + "}")
        elif line.startswith("- ") or line.startswith("* "):
            if not in_items:
                out.append(r"\begin{itemize}[leftmargin=2.2em,itemsep=0.18em,topsep=0.2em]")
                in_items = True
            out.append(r"\item " + inline_md(line[2:].strip()))
        elif callout:
            label, color = callout
            body = line
            if re.fullmatch(r"\*\*[^*]+?\*\*[:：]?", line):
                body, i = collect_following_block(lines, i)
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
\setmainfont{Times New Roman}
\setsansfont{Arial}

\definecolor{TitleInk}{HTML}{263238}
\definecolor{BodyInk}{HTML}{242A2D}
\definecolor{CaptionInk}{HTML}{66757B}
\definecolor{RuleInk}{HTML}{C9D0CE}
\definecolor{blueBack}{HTML}{EEF5F8}
\definecolor{blueLine}{HTML}{4E8798}
\definecolor{blueTag}{HTML}{356E7F}
\definecolor{greenBack}{HTML}{F0F7EA}
\definecolor{greenLine}{HTML}{6F9A4B}
\definecolor{greenTag}{HTML}{527B36}
\definecolor{redBack}{HTML}{FFF0ED}
\definecolor{redLine}{HTML}{C76A5A}
\definecolor{redTag}{HTML}{9B4638}

\hypersetup{colorlinks=true, linkcolor=TitleInk, urlcolor=TitleInk}
\graphicspath{{""" + ASSET_DIR.as_posix() + r"""/}}

\setstretch{1.48}
\setlength{\parindent}{2em}
\setlength{\parskip}{0.34em}
\setlength{\tabcolsep}{5pt}
\sloppy

\pagestyle{fancy}
\setlength{\headheight}{14pt}
\fancyhf{}
\fancyhead[L]{\sffamily\small 新六艺}
\fancyhead[R]{\sffamily\small 防卫意识与城市安全}
\fancyfoot[C]{\sffamily\small\thepage}
\renewcommand{\headrulewidth}{0.25pt}
\renewcommand{\footrulewidth}{0pt}

\captionsetup{font={small,sf}, labelformat=empty, textfont={color=CaptionInk}, skip=6pt}

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
  before skip=0.62em,
  after skip=0.62em,
  fontupper=\small,
  #1
}

\newcommand{\BookMinorTitle}[1]{%
  \par\vspace{0.35em}{\sffamily\large\bfseries\color{TitleInk}#1}\par\vspace{0.15em}%
}

\titleformat{\section}{\sffamily\Huge\bfseries\color{TitleInk}}{}{0pt}{}
\titleformat{\subsection}{\sffamily\LARGE\bfseries\color{TitleInk}}{}{0pt}{}
\titlespacing*{\section}{0pt}{0pt}{0.8em}
\titlespacing*{\subsection}{0pt}{1.1em}{0.45em}

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

