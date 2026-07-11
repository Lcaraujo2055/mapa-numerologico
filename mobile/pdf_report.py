# -*- coding: utf-8 -*-
"""
Geração do PDF do Mapa Numerológico — versão Android.

Escrito sobre `simplepdf.py` (zero dependências externas) em vez de
reportlab/fpdf2 — ambos esbarraram em problemas específicos de empacotamento
do python-for-android (recipe travada do reportlab; bug de pip ao instalar
dependências do fpdf2 sem receita própria). Sem nenhuma dependência extra
além do próprio Kivy, esse problema deixa de existir.

Mesma assinatura de função que as versões anteriores
(`gerar_pdf(nome, data, r, pasta_destino) -> caminho`), para que main.py não
precise de nenhuma alteração.
"""
import os
from datetime import datetime

from simplepdf import PDFDoc, A4_W, A4_H
from core import LIMIAR_EXCESSO
from interpretations import analise_completa

NAVY = (30, 42, 68)
GOLD = (184, 145, 47)
GOLD_SOFT = (243, 233, 210)
INK = (35, 35, 35)
GRAY_TEXT = (107, 107, 107)
ROW_ALT = (243, 244, 247)
LINE_GRAY = (217, 220, 225)
WHITE = (255, 255, 255)

PAGE_W, PAGE_H = A4_W, A4_H
MARGIN = 40
HEADER_H = 74
CONTENT_W = PAGE_W - 2 * MARGIN
BOTTOM_LIMIT = PAGE_H - 55


class MobileReport:
    def __init__(self, nome, data, alma=""):
        self.doc = PDFDoc()
        self.nome = nome
        self.data = data
        self.alma = alma
        self.page_num = 0
        self.y = 0
        self._new_page()

    # ------------------------------------------------------------ Páginas
    def _new_page(self):
        self.doc.add_page()
        self.page_num += 1
        self._draw_chrome()
        self.y = HEADER_H + 18

    def _draw_chrome(self):
        d = self.doc
        d.rect(0, 0, PAGE_W, HEADER_H, fill_rgb=NAVY)
        d.rect(0, HEADER_H, PAGE_W, 3, fill_rgb=GOLD)
        d.text(MARGIN, 13, "MAPA NUMEROLOGICO", font="HB", size=17, rgb=WHITE)
        d.text(MARGIN, 37, "Relatorio pessoal de analise numerologica", font="H", size=9.5, rgb=(216, 222, 234))

        box_w = 230
        x_right = PAGE_W - MARGIN - box_w
        d.text(x_right, 10, self.nome, font="HB", size=11, rgb=WHITE, align="R", max_width=box_w)
        d.text(x_right, 24, self.alma, font="HB", size=9, rgb=GOLD, align="R", max_width=box_w)
        d.text(x_right, 38, f"Nascimento: {self.data}", font="H", size=9.5, rgb=(216, 222, 234), align="R", max_width=box_w)

        footer_y = PAGE_H - 40
        d.line(MARGIN, footer_y, PAGE_W - MARGIN, footer_y, rgb=LINE_GRAY, line_width=0.7)
        emissao = datetime.now().strftime("%d/%m/%Y %H:%M")
        d.text(MARGIN, footer_y + 8, f"Emitido em {emissao}", font="H", size=8, rgb=GRAY_TEXT)
        d.text(MARGIN, footer_y + 8, f"Pagina {self.page_num}", font="H", size=8,
               rgb=GRAY_TEXT, align="R", max_width=CONTENT_W)

    def ensure_space(self, needed_h):
        if self.y + needed_h > BOTTOM_LIMIT:
            self._new_page()

    def force_new_page(self):
        self._new_page()

    # -------------------------------------------------------------- Peças
    def section_title(self, texto):
        self.ensure_space(28)
        self.y += 6
        d = self.doc
        d.rect(MARGIN, self.y, CONTENT_W, 22, fill_rgb=GOLD_SOFT)
        d.rect(MARGIN, self.y, 3, 22, fill_rgb=GOLD)
        d.text(MARGIN + 10, self.y + 5, texto, font="HB", size=11, rgb=NAVY)
        self.y += 22 + 6

    def label_value(self, label, value, x=None, col_w=None):
        x = MARGIN if x is None else x
        col_w = col_w or CONTENT_W
        d = self.doc
        d.text(x, self.y, label, font="H", size=9.5, rgb=GRAY_TEXT, max_width=col_w * 0.5)
        d.text(x + col_w * 0.42, self.y, str(value), font="HB", size=9.5, rgb=INK, max_width=col_w * 0.58)
        self.y += 15

    def paragraph(self, texto):
        d = self.doc
        end_y = d.multi_text(MARGIN, self.y, texto, font="H", size=9.3, rgb=INK,
                              max_width=CONTENT_W, leading=12.5, align="L")
        self.y = end_y + 5

    def cards(self, itens):
        self.ensure_space(56)
        d = self.doc
        n = len(itens)
        gap = 6
        card_w = (CONTENT_W - gap * (n - 1)) / n
        card_h = 50
        x = MARGIN
        for label, valor in itens:
            d.rect(x, self.y, card_w, card_h, fill_rgb=NAVY)
            d.text(x, self.y + 8, label.upper(), font="H", size=8, rgb=(216, 222, 234),
                   align="C", max_width=card_w)
            d.text(x, self.y + 22, str(valor), font="HB", size=17, rgb=GOLD,
                   align="C", max_width=card_w)
            x += card_w + gap
        self.y += card_h + 14

    def table(self, header, rows, col_widths, zebra=True, highlight_last=False):
        d = self.doc
        row_h = 17
        self.ensure_space(row_h * (len(rows) + 1))
        x0 = MARGIN
        # cabeçalho
        d.rect(x0, self.y, CONTENT_W, row_h, fill_rgb=NAVY)
        cx = x0
        for h, w in zip(header, col_widths):
            d.text(cx, self.y + 4, h, font="HB", size=8.6, rgb=WHITE, align="C", max_width=w)
            cx += w
        self.y += row_h
        for i, row in enumerate(rows):
            is_last = highlight_last and i == len(rows) - 1
            bg = GOLD_SOFT if is_last else (WHITE if (i % 2 == 0) else ROW_ALT)
            d.rect(x0, self.y, CONTENT_W, row_h, fill_rgb=bg)
            cx = x0
            for val, w in zip(row, col_widths):
                d.text(cx, self.y + 4, str(val), font=("HB" if is_last else "H"),
                       size=8.6, rgb=INK, align="C", max_width=w)
                cx += w
            self.y += row_h
        self.y += 10

    def output(self, path):
        self.doc.output(path)


def gerar_pdf(nome: str, data: str, r: dict, pasta_destino: str) -> str:
    os.makedirs(pasta_destino, exist_ok=True)
    safe_nome = "".join(
        ch for ch in nome if ch.isalnum() or ch in (" ", "_", "-")
    ).strip().replace(" ", "_") or "Mapa"
    agora = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho = os.path.join(pasta_destino, f"Mapa_Numerologico_{safe_nome}_{agora}.pdf")

    rep = MobileReport(nome, data, alma=r.get("Alma", ""))

    # ---- Números fundamentais ----
    itens = [
        ("Interior", r["Interior"]), ("Exterior", r["Exterior"]),
        ("Sintese", r["Síntese"]), ("Caminho", r["Caminho"]),
        ("Quinta", r["Quinta"]), ("Karma", r["Soma"]),
    ]
    rep.cards(itens)

    # ---- Vocação e Desafios ----
    rep.section_title("Vocacao e Desafios")
    voc = r["Vocacao"]
    des = r["Desafios"]
    half = CONTENT_W / 2
    y_start = rep.y
    rep.label_value("Dia:", voc["Dia do Nascimento"], x=MARGIN, col_w=half)
    rep.label_value("Sintese:", voc["Síntese"], x=MARGIN, col_w=half)
    rep.label_value("Caminho:", voc["Caminho da Vida"], x=MARGIN, col_w=half)
    y_after_left = rep.y
    rep.y = y_start
    for pos in ("1º", "2º", "3º", "4º"):
        rep.label_value(f"{pos}:", des[pos], x=MARGIN + half, col_w=half)
    rep.y = max(rep.y, y_after_left) + 6

    # ---- Tabela numérica ----
    rep.section_title("Tabela Numerica do Nome")
    col_w = CONTENT_W / 3
    rows = [[n, qtd, soma] for n, qtd, soma in r["TabelaRows"]]
    rows.append(["TOTAL", r["TotalLetras"], r["TotalNome"]])
    rep.table(["Numero", "Qtd", "Somatorio"], rows, [col_w, col_w, col_w], highlight_last=True)

    # ---- Temperamentos ----
    rep.section_title("Temperamentos")
    e = r["Eixos"]
    for k, v in e.items():
        rep.label_value(f"{k.replace('Eixo ', '')}:", v)

    # ---- Ausentes / Excessos ----
    rep.section_title("Ausentes, Excessos e Totais")
    aus = ", ".join(map(str, r["Ausentes"])) if r["Ausentes"] else "Nenhum"
    exc = ", ".join(map(str, r["Excessos"])) if r["Excessos"] else "Nenhum"
    rep.label_value("Ausentes:", aus)
    rep.label_value(f"Excessos (>={LIMIAR_EXCESSO}):", exc)
    rep.label_value("Total nome:", r["TotalNome"])
    rep.label_value("Total letras:", r["TotalLetras"])

    # ---- Análise Interpretativa ----
    rep.force_new_page()
    d = rep.doc
    d.text(MARGIN, rep.y, "Analise Interpretativa", font="HB", size=15, rgb=NAVY)
    rep.y += 22
    rep.y = d.multi_text(
        MARGIN, rep.y,
        "Leitura simbolica baseada na tradicao numerologica, pensada como "
        "ferramenta de autorreflexao - nao como diagnostico, previsao ou "
        "afirmacao factual.",
        font="HO", size=8, rgb=GRAY_TEXT, max_width=CONTENT_W, leading=10.5,
    ) + 8

    for titulo_secao, paragrafos in analise_completa(nome, r):
        rep.ensure_space(30)
        d.text(MARGIN, rep.y, titulo_secao, font="HB", size=10.5, rgb=NAVY)
        rep.y += 16
        for p in paragrafos:
            texto_limpo = p.replace("<b>", "").replace("</b>", "")
            rep.ensure_space(20)
            rep.paragraph(texto_limpo)

    rep.output(caminho)
    return caminho
