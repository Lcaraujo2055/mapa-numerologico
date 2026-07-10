# -*- coding: utf-8 -*-
"""
Mapa Numerológico — versão Android (Kivy).

Reaproveita 100% da lógica de core.py, interpretations.py e pdf_report.py.
Só a camada de interface (e o destino/compartilhamento do PDF) é específica
de mobile.

AVISO: este código foi escrito com cuidado seguindo padrões-padrão do Kivy,
mas não pôde ser executado/testado em ambiente real (sem Kivy, sem Android
SDK/NDK disponíveis no ambiente onde foi escrito). Rode e reporte o primeiro
erro que aparecer para irmos ajustando.
"""
import os
from datetime import datetime

from kivy.app import App
from kivy.metrics import dp
from kivy.properties import StringProperty, ListProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.factory import Factory

from core import mapa_completo, LIMIAR_EXCESSO
from pdf_report import gerar_pdf
from android_storage import save_to_downloads

NAVY = (0.118, 0.165, 0.267, 1)
GOLD = (0.722, 0.569, 0.184, 1)
GOLD_SOFT = (0.953, 0.914, 0.822, 1)
ROW_ALT = (0.933, 0.945, 0.965, 1)
WHITE = (1, 1, 1, 1)


# ---------------------------------------------------------------- Widgets
class NumberCard(BoxLayout):
    titulo = StringProperty("")
    valor = StringProperty("\u2014")


class ResultRow(BoxLayout):
    label_text = StringProperty("")
    value_text = StringProperty("\u2014")


class CellLabel(Label):
    bg_color = ListProperty([1, 1, 1, 1])
    is_bold = BooleanProperty(False)


class SectionBlock(BoxLayout):
    """Cartão branco com título + linhas 'rótulo: valor' adicionadas via add_row."""

    def __init__(self, titulo, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Factory.SectionTitle(text=titulo))
        self._rows = {}

    def add_row(self, key, label):
        row = ResultRow(label_text=label)
        self.add_widget(row)
        self._rows[key] = row
        return row

    def set_value(self, key, value):
        if key in self._rows:
            self._rows[key].value_text = "\u2014" if value is None else str(value)


class NumberTable(BoxLayout):
    """Tabela Numérica do Nome (cabeçalho + 9 linhas + total), construída em Python."""

    def __init__(self, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("spacing", dp(1))
        super().__init__(**kwargs)
        self.bind(minimum_height=self.setter("height"))

        header = GridLayout(cols=3, size_hint_y=None, height=dp(30), spacing=dp(1))
        for h in ("N\u00famero", "Qtd", "Somat\u00f3rio"):
            header.add_widget(CellLabel(text=h, bg_color=NAVY, color=(1, 1, 1, 1), is_bold=True))
        self.add_widget(header)

        self.rows_container = GridLayout(cols=3, size_hint_y=None, spacing=dp(1))
        self.rows_container.bind(minimum_height=self.rows_container.setter("height"))
        self.add_widget(self.rows_container)

    def update(self, rows, total_letras, total_nome):
        self.rows_container.clear_widgets()
        for i, (n, qtd, soma) in enumerate(rows):
            bg = WHITE if i % 2 == 0 else ROW_ALT
            for val in (n, qtd, soma):
                self.rows_container.add_widget(CellLabel(text=str(val), bg_color=bg))
        for val in ("TOTAL", total_letras, total_nome):
            self.rows_container.add_widget(
                CellLabel(text=str(val), bg_color=GOLD_SOFT, is_bold=True)
            )


class RootWidget(BoxLayout):
    pass


def show_popup(titulo, mensagem):
    box = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
    box.add_widget(Label(text=mensagem, halign="center"))
    btn = Button(text="OK", size_hint_y=None, height=dp(42))
    box.add_widget(btn)
    popup = Popup(title=titulo, content=box, size_hint=(0.85, 0.4))
    btn.bind(on_release=popup.dismiss)
    popup.open()


# ------------------------------------------------------------------- App
class NumerologiaApp(App):
    def build(self):
        self.title = "Mapa Numerol\u00f3gico"
        self.ultimo = None
        self.root_widget = RootWidget()
        self._build_body()
        return self.root_widget

    # ---------------------------------------------------------- Montagem
    def _build_body(self):
        content = self.root_widget.ids.content

        # Cartões dos números fundamentais
        cards_grid = GridLayout(cols=3, spacing=dp(8), size_hint_y=None, height=dp(168))
        self.cards = {}
        for key in ("Interior", "Exterior", "S\u00edntese", "Caminho", "Quinta", "Karma"):
            card = NumberCard(titulo=key.upper())
            self.cards[key] = card
            cards_grid.add_widget(card)
        content.add_widget(cards_grid)

        # Vocação
        self.blk_vocacao = SectionBlock("Voca\u00e7\u00e3o")
        self.blk_vocacao.add_row("dia", "Dia:")
        self.blk_vocacao.add_row("sintese", "S\u00edntese:")
        self.blk_vocacao.add_row("caminho", "Caminho:")
        content.add_widget(self.blk_vocacao)

        # Desafios
        self.blk_desafios = SectionBlock("Desafios")
        for pos in ("1\u00ba", "2\u00ba", "3\u00ba", "4\u00ba"):
            self.blk_desafios.add_row(pos, f"{pos}:")
        content.add_widget(self.blk_desafios)

        # Temperamentos
        self.blk_eixos = SectionBlock("Temperamentos")
        self.blk_eixos.add_row("mental", "Mental:")
        self.blk_eixos.add_row("emocional", "Emocional:")
        self.blk_eixos.add_row("fisico", "F\u00edsico:")
        self.blk_eixos.add_row("intuitivo", "Intuitivo:")
        content.add_widget(self.blk_eixos)

        # Ausentes / Excessos / Totais
        self.blk_extra = SectionBlock("Ausentes, Excessos e Totais")
        self.blk_extra.add_row("ausentes", "Ausentes:")
        self.blk_extra.add_row("excessos", f"Excessos (\u2265{LIMIAR_EXCESSO}):")
        self.blk_extra.add_row("total_nome", "Total nome:")
        self.blk_extra.add_row("total_letras", "Total letras:")
        content.add_widget(self.blk_extra)

        # Tabela numérica
        self.blk_tabela = SectionBlock("Tabela Num\u00e9rica do Nome")
        self.tabela = NumberTable()
        self.blk_tabela.add_widget(self.tabela)
        content.add_widget(self.blk_tabela)

        self._limpar_resultados()

    # ------------------------------------------------------------ Estado
    def _limpar_resultados(self):
        for card in self.cards.values():
            card.valor = "\u2014"
        for blk, keys in (
            (self.blk_vocacao, ["dia", "sintese", "caminho"]),
            (self.blk_desafios, ["1\u00ba", "2\u00ba", "3\u00ba", "4\u00ba"]),
            (self.blk_eixos, ["mental", "emocional", "fisico", "intuitivo"]),
            (self.blk_extra, ["ausentes", "excessos", "total_nome", "total_letras"]),
        ):
            for k in keys:
                blk.set_value(k, None)
        self.tabela.update([[n, 0, 0] for n in range(1, 10)], 0, 0)

    def _preencher_resultados(self, r):
        self.cards["Interior"].valor = str(r["Interior"])
        self.cards["Exterior"].valor = str(r["Exterior"])
        self.cards["S\u00edntese"].valor = str(r["S\u00edntese"])
        self.cards["Caminho"].valor = str(r["Caminho"])
        self.cards["Quinta"].valor = str(r["Quinta"])
        self.cards["Karma"].valor = str(r["Soma"])

        voc = r["Vocacao"]
        self.blk_vocacao.set_value("dia", voc["Dia do Nascimento"])
        self.blk_vocacao.set_value("sintese", voc["S\u00edntese"])
        self.blk_vocacao.set_value("caminho", voc["Caminho da Vida"])

        des = r["Desafios"]
        for pos in ("1\u00ba", "2\u00ba", "3\u00ba", "4\u00ba"):
            self.blk_desafios.set_value(pos, des[pos])

        e = r["Eixos"]
        self.blk_eixos.set_value("mental", e["Eixo Mental"])
        self.blk_eixos.set_value("emocional", e["Eixo Emocional"])
        self.blk_eixos.set_value("fisico", e["Eixo F\u00edsico"])
        self.blk_eixos.set_value("intuitivo", e["Eixo Intuitivo"])

        aus = ", ".join(map(str, r["Ausentes"])) if r["Ausentes"] else "Nenhum"
        exc = ", ".join(map(str, r["Excessos"])) if r["Excessos"] else "Nenhum"
        self.blk_extra.set_value("ausentes", aus)
        self.blk_extra.set_value("excessos", exc)
        self.blk_extra.set_value("total_nome", r["TotalNome"])
        self.blk_extra.set_value("total_letras", r["TotalLetras"])

        self.tabela.update(r["TabelaRows"], r["TotalLetras"], r["TotalNome"])

    # ------------------------------------------------------------ Ações
    def on_calcular(self):
        ids = self.root_widget.ids
        nome = (ids.in_nome.text or "").strip()
        data = (ids.in_data.text or "").strip()
        if not nome:
            show_popup("Aten\u00e7\u00e3o", "Informe o nome completo.")
            return
        if not data:
            show_popup("Aten\u00e7\u00e3o", "Informe a data de nascimento (dd/mm/aaaa).")
            return
        try:
            r = mapa_completo(nome, data)
            self._preencher_resultados(r)
            self.ultimo = {"nome": nome, "data": data, "r": r}
        except Exception as e:
            show_popup("Erro", str(e))

    def on_gerar_pdf(self):
        if not self.ultimo:
            show_popup("Aten\u00e7\u00e3o", "Primeiro toque em 'Calcular' para gerar o relat\u00f3rio.")
            return
        # Pequeno delay para o botão renderizar o toque antes do trabalho de PDF.
        Clock.schedule_once(lambda dt: self._gerar_pdf_impl(), 0)

    def _gerar_pdf_impl(self):
        try:
            pasta = self.user_data_dir  # diretório privado do app, sempre gravável
            caminho_pdf = gerar_pdf(
                self.ultimo["nome"], self.ultimo["data"], self.ultimo["r"],
                pasta_destino=pasta,
            )
        except Exception as e:
            show_popup("Erro ao gerar PDF", str(e))
            return

        compartilhado = False  # compartilhamento nativo fica para uma próxima versão
        nome_arquivo = os.path.basename(caminho_pdf)
        destino_downloads = save_to_downloads(caminho_pdf, nome_arquivo)

        if destino_downloads:
            show_popup(
                "PDF gerado",
                f"PDF salvo em Downloads:\n{nome_arquivo}\n\n"
                "Abra o app Arquivos (ou Google Drive) e procure na pasta Downloads.",
            )
        elif not compartilhado:
            show_popup(
                "PDF gerado",
                f"PDF salvo em:\n{caminho_pdf}\n\n"
                "Use um gerenciador de arquivos do aparelho para abrir ou mover.",
            )

    def on_limpar(self):
        ids = self.root_widget.ids
        ids.in_nome.text = ""
        ids.in_data.text = ""
        self._limpar_resultados()
        self.ultimo = None


if __name__ == "__main__":
    NumerologiaApp().run()
