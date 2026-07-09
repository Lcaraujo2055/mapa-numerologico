# -*- coding: utf-8 -*-
"""
Geração do PDF do Mapa Numerológico — visual profissional (letterhead),
compactado para caber em UMA página A4.

Depende apenas do ReportLab (não importa GUI).
"""
import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table as RLTable, TableStyle,
    KeepTogether, PageBreak,
)

from core import LIMIAR_EXCESSO
from interpretations import analise_completa

# --------------------------------------------------------------- Paleta --
NAVY = colors.HexColor("#1E2A44")
NAVY_LIGHT = colors.HexColor("#2E3E5C")
GOLD = colors.HexColor("#B8912F")
GOLD_SOFT = colors.HexColor("#F3E9D2")
INK = colors.HexColor("#232323")
GRAY_TEXT = colors.HexColor("#6B6B6B")
ROW_ALT = colors.HexColor("#F3F4F7")
LINE_GRAY = colors.HexColor("#D9DCE1")
WHITE = colors.white

PAGE_W, PAGE_H = A4
HEADER_H = 25 * mm
FOOTER_H = 12 * mm
MARGIN = 14
CONTENT_W = PAGE_W - 2 * MARGIN


def _draw_header_footer(nome, data):
    """Retorna uma função onPage(canvas, doc) que desenha o cabeçalho
    (faixa colorida com título) e o rodapé (linha + timestamp + paginação)."""

    def _on_page(canvas, doc):
        canvas.saveState()

        # ---- Faixa superior (letterhead) ----
        canvas.setFillColor(NAVY)
        canvas.rect(0, PAGE_H - HEADER_H, PAGE_W, HEADER_H, stroke=0, fill=1)

        # linha de destaque dourada sob a faixa
        canvas.setFillColor(GOLD)
        canvas.rect(0, PAGE_H - HEADER_H - 1.6, PAGE_W, 1.6, stroke=0, fill=1)

        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica-Bold", 15)
        canvas.drawString(MARGIN, PAGE_H - 11 * mm, "MAPA NUMEROLÓGICO")

        canvas.setFont("Helvetica", 8.3)
        canvas.setFillColor(colors.HexColor("#D8DEEA"))
        canvas.drawString(MARGIN, PAGE_H - 16.3 * mm, "Relatório pessoal de análise numerológica")

        # nome + data alinhados à direita na faixa
        canvas.setFont("Helvetica-Bold", 9.5)
        canvas.setFillColor(WHITE)
        canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 10.4 * mm, nome or "-")
        canvas.setFont("Helvetica", 8.3)
        canvas.setFillColor(colors.HexColor("#D8DEEA"))
        canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 15.2 * mm, f"Nascimento: {data or '-'}")

        # ---- Rodapé ----
        canvas.setStrokeColor(LINE_GRAY)
        canvas.setLineWidth(0.6)
        canvas.line(MARGIN, FOOTER_H, PAGE_W - MARGIN, FOOTER_H)

        canvas.setFont("Helvetica", 7.3)
        canvas.setFillColor(GRAY_TEXT)
        emissao = datetime.now().strftime("%d/%m/%Y %H:%M")
        canvas.drawString(MARGIN, FOOTER_H - 5.5 * mm, f"Emitido em {emissao}")
        canvas.drawCentredString(PAGE_W / 2, FOOTER_H - 5.5 * mm, "Mapa Numerológico — Documento gerado automaticamente")
        canvas.drawRightString(PAGE_W - MARGIN, FOOTER_H - 5.5 * mm, f"Página {doc.page}")

        canvas.restoreState()

    return _on_page


def _section_title(text, styles):
    """Título de seção com barra dourada à esquerda (via tabela 1x1)."""
    bar = RLTable([[Paragraph(text, styles["SectionText"])]], colWidths=[CONTENT_W])
    bar.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEBEFORE", (0, 0), (0, 0), 2.6, GOLD),
        ("BACKGROUND", (0, 0), (-1, -1), GOLD_SOFT),
    ]))
    return bar


def _base_table_style(header_bg=NAVY, header_fg=WHITE, font_size=8.6,
                       zebra=True, align="CENTER"):
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("TEXTCOLOR", (0, 0), (-1, 0), header_fg),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("ALIGN", (0, 0), (-1, -1), align),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, header_bg),
        ("LINEBELOW", (0, 1), (-1, -2), 0.4, LINE_GRAY),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    if zebra:
        style.append(("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, ROW_ALT]))
    return TableStyle(style)


def _stylesheet():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="SectionText", fontSize=10.2, leading=12,
        textColor=NAVY, fontName="Helvetica-Bold", alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="Body", fontSize=9, leading=12, textColor=INK,
    ))
    styles.add(ParagraphStyle(
        name="CardLabel", fontSize=8.2, leading=10, alignment=TA_CENTER,
        textColor=colors.HexColor("#E7ECF5"),
    ))
    styles.add(ParagraphStyle(
        name="CardValue", fontSize=19, leading=21, alignment=TA_CENTER,
        textColor=GOLD, fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        name="AnaliseTitulo", fontSize=15, leading=18, textColor=NAVY,
        fontName="Helvetica-Bold", spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="AnaliseDisclaimer", fontSize=8, leading=11,
        textColor=GRAY_TEXT, fontName="Helvetica-Oblique", spaceAfter=10,
    ))
    styles.add(ParagraphStyle(
        name="AnaliseSubtitulo", fontSize=10.5, leading=13, textColor=NAVY,
        fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="AnaliseBody", fontSize=9.3, leading=13, textColor=INK,
        alignment=TA_JUSTIFY, spaceAfter=6,
    ))
    return styles


def _numero_cards(r, styles):
    """Linha de cartões destacando os Números Fundamentais."""
    itens = [
        ("Interior", r["Interior"]),
        ("Exterior", r["Exterior"]),
        ("Síntese", r["Síntese"]),
        ("Caminho", r["Caminho"]),
        ("Quinta", r["Quinta"]),
        ("Karma", r["Soma"]),
    ]
    col_w = CONTENT_W / len(itens)
    cell = []
    for label, valor in itens:
        mini = RLTable(
            [[Paragraph(label.upper(), styles["CardLabel"])],
             [Paragraph(str(valor), styles["CardValue"])]],
            colWidths=[col_w - 4],
        )
        mini.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), NAVY),
            ("TOPPADDING", (0, 0), (0, 0), 5),
            ("BOTTOMPADDING", (0, 0), (0, 0), 1),
            ("TOPPADDING", (0, 1), (0, 1), 0),
            ("BOTTOMPADDING", (0, 1), (0, 1), 6),
            ("LINEBELOW", (0, 0), (0, 0), 1, GOLD),
        ]))
        cell.append(mini)
    row = RLTable([cell], colWidths=[col_w] * len(itens))
    row.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return row


def gerar_pdf(nome: str, data: str, r: dict, pasta_destino: str) -> str:
    os.makedirs(pasta_destino, exist_ok=True)
    safe_nome = "".join(
        ch for ch in nome if ch.isalnum() or ch in (" ", "_", "-")
    ).strip().replace(" ", "_") or "Mapa"
    agora = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho = os.path.join(pasta_destino, f"Mapa_Numerologico_{safe_nome}_{agora}.pdf")

    doc = SimpleDocTemplate(
        caminho,
        pagesize=A4,
        rightMargin=MARGIN,
        leftMargin=MARGIN,
        topMargin=HEADER_H + 6,
        bottomMargin=FOOTER_H + 6,
        title=f"Mapa Numerológico - {nome}",
        author="Mapa Numerológico",
    )

    styles = _stylesheet()
    story = []

    # Cartões dos números fundamentais
    story.append(_numero_cards(r, styles))
    story.append(Spacer(1, 8))

    # Vocação + Desafios
    story.append(_section_title("Vocação e Desafios", styles))
    story.append(Spacer(1, 3))
    voc = r["Vocacao"]
    des = r["Desafios"]
    vd = [
        ["Vocação", "", "Desafios", ""],
        ["Dia", str(voc["Dia do Nascimento"]), "1º", str(des["1º"])],
        ["Síntese", str(voc["Síntese"]), "2º", str(des["2º"])],
        ["Caminho", str(voc["Caminho da Vida"]), "3º", str(des["3º"])],
        ["", "", "4º", str(des["4º"])],
    ]
    vt = RLTable(vd, colWidths=[CONTENT_W * 0.30, CONTENT_W * 0.20, CONTENT_W * 0.30, CONTENT_W * 0.20])
    vt.setStyle(_base_table_style())
    story.append(vt)
    story.append(Spacer(1, 8))

    # Tabela numérica + Temperamentos + Ausentes/Excessos lado a lado
    story.append(_section_title("Tabela Numérica, Temperamentos e Observações", styles))
    story.append(Spacer(1, 3))

    tn = [["Nº", "Qtd", "Somatório"]] + [[str(a), str(b), str(c)] for a, b, c in r["TabelaRows"]]
    tn.append(["TOTAL", str(r["TotalLetras"]), str(r["TotalNome"])])
    tnt = RLTable(tn, colWidths=[CONTENT_W * 0.34 / 3] * 3)
    tnt_style = _base_table_style(font_size=8.4)
    tnt_style.add("FONT", (0, -1), (-1, -1), "Helvetica-Bold")
    tnt_style.add("BACKGROUND", (0, -1), (-1, -1), GOLD_SOFT)
    tnt.setStyle(tnt_style)

    e = r["Eixos"]
    eixos_rows = [["Temperamento", "Valor"]]
    for k, v in e.items():
        eixos_rows.append([k.replace("Eixo ", ""), str(v)])
    et = RLTable(eixos_rows, colWidths=[CONTENT_W * 0.44, CONTENT_W * 0.22])
    et_style = _base_table_style(font_size=8.4, align="LEFT")
    et_style.add("ALIGN", (1, 0), (1, -1), "CENTER")
    et.setStyle(et_style)

    aus = ", ".join(map(str, r["Ausentes"])) if r["Ausentes"] else "Nenhum"
    exc = ", ".join(map(str, r["Excessos"])) if r["Excessos"] else "Nenhum"
    ax = RLTable(
        [["Ausentes", aus], [f"Excessos (≥{LIMIAR_EXCESSO})", exc]],
        colWidths=[CONTENT_W * 0.30, CONTENT_W * 0.36],
    )
    ax_style = TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, LINE_GRAY),
        ("FONTSIZE", (0, 0), (-1, -1), 8.2),
        ("FONT", (0, 0), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (0, -1), NAVY),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ALIGN", (1, 0), (1, -1), "LEFT"),
        ("BACKGROUND", (0, 0), (0, -1), GOLD_SOFT),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ])
    ax.setStyle(ax_style)

    right_stack = RLTable([[et], [Spacer(1, 5)], [ax]], colWidths=[CONTENT_W * 0.66])
    right_stack.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    bottom = RLTable([[tnt, right_stack]], colWidths=[CONTENT_W * 0.34, CONTENT_W * 0.66])
    bottom.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 10),
        ("LEFTPADDING", (1, 0), (1, 0), 0),
        ("RIGHTPADDING", (1, 0), (1, 0), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(bottom)

    # ---- Página(s) seguintes: Análise Interpretativa completa ----
    analise_story = [PageBreak()]
    analise_story.append(Paragraph("Análise Interpretativa", styles["AnaliseTitulo"]))
    analise_story.append(Paragraph(
        "Leitura simbólica baseada na tradição numerológica, pensada como ferramenta "
        "de autorreflexão — não como diagnóstico, previsão ou afirmação factual.",
        styles["AnaliseDisclaimer"],
    ))
    for titulo_secao, paragrafos in analise_completa(nome, r):
        analise_story.append(Paragraph(titulo_secao, styles["AnaliseSubtitulo"]))
        for p in paragrafos:
            analise_story.append(Paragraph(p, styles["AnaliseBody"]))

    full_story = [KeepTogether(story)] + analise_story

    doc.build(
        full_story,
        onFirstPage=_draw_header_footer(nome, data),
        onLaterPages=_draw_header_footer(nome, data),
    )
    return caminho
