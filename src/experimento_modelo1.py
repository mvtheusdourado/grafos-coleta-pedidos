"""Reproduz a comparação das quatro estratégias do Modelo 1 nos pedidos Instacart."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

from estrategias import (
    LIMITE_OTIMO,
    custo_rota,
    rota_aleatoria,
    rota_carrinho,
    rota_otima,
    rota_vizinho_mais_proximo,
)

RAIZ = Path(__file__).resolve().parents[1]


def carregar_pedidos(products_csv: Path, itens_csv: Path) -> dict[int, tuple[int, ...]]:
    """Retorna aisles distintos em ordem da primeira inserção no carrinho."""
    for caminho in (products_csv, itens_csv):
        if not caminho.is_file():
            raise FileNotFoundError(f"Arquivo de entrada não encontrado: {caminho}")

    produto_aisle = {}
    with products_csv.open(encoding="utf-8-sig", newline="") as arquivo:
        for linha in csv.DictReader(arquivo):
            produto_aisle[int(linha["product_id"])] = int(linha["aisle_id"])

    posicoes = defaultdict(dict)
    with itens_csv.open(encoding="utf-8-sig", newline="") as arquivo:
        for linha in csv.DictReader(arquivo):
            pid = int(linha["order_id"])
            produto = int(linha["product_id"])
            ordem = int(linha["add_to_cart_order"])
            if produto not in produto_aisle:
                raise ValueError(f"product_id ausente em products.csv: {produto}")
            aisle = produto_aisle[produto]
            anterior = posicoes[pid].get(aisle)
            if anterior is None or ordem < anterior:
                posicoes[pid][aisle] = ordem

    return {
        pid: tuple(a for a, _ in sorted(mapa.items(), key=lambda x: (x[1], x[0])))
        for pid, mapa in posicoes.items()
    }


def avaliar_pedido(pid: int, aisles: tuple[int, ...], sorteios: int, limite_otimo: int):
    """Aplica as estratégias ao MESMO pedido e devolve os custos em passos."""
    if sorteios <= 0:
        raise ValueError("sorteios deve ser positivo")
    carrinho = custo_rota(rota_carrinho(aisles))
    vizinho = custo_rota(rota_vizinho_mais_proximo(aisles))
    aleatoria = sum(
        custo_rota(rota_aleatoria(aisles, semente=pid * 1000 + k))
        for k in range(sorteios)
    ) / sorteios
    otimo = custo_rota(rota_otima(aisles, limite=limite_otimo)) if len(aisles) <= limite_otimo else None
    if otimo is not None and (otimo > carrinho or otimo > vizinho or otimo > aleatoria + 1e-8):
        raise AssertionError(f"Ótimo maior que outra estratégia no pedido {pid}")
    return {
        "order_id": pid,
        "aisles_distintos": len(aisles),
        "carrinho_passos": carrinho,
        "aleatoria_media_passos": aleatoria,
        "vizinho_passos": vizinho,
        "otimo_passos": otimo,
        "vizinho_melhor_que_carrinho": vizinho < carrinho,
        "vizinho_empata_carrinho": vizinho == carrinho,
        "vizinho_pior_que_carrinho": vizinho > carrinho,
        "vizinho_empata_otimo": otimo is not None and vizinho == otimo,
        "gap_vizinho_pct": 100 * (vizinho / otimo - 1) if otimo else None,
    }


def resumir(linhas, sorteios: int, limite_otimo: int, completo: bool):
    """Médias e comparações pareadas; não mistura pedidos sem ótimo no gap."""
    n = len(linhas)
    if not n:
        raise ValueError("Não há pedidos para avaliar.")
    medias = {
        chave: sum(linha[chave] for linha in linhas) / n
        for chave in ("carrinho_passos", "aleatoria_media_passos", "vizinho_passos")
    }
    com_otimo = [linha for linha in linhas if linha["otimo_passos"] is not None]
    contagem = Counter(linha["aisles_distintos"] for linha in linhas)
    return {
        "escopo": "order_products__train.csv / products.csv",
        "resultado_completo_do_recorte": completo,
        "pedidos": n,
        "sorteios_aleatorios_por_pedido": sorteios,
        "semente_sorteio": "order_id * 1000 + indice (0 a sorteios-1)",
        "limite_otimo_aisles_distintos": limite_otimo,
        "pedidos_com_otimo": len(com_otimo),
        "medias_passos": medias,
        "comparacao_vizinho_carrinho": {
            "melhor": sum(l["vizinho_melhor_que_carrinho"] for l in linhas),
            "empate": sum(l["vizinho_empata_carrinho"] for l in linhas),
            "pior": sum(l["vizinho_pior_que_carrinho"] for l in linhas),
        },
        "gap_medio_vizinho_pct_entre_pedidos_com_otimo": (
            sum(l["gap_vizinho_pct"] for l in com_otimo) / len(com_otimo)
            if com_otimo else None
        ),
        "vizinho_igual_otimo_pct_entre_pedidos_com_otimo": (
            100 * sum(l["vizinho_empata_otimo"] for l in com_otimo) / len(com_otimo)
            if com_otimo else None
        ),
        "quantidades_por_aisles_distintos": {str(i): contagem[i] for i in sorted(contagem)},
        "unidade": "passos na grade 9 x 15, sem conversão física",
        "observacao": "Tempo de execução não é tempo físico de coleta."
    }


def executar(max_pedidos: int | None, sorteios: int, limite_otimo: int):
    if max_pedidos is not None and max_pedidos <= 0:
        raise ValueError("--max-pedidos precisa ser positivo")
    if sorteios <= 0:
        raise ValueError("--sorteios precisa ser positivo")
    if limite_otimo < 1 or limite_otimo > LIMITE_OTIMO:
        raise ValueError(f"--limite-otimo deve estar entre 1 e {LIMITE_OTIMO}")

    dados = RAIZ / "data" / "raw"
    pedidos = carregar_pedidos(dados / "products.csv", dados / "order_products__train.csv")
    ids = sorted(pedidos)
    if max_pedidos is not None:
        ids = ids[:max_pedidos]
    if not ids:
        raise ValueError("Nenhum pedido encontrado.")

    total = len(ids)
    linhas = []
    for i, pid in enumerate(ids, 1):
        linhas.append(avaliar_pedido(pid, pedidos[pid], sorteios, limite_otimo))
        if i % 1000 == 0 or i == total:
            print(f"Processados {i}/{total} pedidos", flush=True)

    completo = max_pedidos is None or total == len(pedidos)
    resumo = resumir(linhas, sorteios, limite_otimo, completo)
    pasta = RAIZ / "results"
    pasta.mkdir(exist_ok=True)
    sufixo = "" if completo else "_amostra"
    base = f"experimento_modelo1{sufixo}"
    csv_saida = pasta / f"{base}_por_pedido.csv"
    with csv_saida.open("w", newline="", encoding="utf-8") as arquivo:
        campos = list(linhas[0])
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(linhas)
    json_saida = pasta / f"{base}_resumo.json"
    json_saida.write_text(json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
    print(f"Saídas: {csv_saida.relative_to(RAIZ)} e {json_saida.relative_to(RAIZ)}")


def main():
    parser = argparse.ArgumentParser(description="Experimento reproduzível de roteamento — Modelo 1")
    parser.add_argument("--max-pedidos", type=int, help="Testar somente os primeiros N order_ids")
    parser.add_argument("--sorteios", type=int, default=200, help="Número de rotas aleatórias por pedido")
    parser.add_argument("--limite-otimo", type=int, default=LIMITE_OTIMO, help="Máximo de aisles para Held-Karp")
    args = parser.parse_args()
    executar(args.max_pedidos, args.sorteios, args.limite_otimo)


if __name__ == "__main__":
    main()
