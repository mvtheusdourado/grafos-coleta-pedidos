"""Responsável por gerar a figura que relaciona o custo por aisles a partir dos 10.000 pedidos analisados."""

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parents[1]
ENTRADA = RAIZ / "results" / "experimento_modelo1_amostra_por_pedido.csv"
SAIDA = RAIZ / "figs"

SERIES = {
    "carrinho_passos": "Ordem do carrinho",
    "aleatoria_media_passos": "Ordem aleatoria",
    "vizinho_passos": "Vizinho mais proximo",
    "otimo_passos": "Otimo exato (Held-Karp)",
}


def main():
    grupos = defaultdict(lambda: defaultdict(list))
    total = 0

    with ENTRADA.open(encoding="utf-8-sig", newline="") as arquivo:
        for linha in csv.DictReader(arquivo):
            total += 1
            quantidade = int(linha["aisles_distintos"])
            grupo = min(quantidade, 16)

            for campo in SERIES:
                valor = linha[campo]
                if valor:
                    grupos[grupo][campo].append(float(valor))

    if total != 10000:
        raise ValueError(f"Esperados 10.000 pedidos; encontrados {total}.")

    if sum(len(grupos[g]["carrinho_passos"]) for g in range(16, 17)) != 778:
        raise ValueError("Quantidade de pedidos com 16+ aisles inesperada.")

    fig, ax = plt.subplots(figsize=(11, 6))
    eixo_x = list(range(1, 17))

    for campo, nome in SERIES.items():
        xs = []
        ys = []

        for grupo in eixo_x:
            valores = grupos[grupo][campo]
            if valores:
                xs.append(grupo)
                ys.append(sum(valores) / len(valores))

        ax.plot(xs, ys, marker="o", markersize=4,
                linewidth=2, label=nome)

    ax.set_title("Distancia media por quantidade de aisles distintos")
    ax.set_xlabel("Aisles distintos por pedido")
    ax.set_ylabel("Distancia media (passos)")
    ax.set_xticks(eixo_x)
    ax.set_xticklabels([str(i) for i in range(1, 16)] + ["16+"])
    ax.grid(alpha=0.22)
    ax.legend()
    fig.tight_layout()

    SAIDA.mkdir(exist_ok=True)
    destino = SAIDA / "custo_por_aisles_10Kpedidos.png"
    fig.savefig(destino, dpi=220, bbox_inches="tight")
    print(f"Gerado: {destino}")

    plt.close(fig)
    print(f"Pedidos processados: {total}")
    print("Grupo 16+: 778 pedidos; sem otimo exato.")


if __name__ == "__main__":
    main()
