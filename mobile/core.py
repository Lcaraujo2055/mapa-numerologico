# -*- coding: utf-8 -*-
"""
Núcleo de cálculo numerológico.

Contém toda a lógica matemática do Mapa Numerológico: reduções,
Interior/Exterior, Caminho de Vida, Desafios, Eixos (Temperamentos),
Tabela Numérica do Nome e o cálculo completo (mapa_completo).

Este módulo não depende de GUI nem de PDF — pode ser testado e usado
isoladamente.
"""

TABELA = {
    'A': 1, 'J': 1, 'S': 1,
    'B': 2, 'K': 2, 'T': 2,
    'C': 3, 'L': 3, 'U': 3,
    'D': 4, 'M': 4, 'V': 4,
    'E': 5, 'N': 5, 'W': 5,
    'F': 6, 'O': 6, 'X': 6,
    'G': 7, 'P': 7, 'Y': 7,
    'H': 8, 'Q': 8, 'Z': 8,
    'I': 9, 'R': 9,
}
VOGAIS = {'A', 'E', 'I', 'O', 'U'}
MESTRES = {11, 22, 33}
LIMIAR_EXCESSO = 4


# ------------------------------------------------------------- Núcleo -----
def reduzir(n: int, manter_mestres: bool = True) -> int:
    """Reduz numerologicamente. Se manter_mestres=True, para em 11/22/33."""
    while n > 9:
        if manter_mestres and n in MESTRES:
            return n
        n = sum(int(d) for d in str(n))
    return n


def limpar_nome(nome: str) -> str:
    """Mantém apenas letras e espaços, em maiúsculas."""
    return ''.join(c for c in (nome or "").upper().strip() if c.isalpha() or c.isspace())


def parse_data(data: str):
    """Aceita dd/mm/aaaa (ou dd-mm-aaaa)."""
    s = (data or "").strip().replace("-", "/")
    partes = s.split("/")
    if len(partes) != 3:
        raise ValueError("Data inválida. Use dd/mm/aaaa.")
    dd, mm, aaaa = partes
    if not (dd.isdigit() and mm.isdigit() and aaaa.isdigit()):
        raise ValueError("Data inválida. Use apenas números em dd/mm/aaaa.")
    dia, mes, ano = int(dd), int(mm), int(aaaa)
    if not (1 <= dia <= 31 and 1 <= mes <= 12 and 1000 <= ano <= 9999):
        raise ValueError("Data inválida. Verifique dia/mês/ano.")
    return dia, mes, ano


def contar_numeros_no_nome(nome: str):
    """Conta quantas vezes cada número 1..9 aparece no nome (pela TABELA)."""
    cont = {i: 0 for i in range(1, 10)}
    for l in limpar_nome(nome):
        if l in TABELA:
            cont[TABELA[l]] += 1
    return cont


def calcular_interior_exterior(nome: str):
    """Interior=vogais, Exterior=consoantes. Retorna (interior reduzido, exterior reduzido, soma bruta)."""
    interior = exterior = 0
    for l in limpar_nome(nome):
        if l in TABELA:
            if l in VOGAIS:
                interior += TABELA[l]
            else:
                exterior += TABELA[l]
    soma_nome = interior + exterior
    return reduzir(interior, True), reduzir(exterior, True), soma_nome


def caminho_vida(data: str):
    """Caminho = soma dos dígitos da data, reduzindo com mestres."""
    soma = sum(int(d) for d in data if d.isdigit())
    return reduzir(soma, True), soma


def desafios(data: str):
    """Desafios (convenção sem mestres)."""
    d, m, a = parse_data(data)
    d, m, a = reduzir(d, False), reduzir(m, False), reduzir(a, False)
    d1 = abs(d - m)
    d2 = abs(d - a)
    d3 = abs(d1 - d2)
    d4 = abs(m - a)
    return {
        "1º": reduzir(d1, False),
        "2º": reduzir(d2, False),
        "3º": reduzir(d3, False),
        "4º": reduzir(d4, False),
    }


def tabela_numerica(nome: str):
    """Frequência 1..9 no nome e somatórios."""
    freq = {i: 0 for i in range(1, 10)}
    for l in limpar_nome(nome):
        if l in TABELA:
            freq[TABELA[l]] += 1
    rows = []
    total_nome = 0
    for n in range(1, 10):
        qtd = freq[n]
        soma = qtd * n
        rows.append([n, qtd, soma])
        total_nome += soma
    total_letras = sum(freq.values())
    return rows, total_nome, total_letras, freq


# ------------------------------------------------- Eixos (Temperamentos) --
def eixos_funcionais(nome: str):
    """
    Eixos por CONTAGEM (sem ponderação) e sem mestres.
    Ordem (UI + PDF): Mental, Emocional, Físico, Intuitivo.
    """
    c = contar_numeros_no_nome(nome)
    eixo_ego_dominio = reduzir(c[1] + c[8], False)
    eixo_aec = reduzir(c[2] + c[3] + c[6], False)
    eixo_corporal = reduzir(c[4] + c[5], False)
    eixo_espiritual_humanitario = reduzir(c[7] + c[9], False)
    return {
        "Eixo Mental": eixo_ego_dominio,
        "Eixo Emocional": eixo_aec,
        "Eixo Físico": eixo_corporal,
        "Eixo Intuitivo": eixo_espiritual_humanitario,
    }


# ------------------------------------------------------- Mapa completo ----
def mapa_completo(nome: str, data: str):
    dia, mes, ano = parse_data(data)
    interior, exterior, soma_nome = calcular_interior_exterior(nome)
    sintese = reduzir(soma_nome, True)
    caminho, _ = caminho_vida(data)

    # Quinta Essência = reduzir(Síntese + Caminho, mantendo mestres)
    quinta = reduzir(sintese + caminho, True)

    tab_rows, total_nome, total_letras, freq = tabela_numerica(nome)

    vocacao = {
        "Dia do Nascimento": reduzir(dia, True),
        "Síntese": sintese,
        "Caminho da Vida": caminho,
    }

    # Soma (rotulada como "Karma" no PDF) — com mestres
    soma = reduzir((sintese + interior + reduzir(dia, True) + caminho), True)

    ausentes = [n for n in range(1, 10) if freq[n] == 0]
    excessos = [n for n in range(1, 10) if freq[n] >= LIMIAR_EXCESSO]

    return {
        "Interior": interior,
        "Exterior": exterior,
        "Síntese": sintese,
        "Caminho": caminho,
        "Quinta": quinta,
        "Soma": soma,
        "Vocacao": vocacao,
        "Desafios": desafios(data),
        "Eixos": eixos_funcionais(nome),
        "TabelaRows": tab_rows,
        "TotalNome": total_nome,
        "TotalLetras": total_letras,
        "Ausentes": ausentes,
        "Excessos": excessos,
    }
