"""Modelo 2: grafo de coocorrência e layout alternativo na grade 9x15.

Utilizar data/raw/products.csv e data/raw/order_products__train.csv.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

from estrategias import (
    CAIXA,
    LAYOUT_PADRAO,
    criar_layout,
    custo_rota,
    rota_carrinho,
    rota_vizinho_mais_proximo,
)

RAIZ = Path(__file__).resolve().parents[1]


def carregar_pedidos(products_csv: Path, order_products_csv: Path) -> dict[int, tuple[int, ...]]:
    """Mapeia cada pedido à sequência de aisles distintos, em add_to_cart_order."""
    produto_aisle = {}
    with products_csv.open(newline="", encoding="utf-8") as arquivo:
        for linha in csv.DictReader(arquivo):
            produto_aisle[int(linha["product_id"])] = int(linha["aisle_id"])

    # Mantém a menor posição do carrinho de cada aisle dentro do pedido.
    por_pedido = defaultdict(dict)
    with order_products_csv.open(newline="", encoding="utf-8") as arquivo:
        for linha in csv.DictReader(arquivo):
            pedido = int(linha["order_id"])
            produto = int(linha["product_id"])
            ordem = int(linha["add_to_cart_order"])
            aisle = produto_aisle[produto]
            anterior = por_pedido[pedido].get(aisle)
            if anterior is None or ordem < anterior:
                por_pedido[pedido][aisle] = ordem

    return {
        pedido: tuple(a for a, _ in sorted(posicoes.items(), key=lambda x: (x[1], x[0])))
        for pedido, posicoes in por_pedido.items()
    }


def dividir_pedidos(pedidos: dict, fracao_treino=0.8, semente=2026):
    """Partição determinística por order_id, sem usar pedidos de teste no grafo."""
    if not 0 < fracao_treino < 1:
        raise ValueError("A fração de treino deve estar entre 0 e 1.")
    ids = sorted(pedidos)
    random.Random(semente).shuffle(ids)
    corte = int(len(ids) * fracao_treino)
    return ids[:corte], ids[corte:]


def construir_grafo(pedidos_treino, aisles, suporte_minimo=5):
    """Vértices=aisles; arestas ponderadas pela similaridade de Jaccard.

    Frequência f(a): pedidos que contêm a.
    Coocorrência c(a,b): pedidos que contêm simultaneamente a e b.
    Peso J(a,b) = c(a,b) / (f(a) + f(b) - c(a,b)).
    """
    if suporte_minimo < 1:
        raise ValueError("suporte_minimo precisa ser >= 1")
    conjunto_aisles = set(aisles)
    frequencias = Counter()
    pares = Counter()
    for pedido in pedidos_treino:
        unicos = sorted(set(pedido))
        if not set(unicos).issubset(conjunto_aisles):
            raise ValueError("Pedido contém aisle inexistente no layout.")
        frequencias.update(unicos)
        pares.update(combinations(unicos, 2))

    pesos = {}
    for (a, b), cooc in pares.items():
        if cooc >= suporte_minimo:
            uniao = frequencias[a] + frequencias[b] - cooc
            pesos[(a, b)] = cooc / uniao
    return frequencias, pares, pesos


def distancia_grade(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def objetivo(layout, pesos):
    """Soma do peso Jaccard multiplicado pela distância entre os aisles."""
    return sum(peso * distancia_grade(layout[a], layout[b]) for (a, b), peso in pesos.items())


def otimizar_layout(layout_inicial, pesos, max_trocas=30):
    """Busca local determinística por trocas de posição; o caixa nunca se move.

    Só aceita trocas que reduzem estritamente a função objetivo.
    """
    atual = dict(layout_inicial)
    aisles = sorted(a for a in atual if a != CAIXA)
    vizinhos = {a: {} for a in aisles}
    for (a, b), peso in pesos.items():
        vizinhos[a][b] = peso
        vizinhos[b][a] = peso
    inicial = objetivo(atual, pesos)
    trocas = 0

    for _ in range(max_trocas):
        melhor_delta, melhor_par = -1e-10, None
        for i, a in enumerate(aisles):
            pa = atual[a]
            for b in aisles[i + 1:]:
                pb = atual[b]
                delta = 0.0
                # A distância entre a e b não muda quando ambos são trocados.
                for k, peso in vizinhos[a].items():
                    if k != b:
                        pk = atual[k]
                        delta += peso * (distancia_grade(pb, pk) - distancia_grade(pa, pk))
                for k, peso in vizinhos[b].items():
                    if k != a:
                        pk = atual[k]
                        delta += peso * (distancia_grade(pa, pk) - distancia_grade(pb, pk))
                if delta < melhor_delta:
                    melhor_delta, melhor_par = delta, (a, b)
        if melhor_par is None:
            break
        a, b = melhor_par
        atual[a], atual[b] = atual[b], atual[a]
        trocas += 1

    assert atual[CAIXA] == layout_inicial[CAIXA]
    assert set(atual) == set(layout_inicial)
    assert set(atual.values()) == set(layout_inicial.values())
    final = objetivo(atual, pesos)
    if final > inicial + 1e-7:
        raise AssertionError("A otimização aumentou a função objetivo.")
    return atual, {"objetivo_inicial": inicial, "objetivo_final": final, "trocas": trocas}


def avaliar_layouts(pedidos, ids_teste, layout1, layout2):
    """Compara rotas recalculadas nos dois layouts para os mesmos pedidos."""
    resumo = {}
    for nome, estrategia in (("carrinho", rota_carrinho), ("vizinho_mais_proximo", rota_vizinho_mais_proximo)):
        custo1 = custo2 = 0
        melhor = empate = pior = 0
        for pid in ids_teste:
            pedido = pedidos[pid]
            c1 = custo_rota(estrategia(pedido, layout=layout1), layout=layout1)
            c2 = custo_rota(estrategia(pedido, layout=layout2), layout=layout2)
            custo1 += c1
            custo2 += c2
            if c2 < c1:
                melhor += 1
            elif c2 == c1:
                empate += 1
            else:
                pior += 1
        n = len(ids_teste)
        if n == 0:
            raise ValueError("Conjunto de teste vazio.")
        resumo[nome] = {
            "media_layout_original_passos": custo1 / n,
            "media_layout_coocorrencia_passos": custo2 / n,
            "reducao_percentual": 100 * (custo1 - custo2) / custo1,
            "pedidos_modelo2_melhor": melhor,
            "pedidos_empatados": empate,
            "pedidos_modelo2_pior": pior,
        }
    return resumo


def matriz_do_layout(layout, altura=9, largura=15):
    matriz = [[None] * largura for _ in range(altura)]
    for aisle, (l, c) in layout.items():
        if matriz[l][c] is not None:
            raise ValueError("Posição duplicada no layout.")
        matriz[l][c] = aisle if aisle != CAIXA else "caixa"
    if any(v is None for linha in matriz for v in linha):
        raise ValueError("Layout incompleto.")
    return [[None if v == "caixa" else v for v in linha] for linha in matriz]


def salvar_arestas(path, frequencias, pares, pesos):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["aisle_a", "aisle_b", "pedidos_ambos", "freq_a", "freq_b", "jaccard"])
        for (a, b), peso in sorted(pesos.items()):
            escritor.writerow([a, b, pares[(a, b)], frequencias[a], frequencias[b], f"{peso:.12f}"])


def main():
    parser = argparse.ArgumentParser(description="Grafo e layout por coocorrência (9x15)")
    parser.add_argument("--semente", type=int, default=2026)
    parser.add_argument("--suporte-minimo", type=int, default=5)
    parser.add_argument("--max-trocas", type=int, default=30)
    args = parser.parse_args()

    pedidos = carregar_pedidos(RAIZ / "data/raw/products.csv", RAIZ / "data/raw/order_products__train.csv")
    ids_treino, ids_teste = dividir_pedidos(pedidos, semente=args.semente)
    aisles = sorted(a for a in LAYOUT_PADRAO if a != CAIXA)
    frequencias, pares, pesos = construir_grafo((pedidos[p] for p in ids_treino), aisles, args.suporte_minimo)
    layout2, otimizacao = otimizar_layout(LAYOUT_PADRAO, pesos, args.max_trocas)
    avaliacao = avaliar_layouts(pedidos, ids_teste, LAYOUT_PADRAO, layout2)

    # Valida a compatibilidade com o código existente.
    matriz = matriz_do_layout(layout2)
    if criar_layout(matriz) != layout2:
        raise AssertionError("O layout exportado não é compatível com criar_layout.")

    destino = RAIZ / "data/processed"
    destino.mkdir(parents=True, exist_ok=True)
    salvar_arestas(destino / "grafo_coocorrencia.csv", frequencias, pares, pesos)
    (destino / "layout_coocorrencia.json").write_text(
        json.dumps({"matriz_9x15": matriz}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    resultados = {
        "pedidos_total": len(pedidos),
        "pedidos_treino": len(ids_treino),
        "pedidos_teste": len(ids_teste),
        "semente": args.semente,
        "suporte_minimo": args.suporte_minimo,
        "arestas_coocorrencia": len(pesos),
        "otimizacao": otimizacao,
        "avaliacao": avaliacao,
    }
    saida = RAIZ / "results"
    saida.mkdir(parents=True, exist_ok=True)
    (saida / "comparacao_layouts.json").write_text(
        json.dumps(resultados, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(resultados, indent=2, ensure_ascii=False))
    print("Resultados salvos em data/processed/ e results/.")


if __name__ == "__main__":
    main()