"""Estratégias de coleta de pedidos (Cenário 5, SMAC03 Grafos).

Modelo da loja (Modelo 1 do relatório):
    - a loja é uma grade de células; cada célula é um aisle do Instacart;
    - o separador anda só na vertical e na horizontal, com custo 1 por passo;
    - logo, a distância entre duas células é a distância de Manhattan;
    - a célula vazia (None) da matriz é o caixa, onde a rota começa e termina.

Ideia comum a todas as estratégias: uma estratégia só decide a ORDEM em que os
aisles do pedido são visitados. Toda função rota_* devolve essa ordem (lista de
aisle ids, sem o caixa); a distância da rota vem de custo_rota().

Todas as funções recebem um `layout` opcional (dicionário aisle -> posição).
Por padrão é o mapa atual da loja; para testar outro layout (por exemplo, o
guiado por coocorrência da Q4), basta passar outro dicionário.
"""

import random

from grafo_loja import mapa_loja

# Chave do caixa dentro do layout (os aisles são inteiros de 1 a 134).
CAIXA = "caixa"

# Limite padrão de aisles distintos para o ótimo exato (custo cresce como n² · 2ⁿ).
LIMITE_OTIMO = 15


# ---------------------------------------------------------------------------
# Layout e distâncias
# ---------------------------------------------------------------------------

def criar_layout(matriz):
    """Converte a matriz da loja em um dicionário {aisle: (linha, coluna)}.

    A célula None vira a posição do caixa, guardada na chave CAIXA.
    """
    layout = {}
    for linha, valores in enumerate(matriz):
        for coluna, aisle in enumerate(valores):
            chave = CAIXA if aisle is None else aisle
            if chave in layout:
                raise ValueError(f"{chave!r} aparece mais de uma vez na matriz.")
            layout[chave] = (linha, coluna)
    if CAIXA not in layout:
        raise ValueError("A matriz precisa de uma célula None para o caixa.")
    return layout


LAYOUT_PADRAO = criar_layout(mapa_loja)


def distancia(a, b, layout=LAYOUT_PADRAO):
    """Distância de Manhattan entre dois aisles (ou o caixa), em passos."""
    (la, ca), (lb, cb) = layout[a], layout[b]
    return abs(la - lb) + abs(ca - cb)


def custo_rota(rota, layout=LAYOUT_PADRAO):
    """Distância total de: caixa -> rota[0] -> ... -> rota[-1] -> caixa."""
    caminho = [CAIXA] + list(rota) + [CAIXA]
    return sum(distancia(caminho[i], caminho[i + 1], layout)
               for i in range(len(caminho) - 1))


def paradas(aisles, layout=LAYOUT_PADRAO):
    """Remove aisles repetidos mantendo a 1ª ocorrência; valida que existem.

    Dois produtos do mesmo aisle são uma parada só.
    """
    vistos = []
    for aisle in aisles:
        if aisle == CAIXA or aisle not in layout:
            raise ValueError(f"Aisle {aisle!r} não existe no layout.")
        if aisle not in vistos:
            vistos.append(aisle)
    return vistos


# ---------------------------------------------------------------------------
# Estratégias
# ---------------------------------------------------------------------------

def rota_carrinho(aisles, layout=LAYOUT_PADRAO):
    """Visita os aisles na ordem em que os produtos foram postos no carrinho.

    `aisles` deve vir na ordem de add_to_cart_order do Instacart. Se o mesmo
    aisle aparece de novo mais tarde, ele já foi visitado e é ignorado.
    """
    return paradas(aisles, layout)


def rota_aleatoria(aisles, semente=None, layout=LAYOUT_PADRAO):
    """Visita os aisles numa ordem sorteada (coleta sem critério).

    Use `semente` fixa para resultados reproduzíveis nos experimentos.
    """
    rota = paradas(aisles, layout)
    random.Random(semente).shuffle(rota)
    return rota


def rota_vizinho_mais_proximo(aisles, layout=LAYOUT_PADRAO):
    """Gulosa: de onde está, vai sempre ao aisle mais próximo que ainda falta.

    Empate de distância: vai ao aisle de menor id (para o resultado não
    depender da ordem da entrada).
    """
    faltam = set(paradas(aisles, layout))
    atual = CAIXA
    rota = []
    while faltam:
        proximo = min(faltam, key=lambda a: (distancia(atual, a, layout), a))
        rota.append(proximo)
        faltam.remove(proximo)
        atual = proximo
    return rota


def rota_otima(aisles, layout=LAYOUT_PADRAO, limite=LIMITE_OTIMO):
    """Rota de menor distância possível (Held-Karp, programação dinâmica).

    É o Problema do Caixeiro Viajante sobre {caixa} ∪ {aisles do pedido}.

    Ideia: C[S][j] = menor custo para sair do caixa, visitar exatamente o
    conjunto S de aisles e terminar no aisle j (j dentro de S).
        - base:        C[{j}][j] = d(caixa, j)
        - recorrência: C[S][j]   = min sobre i em S-{j} de C[S-{j}][i] + d(i, j)
        - resposta:    min sobre j de C[todos][j] + d(j, caixa)

    O conjunto S é guardado como um número binário (máscara): o bit k ligado
    significa "o k-ésimo aisle está em S". Ex.: com 3 aisles, 0b101 = {0, 2}.

    Custo: O(n² · 2ⁿ) com n = nº de aisles distintos. Acima de `limite`
    a função recusa (ValueError) em vez de travar.
    """
    pontos = sorted(paradas(aisles, layout))
    n = len(pontos)
    if n > limite:
        raise ValueError(f"Pedido com {n} aisles distintos excede o limite de {limite}.")
    if n <= 1:
        return pontos

    # Distâncias pré-calculadas: do caixa a cada ponto e entre pares de pontos.
    d_caixa = [distancia(CAIXA, p, layout) for p in pontos]
    d = [[distancia(p, q, layout) for q in pontos] for p in pontos]

    INF = float("inf")
    todos = (1 << n) - 1
    custo = [[INF] * n for _ in range(1 << n)]  # custo[mascara][j]
    veio_de = [[-1] * n for _ in range(1 << n)]  # ponto anterior a j, p/ remontar a rota

    for j in range(n):
        custo[1 << j][j] = d_caixa[j]

    # Máscaras em ordem crescente: S - {j} é sempre menor que S, já calculado.
    for mascara in range(1, todos + 1):
        for j in range(n):
            if not mascara & (1 << j) or mascara == (1 << j):
                continue
            anterior = mascara ^ (1 << j)  # S - {j}
            for i in range(n):
                if anterior & (1 << i):
                    c = custo[anterior][i] + d[i][j]
                    if c < custo[mascara][j]:
                        custo[mascara][j] = c
                        veio_de[mascara][j] = i

    # Fecha o ciclo voltando ao caixa e escolhe o melhor último ponto.
    ultimo = min(range(n), key=lambda j: custo[todos][j] + d_caixa[j])

    # Remonta a rota de trás para frente seguindo veio_de.
    rota = []
    mascara, j = todos, ultimo
    while j != -1:
        rota.append(pontos[j])
        mascara, j = mascara ^ (1 << j), veio_de[mascara][j]
    rota.reverse()
    return rota
