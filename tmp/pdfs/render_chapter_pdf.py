from __future__ import annotations

import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[2]
FONT_REGULAR = Path(r"C:\Windows\Fonts\NotoSerifSC-VF.ttf")
FONT_SANS = Path(r"C:\Windows\Fonts\NotoSansSC-VF.ttf")


def register_fonts() -> tuple[str, str]:
    body_font = "NotoSerifSC"
    sans_font = "NotoSansSC"
    pdfmetrics.registerFont(TTFont(body_font, str(FONT_REGULAR)))
    pdfmetrics.registerFont(TTFont(sans_font, str(FONT_SANS)))
    return body_font, sans_font


def clean_inline(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)
    text = re.sub(r"`([^`]+)`", r"<font name='NotoSansSC'>\1</font>", text)
    text = text.replace("&", "&amp;").replace("<b>", "<b>").replace("</b>", "</b>")
    text = text.replace("<i>", "<i>").replace("</i>", "</i>")
    text = text.replace("<font name='NotoSansSC'>", "<font name='NotoSansSC'>").replace("</font>", "</font>")
    return text


def paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(clean_inline(text), style)


def image_flowable(md_path: Path, alt: str, rel: str, max_width: float):
    img_path = (md_path.parent / rel).resolve()
    if not img_path.exists():
        img_path = (ROOT / rel).resolve()
    img = Image(str(img_path))
    ratio = img.imageHeight / float(img.imageWidth)
    width = max_width
    height = width * ratio
    if height > 145 * mm:
        height = 145 * mm
        width = height / ratio
    caption_style = STYLES["caption"]
    return KeepTogether(
        [
            Spacer(1, 4 * mm),
            Image(str(img_path), width=width, height=height),
            Paragraph(clean_inline(alt), caption_style),
            Spacer(1, 5 * mm),
        ]
    )


def parse_table(lines: list[str], start: int, table_style: ParagraphStyle):
    rows = []
    i = start
    while i < len(lines) and lines[i].strip().startswith("|"):
        raw = lines[i].strip().strip("|")
        cells = [cell.strip() for cell in raw.split("|")]
        if not all(re.fullmatch(r":?-{2,}:?", cell) for cell in cells):
            rows.append([paragraph(cell, table_style) for cell in cells])
        i += 1
    return rows, i


def build_story(md_path: Path, max_width: float):
    lines = md_path.read_text(encoding="utf-8").splitlines()
    story = []
    para_buf: list[str] = []
    i = 0

    def flush_para():
        nonlocal para_buf
        text = " ".join(x.strip() for x in para_buf).strip()
        if text:
            story.append(paragraph(text, STYLES["body"]))
            story.append(Spacer(1, 2.5 * mm))
        para_buf = []

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped or stripped == "---":
            flush_para()
            if stripped == "---":
                story.append(Spacer(1, 5 * mm))
            i += 1
            continue

        image_match = re.match(r"!\[(.*?)\]\((.*?)\)", stripped)
        if image_match:
            flush_para()
            story.append(image_flowable(md_path, image_match.group(1), image_match.group(2), max_width))
            i += 1
            continue

        if stripped.startswith("<!--"):
            i += 1
            continue

        if stripped.startswith("#"):
            flush_para()
            level = len(stripped) - len(stripped.lstrip("#"))
            title = stripped[level:].strip()
            style = STYLES.get(f"h{level}", STYLES["h4"])
            if level <= 2 and story:
                story.append(PageBreak())
            story.append(paragraph(title, style))
            story.append(Spacer(1, 3 * mm))
            i += 1
            continue

        if stripped.startswith("|"):
            flush_para()
            rows, i = parse_table(lines, i, STYLES["table"])
            if rows:
                table = Table(rows, repeatRows=1)
                table.setStyle(
                    TableStyle(
                        [
                            ("FONTNAME", (0, 0), (-1, -1), "NotoSansSC"),
                            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEF3F5")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#263238")),
                            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B8C2C7")),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 4),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                            ("TOPPADDING", (0, 0), (-1, -1), 4),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ]
                    )
                )
                story.append(table)
                story.append(Spacer(1, 4 * mm))
            continue

        if stripped.startswith("- "):
            flush_para()
            story.append(paragraph("• " + stripped[2:].strip(), STYLES["body"]))
            story.append(Spacer(1, 1.5 * mm))
            i += 1
            continue

        para_buf.append(stripped)
        i += 1

    flush_para()
    return story


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("NotoSansSC", 8)
    canvas.setFillColor(colors.HexColor("#69777D"))
    canvas.drawCentredString(A4[0] / 2, 10 * mm, str(doc.page))
    canvas.restoreState()


BODY_FONT, SANS_FONT = register_fonts()
BASE = getSampleStyleSheet()
STYLES = {
    "body": ParagraphStyle(
        "body",
        parent=BASE["BodyText"],
        fontName=BODY_FONT,
        fontSize=10.2,
        leading=17,
        firstLineIndent=10,
        alignment=TA_LEFT,
        wordWrap="CJK",
        spaceAfter=1.5,
    ),
    "h2": ParagraphStyle(
        "h2",
        parent=BASE["Heading1"],
        fontName=SANS_FONT,
        fontSize=22,
        leading=30,
        textColor=colors.HexColor("#18252B"),
        wordWrap="CJK",
    ),
    "h3": ParagraphStyle(
        "h3",
        parent=BASE["Heading2"],
        fontName=SANS_FONT,
        fontSize=16,
        leading=23,
        textColor=colors.HexColor("#263238"),
        spaceBefore=5,
        wordWrap="CJK",
    ),
    "h4": ParagraphStyle(
        "h4",
        parent=BASE["Heading3"],
        fontName=SANS_FONT,
        fontSize=12.5,
        leading=18,
        textColor=colors.HexColor("#31444C"),
        spaceBefore=4,
        wordWrap="CJK",
    ),
    "caption": ParagraphStyle(
        "caption",
        parent=BASE["BodyText"],
        fontName=SANS_FONT,
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#5C6B72"),
        alignment=TA_CENTER,
        wordWrap="CJK",
        spaceBefore=2,
    ),
    "table": ParagraphStyle(
        "table",
        parent=BASE["BodyText"],
        fontName=SANS_FONT,
        fontSize=8,
        leading=11,
        wordWrap="CJK",
    ),
}


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: render_chapter_pdf.py input.md output.pdf")
        return 2
    input_md = Path(sys.argv[1]).resolve()
    output_pdf = Path(sys.argv[2]).resolve()
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_pdf),
        pagesize=A4,
        leftMargin=22 * mm,
        rightMargin=22 * mm,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        title=input_md.stem,
        author="新六艺",
    )
    story = build_story(input_md, doc.width)
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(output_pdf)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
