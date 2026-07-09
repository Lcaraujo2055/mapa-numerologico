# -*- coding: utf-8 -*-
"""
Geração do PDF do Mapa Numerológico — versão Android, usando fpdf2.

Por que fpdf2 e não reportlab aqui: o python-for-android tem uma "receita"
própria para reportlab que baixa uma versão antiga travada (ignorando
qualquer versão pedida no buildozer.spec) e essa versão antiga não compila
no Android (usa uma API interna do CPython que mudou a partir do Python
3.11). O fpdf2 é 100% Python puro — sem nenhum código C — então não sofre
desse problema.

Mesma assinatura de função que a versão desktop (`gerar_pdf(nome, data, r,
pasta_destino) -> caminho`), para que main.py não precise de nenhuma
alteração.
"""
import os
from datetime import datetime

from fpdf import FPDF

from core import LIMIAR_EXCESSO
from interpretations import analise_completa

# --------------------------------------------------------------- Paleta --
NAVY = (30, 42, 68)
GOLD = (184, 145, 47)
GOLD_SOFT = (243, 233, 210)
INK = (35, 35, 35)
GRAY_TEXT = (107, 107, 107)
ROW_ALT = (243, 244, 247)
LINE_GRAY = (217, 220, 225)
WHITE = (255, 255, 255)

PAGE_W = 210  # A4 em mm
MARGIN = 14
HEADER_H = 26
FOOTER_Y = 283


def _safe(s):
    """Remove caracteres fora do Latin-1 (fonte núcleo do PDF só suporta
    esse conjunto), trocando os mais comuns por equivalentes simples e
    descartando qualquer outro em vez de travar a geração do PDF."""
    if s is None:
        return ""
    s = str(s)
    s = (s.replace("\u2014", "-").replace("\u2013", "-")
           .replace("\u2265", ">=").replace("\u2264", "<=")
           .replace("\u2019", "'").replace("\u2018", "'")
           .replace("\u201c", '"').replace("\u201d", '"'))
    return s.encode("latin-1", errors="replace").decode("latin-1")


class _PDF(FPDF):
    def __init__(self, nome, data, *args, **kwargs):
        self._nome = _safe(nome)
        self._data_nasc = _safe(data)
        super().__init__(*args, **kwargs)
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(MARGIN, HEADER_H + 6, MARGIN)

    def header(self):
        self.set_fill_color(*NAVY)
        self.rect(0, 0, PAGE_W, HEADER_H, style="F")
        self.set_fill_color(*GOLD)
        self.rect(0, HEADER_H, PAGE_W, 1.2, style="F")

        self.set_xy(MARGIN, 6)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 15)
        self.cell(120, 8, _safe("MAPA NUMEROLOGICO"))

        self.set_xy(MARGIN, 15)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(216, 222, 234)
        self.cell(120, 6, _safe("Relatorio pessoal de analise numerologica"))

        self.set_xy(PAGE_W - MARGIN - 90, 6)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 10)
        self.cell(90, 8, self._nome, align="R")

        self.set_xy(PAGE_W - MARGIN - 90, 15)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(216, 222, 234)
        self.cell(90, 6, _safe(f"Nascimento: {self._data_nasc}"), align="R")

        self.set_y(HEADER_H + 6)

    def footer(self):
        self.set_y(-16)
        self.set_draw_color(*LINE_GRAY)
        self.line(MARGIN, self.get_y(), PAGE_W - MARGIN, self.get_y())
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(*GRAY_TEXT)
        emissao = _safe(datetime.now().strftime("%d/%m/%Y %H:%M"))
        self.set_xy(MARGIN, self.get_y() + 2)
        self.cell(60, 5, f"Emitido em {emissao}")
        self.set_xy(PAGE_W - MARGIN - 60, self.get_y())
        self.cell(60, 5, _safe(f"Pagina {self.page_no()}"), align="R")

    # ----------------------------------------------------------- Ajudas --
    def section_title(self, texto):
        self.ln(3)
        self.set_fill_color(*GOLD_SOFT)
        self.set_text_color(*NAVY)
        self.set_font("Helvetica", "B", 11)
        y0 = self.get_y()
        self.cell(0, 8, "  " + _safe(texto), fill=True)
        self.ln(8)
        self.set_draw_color(*GOLD)
        self.set_line_width(1)
        self.line(MARGIN, y0, MARGIN, y0 + 8)
        self.set_line_width(0.2)
        self.ln(1)

    def label_value_row(self, label, value, col_w=None):
        col_w = col_w or (PAGE_W - 2 * MARGIN) / 2
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*GRAY_TEXT)
        self.cell(col_w * 0.5, 6, _safe(label))
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*INK)
        self.cell(col_w * 0.5, 6, _safe(value))
        self.ln(6)

    def paragraph(self, texto):
        self.set_font("Helvetica", "", 9.3)
        self.set_text_color(*INK)
        self.multi_cell(0, 5.2, _safe(texto), align="J")
        self.ln(1.5)


def _numero_cards(pdf, itens):
    """Linha de 'cartões' navy/dourado com os números fundamentais."""
    content_w = PAGE_W - 2 * MARGIN
    n = len(itens)
    gap = 2
    card_w = (content_w - gap * (n - 1)) / n
    card_h = 20
    x0 = MARGIN
    y0 = pdf.get_y()
    for label, valor in itens:
        pdf.set_fill_color(*NAVY)
        pdf.rect(x0, y0, card_w, card_h, style="F")
        pdf.set_xy(x0, y0 + 3)
        pdf.set_font("Helvetica", "", 7.3)
        pdf.set_text_color(231, 236, 245)
        pdf.cell(card_w, 4, _safe(label.upper()), align="C")
        pdf.set_xy(x0, y0 + 9)
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(*GOLD)
        pdf.cell(card_w, 8, _safe(valor), align="C")
        x0 += card_w + gap
    pdf.set_xy(MARGIN, y0 + card_h + 4)


def _tabela_numerica(pdf, rows, total_letras, total_nome):
    content_w = PAGE_W - 2 * MARGIN
    col_w = content_w / 3
    row_h = 6.5

    pdf.set_fill_color(*NAVY)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    for h in ("Numero", "Qtd", "Somatorio"):
        pdf.cell(col_w, row_h, _safe(h), fill=True, align="C")
    pdf.ln(row_h)

    pdf.set_font("Helvetica", "", 9)
    for i, (n, qtd, soma) in enumerate(rows):
        bg = WHITE if i % 2 == 0 else ROW_ALT
        pdf.set_fill_color(*bg)
        pdf.set_text_color(*INK)
        for val in (n, qtd, soma):
            pdf.cell(col_w, row_h, _safe(val), fill=True, align="C")
        pdf.ln(row_h)

    pdf.set_fill_color(*GOLD_SOFT)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*INK)
    for val in ("TOTAL", total_letras, total_nome):
        pdf.cell(col_w, row_h, _safe(val), fill=True, align="C")
    pdf.ln(row_h + 3)


def gerar_pdf(nome: str, data: str, r: dict, pasta_destino: str) -> str:
    os.makedirs(pasta_destino, exist_ok=True)
    safe_nome = "".join(
        ch for ch in nome if ch.isalnum() or ch in (" ", "_", "-")
    ).strip().replace(" ", "_") or "Mapa"
    agora = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho = os.path.join(pasta_destino, f"Mapa_Numerologico_{safe_nome}_{agora}.pdf")

    pdf = _PDF(nome, data, orientation="P", unit="mm", format="A4")
    pdf.add_page()

    # ---- Números fundamentais ----
    itens = [
        ("Interior", r["Interior"]), ("Exterior", r["Exterior"]),
        ("Sintese", r["Síntese"]), ("Caminho", r["Caminho"]),
        ("Quinta", r["Quinta"]), ("Karma", r["Soma"]),
    ]
    _numero_cards(pdf, itens)

    # ---- Vocação e Desafios ----
    pdf.section_title("Vocacao e Desafios")
    voc = r["Vocacao"]
    des = r["Desafios"]
    col_w = (PAGE_W - 2 * MARGIN) / 2
    y_start = pdf.get_y()
    pdf.label_value_row("Dia:", voc["Dia do Nascimento"], col_w)
    pdf.label_value_row("Sintese:", voc["Síntese"], col_w)
    pdf.label_value_row("Caminho:", voc["Caminho da Vida"], col_w)
    y_after_voc = pdf.get_y()

    pdf.set_xy(MARGIN + col_w, y_start)
    for pos in ("1º", "2º", "3º", "4º"):
        pdf.set_x(MARGIN + col_w)
        pdf.label_value_row(f"{pos}:", des[pos], col_w)
    pdf.set_y(max(y_after_voc, pdf.get_y()))

    # ---- Tabela numérica ----
    pdf.section_title("Tabela Numerica do Nome")
    _tabela_numerica(pdf, r["TabelaRows"], r["TotalLetras"], r["TotalNome"])

    # ---- Temperamentos ----
    pdf.section_title("Temperamentos")
    e = r["Eixos"]
    for k, v in e.items():
        pdf.label_value_row(f"{k.replace('Eixo ', '')}:", v)

    # ---- Ausentes / Excessos ----
    pdf.section_title("Ausentes, Excessos e Totais")
    aus = ", ".join(map(str, r["Ausentes"])) if r["Ausentes"] else "Nenhum"
    exc = ", ".join(map(str, r["Excessos"])) if r["Excessos"] else "Nenhum"
    pdf.label_value_row("Ausentes:", aus)
    pdf.label_value_row(f"Excessos (>={LIMIAR_EXCESSO}):", exc)
    pdf.label_value_row("Total nome:", r["TotalNome"])
    pdf.label_value_row("Total letras:", r["TotalLetras"])

    # ---- Análise Interpretativa (pode ocupar mais de uma página) ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 8, _safe("Analise Interpretativa"))
    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(*GRAY_TEXT)
    pdf.multi_cell(
        0, 4.5,
        _safe("Leitura simbolica baseada na tradicao numerologica, pensada como "
              "ferramenta de autorreflexao - nao como diagnostico, previsao ou "
              "afirmacao factual."),
    )
    pdf.ln(2)

    for titulo_secao, paragrafos in analise_completa(nome, r):
        pdf.set_font("Helvetica", "B", 10.5)
        pdf.set_text_color(*NAVY)
        pdf.cell(0, 7, _safe(titulo_secao))
        pdf.ln(7)
        for p in paragrafos:
            # remove tags <b>/</b> usadas na versão reportlab (fpdf2 core
            # fonts não interpretam HTML); mantém só o texto.
            texto_limpo = p.replace("<b>", "").replace("</b>", "")
            pdf.paragraph(texto_limpo)

    pdf.output(caminho)
    return caminho
