# -*- coding: utf-8 -*-
"""
Textos interpretativos usados na seção "Análise Interpretativa" do PDF.

Conteúdo autoral, escrito para este projeto — não é transcrição de nenhuma
obra de terceiros. Trata-se de uma leitura simbólica/tradicional da
numerologia, apresentada como ferramenta de autorreflexão, não como
afirmação factual ou científica.
"""

# --------------------------------------------------- Essência de cada número
NUMERO_ESSENCIA = {
    1: ("liderança, iniciativa e individualidade. É o número do começo: traz coragem "
        "para abrir caminhos, tomar decisões e agir de forma independente. Em excesso "
        "de rigidez, pode se manifestar como teimosia ou dificuldade em aceitar "
        "parcerias e opiniões divergentes."),
    2: ("cooperação, sensibilidade e diplomacia. É o número da parceria: favorece a "
        "escuta, o tato nas relações e a capacidade de mediar conflitos. Seu ponto de "
        "atenção é a dependência excessiva da aprovação alheia ou a insegurança diante "
        "de decisões próprias."),
    3: ("expressão, criatividade e comunicação. É o número da alegria social: floresce "
        "na fala, na escrita, na arte e no convívio leve. Seu desafio é a dispersão — "
        "espalhar energia em muitas direções sem aprofundar em nenhuma."),
    4: ("estrutura, disciplina e trabalho constante. É o número da construção sólida: "
        "traz method, organização e capacidade de concretizar projetos de longo prazo. "
        "Em excesso, pode aparecer como rigidez ou resistência a qualquer mudança de rota."),
    5: ("liberdade, movimento e versatilidade. É o número da mudança: traz curiosidade, "
        "adaptabilidade e gosto por experiências novas. Seu ponto de atenção é a "
        "inconstância — dificuldade em manter foco e compromissos de longo prazo."),
    6: ("responsabilidade, cuidado e senso de harmonia. É o número do lar e da "
        "comunidade: favorece o acolhimento, a busca por equilíbrio e a atenção aos "
        "outros. Seu desafio é o excesso de controle ou de sacrifício próprio em nome "
        "do cuidado alheio."),
    7: ("introspecção, análise e busca de sentido. É o número da profundidade: inclina "
        "à reflexão, ao estudo e a uma relação mais silenciosa com a espiritualidade. "
        "Seu ponto de atenção é o isolamento ou o ceticismo excessivo diante do que "
        "não pode ser explicado racionalmente."),
    8: ("poder material, gestão e ambição realizadora. É o número da concretização: "
        "favorece a organização de recursos, negócios e resultados tangíveis. Seu "
        "desafio é o excesso de foco no controle e no status, em detrimento de outras "
        "dimensões da vida."),
    9: ("compaixão, humanismo e encerramento de ciclos. É o número da generosidade "
        "ampla: inclina ao desapego, à visão de conjunto e ao cuidado com causas "
        "coletivas. Seu ponto de atenção é o idealismo excessivo, que pode dificultar "
        "lidar com o concreto do dia a dia."),
    11: ("um número mestre: intuição amplificada e sensibilidade fora do comum. Traz "
         "inspiração, percepção aguçada e potencial de influenciar outros pela força "
         "simbólica e emocional. Como toda energia amplificada, pode gerar tensão "
         "nervosa e autocobrança quando não encontra um canal construtivo de expressão."),
    22: ("um número mestre: o 'construtor', capaz de transformar visões grandiosas em "
         "realizações práticas e de largo alcance. Une a ambição do 8 à intuição do 11 "
         "com os pés no chão. Sua tensão característica é a pressão de estar sempre à "
         "altura do próprio potencial."),
    33: ("um número mestre: o 'mestre professor', associado a amor incondicional e "
         "serviço em grande escala. Inclina à dedicação ao bem coletivo, ao ensino e "
         "ao cuidado altruísta. Seu ponto de atenção é a exaustão que vem de doar-se "
         "além da própria capacidade."),
}

# ------------------------------------------------------- Introduções por eixo
CATEGORIA_INTRO = {
    "Interior": ("O número Interior revela o que move você por dentro — seus desejos, "
                 "valores e motivações mais íntimas, nem sempre expressos abertamente. "
                 "Em Interior {n}, a essência é"),
    "Exterior": ("O número Exterior indica como você tende a ser percebido pelos outros "
                 "— a primeira impressão, a 'máscara social' que projeta no dia a dia. "
                 "Em Exterior {n}, a essência é"),
    "Sintese": ("A Síntese une Interior e Exterior em um só número, representando sua "
                "expressão mais completa: a soma entre o que você sente e o que mostra "
                "ao mundo. Em Síntese {n}, a essência é"),
    "Caminho": ("O Caminho de Vida, calculado a partir da data de nascimento, aponta a "
                "trajetória geral, as lições centrais e as oportunidades que se repetem "
                "ao longo da existência. Em Caminho {n}, a essência é"),
    "Quinta": ("A Quinta Essência nasce do encontro entre a Síntese (quem você é) e o "
               "Caminho (para onde caminha), indicando um eixo de equilíbrio entre "
               "identidade e propósito. Em Quinta {n}, a essência é"),
    "Karma": ("O número de Karma reúne Síntese, Interior, Dia do Nascimento e Caminho, "
              "apontando padrões que se repetem — aquilo que esta leitura chama de tarefa "
              "a equilibrar ao longo da vida. Em Karma {n}, a essência é"),
    "Dia": ("O número do Dia do Nascimento aponta um talento natural, quase inato, que "
            "acompanha a pessoa desde cedo e costuma se manifestar sem muito esforço "
            "consciente. Em Dia {n}, a essência é"),
}

_ORDEM_CATEGORIAS = ["Interior", "Exterior", "Sintese", "Caminho", "Quinta", "Karma", "Dia"]


def texto_numero(categoria: str, numero: int) -> str:
    """Monta o parágrafo interpretativo de um número dentro de uma categoria."""
    intro = CATEGORIA_INTRO[categoria].format(n=numero)
    essencia = NUMERO_ESSENCIA.get(numero, "uma energia que foge das faixas usuais de leitura.")
    return f"{intro} {essencia}"


# ------------------------------------------------------------- Temperamentos
EIXO_FAIXAS = {
    "Mental": {
        "baixo": ("valores mais baixos aqui sugerem uma vontade mais fluida e menos "
                  "combativa, com menor necessidade de estar no comando das situações."),
        "medio": ("um valor equilibrado aqui indica alternância saudável entre tomar a "
                  "frente e ceder espaço, sem uma necessidade fixa de controle."),
        "alto": ("valores mais altos aqui indicam vontade forte, gosto por protagonismo e "
                 "facilidade em decidir — vale observar para que isso não escorregue para "
                 "controle ou autoritarismo."),
    },
    "Emocional": {
        "baixo": ("valores mais baixos aqui sugerem discrição afetiva, com preferência por "
                  "expressar sentimentos de forma mais reservada."),
        "medio": ("um valor equilibrado aqui indica capacidade de alternar entre expressar "
                  "e conter emoções, conforme o contexto."),
        "alto": ("valores mais altos aqui indicam grande sensibilidade e forte necessidade "
                 "de vínculo — vale cuidar para não se sobrecarregar cuidando demais dos "
                 "outros ou depender emocionalmente deles."),
    },
    "Físico": {
        "baixo": ("valores mais baixos aqui sugerem menor ênfase na ação prática imediata "
                  "e na relação com rotina material."),
        "medio": ("um valor equilibrado aqui indica boa combinação entre estrutura e "
                  "movimento, entre estabilidade e disposição para agir."),
        "alto": ("valores mais altos aqui indicam forte energia prática e gosto por ação "
                 "concreta — vale observar se isso não se traduz em inquietação ou pressa "
                 "excessiva."),
    },
    "Intuitivo": {
        "baixo": ("valores mais baixos aqui sugerem foco mais voltado ao concreto e ao "
                  "imediato, com menor tendência espontânea à introspecção."),
        "medio": ("um valor equilibrado aqui indica alternância saudável entre razão e "
                  "intuição na hora de tomar decisões."),
        "alto": ("valores mais altos aqui indicam forte chamado interior, sensibilidade "
                 "espiritual e humanitária — vale cuidar para que isso não vire isolamento "
                 "do mundo prático."),
    },
}


def texto_eixo(nome_eixo: str, valor: int) -> str:
    faixa = "baixo" if valor <= 2 else ("alto" if valor >= 7 else "medio")
    return EIXO_FAIXAS[nome_eixo][faixa]


# ------------------------------------------------------------------ Desafios
DESAFIO_FASE = {
    "1º": "o primeiro desafio costuma se manifestar na juventude, moldando os primeiros anos de formação da personalidade.",
    "2º": "o segundo desafio se estende por boa parte da vida adulta, sendo o pano de fundo mais constante do amadurecimento.",
    "3º": "o terceiro desafio é chamado de desafio principal, atuando com mais intensidade na fase central da vida.",
    "4º": "o quarto desafio aparece com mais força na maturidade e nos ciclos finais da vida.",
}

DESAFIO_NUMERO_TEXTO = {
    0: "Não há um obstáculo numérico específico nesta fase; o convite é para construir liberdade de escolha, sem um padrão fixo a superar.",
    1: "O desafio pede o desenvolvimento da independência e da autoconfiança, superando o medo de afirmar a própria vontade ou de agir sozinho.",
    2: "O desafio envolve lidar com a sensibilidade e a necessidade de aprovação, aprendendo cooperação sem perder a própria voz.",
    3: "O desafio está em administrar a dispersão e a autocrítica, canalizando a criatividade sem cair na superficialidade.",
    4: "O desafio pede disciplina e paciência para construir bases sólidas, superando a rigidez ou a resistência a mudanças necessárias.",
    5: "O desafio envolve equilibrar liberdade e responsabilidade, evitando a inconstância e mudanças sem direção definida.",
    6: "O desafio está em equilibrar o cuidado com os outros e o cuidado consigo, evitando excesso de sacrifício ou de controle sobre pessoas próximas.",
    7: "O desafio pede desenvolver confiança e abertura, superando tendências ao isolamento ou ao ceticismo excessivo.",
    8: "O desafio envolve lidar com poder e recursos materiais de forma equilibrada, superando o medo de fracassar ou o excesso de controle sobre resultados.",
    9: "O desafio pede a superação do apego e do idealismo excessivo, aprendendo a fechar ciclos com mais desapego e compaixão prática.",
}


def texto_desafio(posicao: str, valor: int) -> str:
    fase = DESAFIO_FASE.get(posicao, "")
    numero_txt = DESAFIO_NUMERO_TEXTO.get(valor, "Este valor foge da faixa usual de leitura.")
    return f"Na {posicao} posição, {fase} {numero_txt}"


# --------------------------------------------------------- Ausentes/Excessos
AUSENTE_TEXTO = {
    1: "convém desenvolver conscientemente a iniciativa e a autoconfiança, que aqui não vêm de forma automática.",
    2: "a diplomacia e a escuta do outro podem exigir esforço consciente para se desenvolver.",
    3: "a expressão criativa e a comunicação podem precisar de estímulo deliberado para florescer.",
    4: "organização e disciplina podem não ser instintivas, exigindo prática consciente.",
    5: "adaptar-se a mudanças pode exigir mais esforço consciente do que o natural.",
    6: "cuidar e se responsabilizar por outros pode não ser uma tendência espontânea.",
    7: "a introspecção e a análise mais profunda podem precisar ser cultivadas deliberadamente.",
    8: "lidar com dinheiro, poder e gestão prática pode exigir aprendizado consciente.",
    9: "o desapego e a visão mais ampla e compassiva podem precisar ser exercitados.",
}

EXCESSO_TEXTO = {
    1: "pode indicar uma vontade tão forte que beira o individualismo ou a teimosia.",
    2: "pode indicar sensibilidade excessiva e dependência da opinião alheia.",
    3: "pode indicar dispersão e dificuldade em manter o foco em uma só direção.",
    4: "pode indicar rigidez, apego excessivo a rotinas e resistência à mudança.",
    5: "pode indicar inquietação e dificuldade em manter compromissos de longo prazo.",
    6: "pode indicar tendência a controlar ou a se sacrificar demais pelos outros.",
    7: "pode indicar isolamento, desconfiança ou racionalização excessiva dos sentimentos.",
    8: "pode indicar foco excessivo em resultados materiais e status.",
    9: "pode indicar idealismo excessivo e dificuldade em lidar com o concreto do dia a dia.",
}


def analise_completa(nome: str, r: dict):
    """Monta a lista de seções (título, [parágrafos]) da Análise Interpretativa."""
    secoes = []

    fundamentais = [
        texto_numero("Interior", r["Interior"]),
        texto_numero("Exterior", r["Exterior"]),
        texto_numero("Sintese", r["Síntese"]),
        texto_numero("Caminho", r["Caminho"]),
        texto_numero("Quinta", r["Quinta"]),
        texto_numero("Karma", r["Soma"]),
    ]
    secoes.append(("Números Fundamentais", fundamentais))

    voc = r["Vocacao"]
    vocacao = [texto_numero("Dia", voc["Dia do Nascimento"])]
    secoes.append(("Vocação", vocacao))

    des = r["Desafios"]
    desafios_txt = [texto_desafio(pos, des[pos]) for pos in ["1º", "2º", "3º", "4º"]]
    secoes.append(("Desafios", desafios_txt))

    e = r["Eixos"]
    eixos_txt = [
        f"<b>{k.replace('Eixo ', '')} ({v}):</b> " + texto_eixo(k.replace("Eixo ", ""), v)
        for k, v in e.items()
    ]
    secoes.append(("Temperamentos", eixos_txt))

    aus_exc = []
    if r["Ausentes"]:
        partes = [f"<b>{n}</b> — {AUSENTE_TEXTO.get(n, '')}" for n in r["Ausentes"]]
        aus_exc.append("Números ausentes no nome: " + " ".join(partes))
    else:
        aus_exc.append("Não há números ausentes: todas as energias de 1 a 9 aparecem ao menos uma vez no nome.")

    if r["Excessos"]:
        partes = [f"<b>{n}</b> — {EXCESSO_TEXTO.get(n, '')}" for n in r["Excessos"]]
        aus_exc.append("Números em excesso no nome: " + " ".join(partes))
    else:
        aus_exc.append("Não há números em excesso segundo o limiar adotado nesta leitura.")
    secoes.append(("Números Ausentes e em Excesso", aus_exc))

    return secoes
