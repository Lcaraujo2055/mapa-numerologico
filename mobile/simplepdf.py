# -*- coding: utf-8 -*-
"""
Gerador de PDF mínimo, sem NENHUMA dependência externa — só biblioteca
padrão do Python. Escreve a sintaxe do PDF diretamente.

Motivo: tanto o reportlab quanto o fpdf2 esbarraram em problemas de
empacotamento específicos do python-for-android (recipe travada / bug de
pip ao instalar pacotes sem receita). Este módulo elimina esse risco por
completo, pois não precisa de nenhum "requirement" extra além do próprio
Kivy.

Suporta: texto (com quebra de linha automática), retângulos preenchidos,
linhas, múltiplas páginas, fontes-base padrão do PDF (Helvetica), e
caracteres acentuados do português via WinAnsiEncoding.
"""

A4_W, A4_H = 595.28, 841.89

_FONTS = {
    "H": "Helvetica",
    "HB": "Helvetica-Bold",
    "HO": "Helvetica-Oblique",
}

# Larguras aproximadas (em milésimos do tamanho da fonte) da Helvetica,
# padrão AFM. Cobre ASCII + acentuados latin-1 mais comuns.
_WIDTHS_HELVETICA = {
    ' ': 278, '!': 278, '"': 355, '#': 556, '$': 556, '%': 889, '&': 667,
    "'": 191, '(': 333, ')': 333, '*': 389, '+': 584, ',': 278, '-': 333,
    '.': 278, '/': 278, '0': 556, '1': 556, '2': 556, '3': 556, '4': 556,
    '5': 556, '6': 556, '7': 556, '8': 556, '9': 556, ':': 278, ';': 278,
    '<': 584, '=': 584, '>': 584, '?': 556, '@': 1015, 'A': 667, 'B': 667,
    'C': 722, 'D': 722, 'E': 667, 'F': 611, 'G': 778, 'H': 722, 'I': 278,
    'J': 500, 'K': 667, 'L': 556, 'M': 833, 'N': 722, 'O': 778, 'P': 667,
    'Q': 778, 'R': 722, 'S': 667, 'T': 611, 'U': 722, 'V': 667, 'W': 944,
    'X': 667, 'Y': 667, 'Z': 611, '[': 278, '\\': 278, ']': 278, '^': 469,
    '_': 556, '`': 333, 'a': 556, 'b': 556, 'c': 500, 'd': 556, 'e': 556,
    'f': 278, 'g': 556, 'h': 556, 'i': 222, 'j': 222, 'k': 500, 'l': 222,
    'm': 833, 'n': 556, 'o': 556, 'p': 556, 'q': 556, 'r': 333, 's': 500,
    't': 278, 'u': 556, 'v': 500, 'w': 722, 'x': 500, 'y': 500, 'z': 500,
    '{': 334, '|': 260, '}': 334, '~': 584,
    'á': 556, 'à': 556, 'â': 556, 'ã': 556, 'ä': 556, 'é': 556, 'è': 556,
    'ê': 556, 'ë': 556, 'í': 222, 'ì': 222, 'î': 222, 'ï': 222, 'ó': 556,
    'ò': 556, 'ô': 556, 'õ': 556, 'ö': 556, 'ú': 556, 'ù': 556, 'û': 556,
    'ü': 556, 'ç': 500, 'ñ': 556, 'Á': 667, 'À': 667, 'Â': 667, 'Ã': 667,
    'É': 667, 'È': 667, 'Ê': 667, 'Í': 278, 'Ì': 278, 'Ó': 778, 'Ò': 778,
    'Ô': 778, 'Õ': 778, 'Ú': 722, 'Ù': 722, 'Ç': 722, 'Ñ': 722,
    'º': 400, 'ª': 370, '°': 400,
}
_WIDTHS_BOLD = dict(_WIDTHS_HELVETICA)
_BOLD_OVERRIDES = {
    'a': 556, 'b': 611, 'c': 556, 'd': 611, 'e': 556, 'f': 333, 'g': 611,
    'h': 611, 'i': 278, 'j': 278, 'k': 556, 'l': 278, 'm': 889, 'n': 611,
    'o': 611, 'p': 611, 'q': 611, 'r': 389, 's': 556, 't': 333, 'u': 611,
    'v': 556, 'w': 778, 'x': 556, 'y': 556, 'z': 500,
    'A': 722, 'B': 722, 'C': 722, 'D': 722, 'E': 667, 'F': 611, 'G': 778,
    'H': 722, 'I': 278, 'J': 556, 'K': 722, 'L': 611, 'M': 833, 'N': 722,
    'O': 778, 'P': 667, 'Q': 778, 'R': 722, 'S': 667, 'T': 611, 'U': 722,
    'V': 667, 'W': 944, 'X': 667, 'Y': 667, 'Z': 611,
}
_WIDTHS_BOLD.update(_BOLD_OVERRIDES)


def _text_width(text, bold, size):
    table = _WIDTHS_BOLD if bold else _WIDTHS_HELVETICA
    total = sum(table.get(ch, 556) for ch in text)
    return total * size / 1000.0


def _escape(text):
    return text.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def _wrap_text(text, bold, size, max_width):
    """Quebra texto em linhas que cabem em max_width (pontos)."""
    words = text.split(" ")
    lines = []
    current = ""
    for w in words:
        candidate = (current + " " + w).strip() if current else w
        if _text_width(candidate, bold, size) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


class PDFDoc:
    def __init__(self):
        self._objects = []  # lista de bytes de cada objeto (índice 0 = obj 1)
        self._pages = []  # cada item: dict(content=[ops...], )
        self._font_obj_nums = {}
        self._cur_ops = None
        self._page_w = A4_W
        self._page_h = A4_H

    # --------------------------------------------------------- Estrutura
    def _new_obj(self):
        self._objects.append(None)
        return len(self._objects)  # número do objeto (1-based)

    def add_page(self):
        self._cur_ops = []
        self._pages.append(self._cur_ops)
        return len(self._pages) - 1

    # -------------------------------------------------------- Primitivas
    def set_fill_color(self, rgb):
        r, g, b = rgb
        self._cur_ops.append(f"{r/255:.3f} {g/255:.3f} {b/255:.3f} rg")

    def set_stroke_color(self, rgb):
        r, g, b = rgb
        self._cur_ops.append(f"{r/255:.3f} {g/255:.3f} {b/255:.3f} RG")

    def rect(self, x, y, w, h, fill_rgb=None, stroke_rgb=None, line_width=1):
        # PDF: origem (0,0) no canto inferior esquerdo. Nossa API usa
        # origem no canto SUPERIOR esquerdo (mais intuitivo p/ layout tipo
        # "topo da página"), então convertemos aqui.
        y_pdf = self._page_h - y - h
        self._cur_ops.append("q")
        if fill_rgb is not None:
            self.set_fill_color(fill_rgb)
        if stroke_rgb is not None:
            self.set_stroke_color(stroke_rgb)
            self._cur_ops.append(f"{line_width} w")
        self._cur_ops.append(f"{x:.2f} {y_pdf:.2f} {w:.2f} {h:.2f} re")
        if fill_rgb is not None and stroke_rgb is not None:
            self._cur_ops.append("B")
        elif fill_rgb is not None:
            self._cur_ops.append("f")
        elif stroke_rgb is not None:
            self._cur_ops.append("S")
        self._cur_ops.append("Q")

    def line(self, x1, y1, x2, y2, rgb=(0, 0, 0), line_width=1):
        y1p = self._page_h - y1
        y2p = self._page_h - y2
        self._cur_ops.append("q")
        self.set_stroke_color(rgb)
        self._cur_ops.append(f"{line_width} w")
        self._cur_ops.append(f"{x1:.2f} {y1p:.2f} m {x2:.2f} {y2p:.2f} l S")
        self._cur_ops.append("Q")

    def text(self, x, y, s, font="H", size=10, rgb=(0, 0, 0), align="L", max_width=None):
        """Desenha uma linha de texto. y = topo da linha (baseline ~ y+size*0.8)."""
        if not s:
            return
        bold = font == "HB"
        baseline_y = self._page_h - y - size * 0.85
        tx = x
        if align in ("C", "R") and max_width is not None:
            w = _text_width(s, bold, size)
            if align == "C":
                tx = x + (max_width - w) / 2
            elif align == "R":
                tx = x + (max_width - w)
        r, g, b = rgb
        encoded = s.encode("cp1252", errors="replace").decode("latin-1")
        self._cur_ops.append("BT")
        self._cur_ops.append(f"/{font} {size:.2f} Tf")
        self._cur_ops.append(f"{r/255:.3f} {g/255:.3f} {b/255:.3f} rg")
        self._cur_ops.append(f"{tx:.2f} {baseline_y:.2f} Td")
        self._cur_ops.append(f"({_escape(encoded)}) Tj")
        self._cur_ops.append("ET")

    def multi_text(self, x, y, s, font="H", size=10, rgb=(0, 0, 0), max_width=200, leading=None, align="L"):
        """Escreve texto com quebra automática de linha. Retorna o y final (abaixo da última linha)."""
        leading = leading or size * 1.35
        bold = font == "HB"
        cur_y = y
        for line in s.split("\n"):
            for wrapped in _wrap_text(line, bold, size, max_width):
                self.text(x, cur_y, wrapped, font=font, size=size, rgb=rgb, align=align, max_width=max_width)
                cur_y += leading
        return cur_y

    def text_width(self, s, font="H", size=10):
        return _text_width(s, font == "HB", size)

    # ------------------------------------------------------------- Saída
    def output(self, path):
        # 1) Fontes
        for code, base in _FONTS.items():
            n = self._new_obj()
            self._font_obj_nums[code] = n
            self._objects[n - 1] = (
                f"<< /Type /Font /Subtype /Type1 /BaseFont /{base} "
                f"/Encoding /WinAnsiEncoding >>"
            ).encode("latin-1")

        font_res = " ".join(f"/{code} {num} 0 R" for code, num in self._font_obj_nums.items())

        # 2) Páginas + streams de conteúdo
        page_obj_nums = []
        pages_obj_num = self._new_obj()  # reservado, preenchido depois
        for ops in self._pages:
            content_bytes = ("\n".join(ops)).encode("latin-1", errors="replace")
            content_num = self._new_obj()
            self._objects[content_num - 1] = (
                f"<< /Length {len(content_bytes)} >>\nstream\n"
            ).encode("latin-1") + content_bytes + b"\nendstream"

            page_num = self._new_obj()
            page_obj_nums.append(page_num)
            self._objects[page_num - 1] = (
                f"<< /Type /Page /Parent {pages_obj_num} 0 R "
                f"/MediaBox [0 0 {self._page_w:.2f} {self._page_h:.2f}] "
                f"/Resources << /Font << {font_res} >> >> "
                f"/Contents {content_num} 0 R >>"
            ).encode("latin-1")

        kids = " ".join(f"{n} 0 R" for n in page_obj_nums)
        self._objects[pages_obj_num - 1] = (
            f"<< /Type /Pages /Kids [{kids}] /Count {len(page_obj_nums)} >>"
        ).encode("latin-1")

        # 3) Catálogo
        catalog_num = self._new_obj()
        self._objects[catalog_num - 1] = (
            f"<< /Type /Catalog /Pages {pages_obj_num} 0 R >>"
        ).encode("latin-1")

        # 4) Monta o arquivo final com tabela xref
        buf = bytearray()
        buf += b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
        offsets = [0] * (len(self._objects) + 1)
        for i, obj_bytes in enumerate(self._objects, start=1):
            offsets[i] = len(buf)
            buf += f"{i} 0 obj\n".encode("latin-1")
            buf += obj_bytes
            buf += b"\nendobj\n"

        xref_offset = len(buf)
        n_objs = len(self._objects) + 1
        buf += f"xref\n0 {n_objs}\n".encode("latin-1")
        buf += b"0000000000 65535 f \n"
        for i in range(1, n_objs):
            buf += f"{offsets[i]:010d} 00000 n \n".encode("latin-1")

        buf += (
            f"trailer\n<< /Size {n_objs} /Root {catalog_num} 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF"
        ).encode("latin-1")

        with open(path, "wb") as f:
            f.write(bytes(buf))
