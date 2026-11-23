"""Figura científica dos layouts."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle

from grafo_loja import mapa_loja

RAIZ = Path(__file__).resolve().parents[1]
LINHAS, COLUNAS = 9, 15
FUNDO = "#FFFFFF"
TEXTO = "#1F2937"
SECUNDARIA = "#526276"
AZUL = "#1D4ED8"
AZUL_CLARO = "#DDEAFE"
NEUTRO = "#F4F6F8"
GRADE = "#D1D9E4"
CAIXA = "#24354D"


def validar_matriz(matriz: list, nome: str) -> None:
    if len(matriz) != LINHAS or any(len(linha) != COLUNAS for linha in matriz):
        raise ValueError(f"{nome}: dimensões diferentes de 9 × 15.")
    valores = [valor for linha in matriz for valor in linha]
    if len(valores) != 135 or valores.count(None) != 1:
        raise ValueError(f"{nome}: esperados 134 aisles e um caixa.")
    if set(v for v in valores if v is not None) != set(range(1, 135)):
        raise ValueError(f"{nome}: aisles precisam ser únicos, de 1 a 134.")
    if matriz[8][14] is not None:
        raise ValueError(f"{nome}: o caixa deve permanecer em (8, 14).")


def desenhar_layout(eixo, matriz, original, titulo, legenda) -> None:
    for linha in range(LINHAS):
        for coluna in range(COLUNAS):
            aisle = matriz[linha][coluna]
            mudou = original[linha][coluna] != aisle
            if aisle is None:
                cor = CAIXA
                texto = "CX"
                cor_texto = FUNDO
            else:
                cor = AZUL_CLARO if mudou else NEUTRO
                texto = str(aisle)
                cor_texto = TEXTO

            eixo.add_patch(Rectangle(
                (coluna, linha), 1, 1, linewidth=0.8,
                edgecolor=FUNDO, facecolor=cor,
            ))
            eixo.text(
                coluna + .5, linha + .5, texto,
                ha="center", va="center", fontsize=8.1,
                fontweight="bold" if aisle is None or mudou else "normal",
                color=cor_texto,
            )

    # Borda externa e posicionamento idêntico dos dois painéis.
    eixo.add_patch(Rectangle(
        (0, 0), COLUNAS, LINHAS, facecolor="none",
        edgecolor=GRADE, linewidth=1.0,
    ))
    eixo.set_xlim(0, COLUNAS)
    eixo.set_ylim(LINHAS, 0)
    eixo.set_aspect("equal")
    eixo.axis("off")
    eixo.set_title(titulo, loc="left", color=TEXTO, fontsize=13,
                   fontweight="bold", pad=26)
    eixo.text(0, -0.25, legenda, fontsize=9, color=SECUNDARIA,
              ha="left", va="bottom")


def main() -> None:
    arquivo_layout = RAIZ / "data" / "processed" / "layout_coocorrencia.json"
    arquivo_resultados = RAIZ / "results" / "comparacao_layouts.json"
    if not arquivo_layout.is_file():
        raise FileNotFoundError(f"Não encontrado: {arquivo_layout}")
    if not arquivo_resultados.is_file():
        raise FileNotFoundError(f"Não encontrado: {arquivo_resultados}")

    original = mapa_loja
    alternativo = json.loads(arquivo_layout.read_text(encoding="utf-8"))["matriz_9x15"]
    resultados = json.loads(arquivo_resultados.read_text(encoding="utf-8"))
    validar_matriz(original, "Layout original")
    validar_matriz(alternativo, "Layout alternativo")
    alteradas = sum(
        original[r][c] != alternativo[r][c]
        for r in range(LINHAS) for c in range(COLUNAS)
    )

    plt.rcParams.update({"font.family": "DejaVu Sans", "savefig.facecolor": FUNDO})
    fig, eixos = plt.subplots(1, 2, figsize=(16, 7.0), facecolor=FUNDO)
    fig.subplots_adjust(left=.035, right=.965, bottom=.19, top=.79, wspace=.07)
    fig.text(.035, .955, "COMPARAÇÃO DOS LAYOUTS DA LOJA", fontsize=19,
             fontweight="bold", color=TEXTO, ha="left")
    fig.text(.035, .910,
             "Mesma grade 9 × 15 · 134 corredores (aisles) · caixa fixo no canto inferior direito",
             fontsize=11, color=SECUNDARIA, ha="left")

    desenhar_layout(eixos[0], original, original,
                   "A  |  Layout original", "Distribuição inicial por departamentos")
    desenhar_layout(eixos[1], alternativo, original,
                   "B  |  Layout por coocorrência",
                   f"Busca local com {resultados['otimizacao']['trocas']} trocas aceitas")

    marcadores = [
        Patch(facecolor=NEUTRO, edgecolor=GRADE, label="Posição preservada"),
        Patch(facecolor=AZUL_CLARO, edgecolor=GRADE, label="Aisle em posição diferente"),
        Patch(facecolor=CAIXA, edgecolor=CAIXA, label="Caixa / partida e chegada"),
    ]
    fig.legend(handles=marcadores, loc="lower center", bbox_to_anchor=(.5, .122),
               ncol=3, frameon=False, fontsize=10,
               columnspacing=2.8, handlelength=1.5)

    resultados_avaliacao = resultados["avaliacao"]
    carrinho = resultados_avaliacao["carrinho"]["reducao_percentual"]
    vizinho = resultados_avaliacao["vizinho_mais_proximo"]["reducao_percentual"]
    reducoes = (
        f"carrinho {carrinho:.2f}% · vizinho mais próximo {vizinho:.2f}%"
    ).replace(".", ",")
    fig.text(.035, .055,
             f"{alteradas} das 134 posições de aisles foram alteradas. "
             f"Redução média no conjunto de teste: {reducoes}.",
             ha="left", fontsize=10, color=TEXTO)
    fig.text(.035, .025,
             "Distâncias em passos de grade (Manhattan). Modelo de loja hipotético, não planta física real.",
             ha="left", fontsize=9, color=SECUNDARIA)


    pasta_saida = RAIZ / "figs"
    pasta_saida.mkdir(parents=True, exist_ok=True)

    png = pasta_saida / "comparacao_layouts.png"
    fig.savefig(png, dpi=220, facecolor=FUNDO)
    plt.close(fig)

    print(f"Figura PNG: {png}")
    print(f"Posições alteradas: {alteradas} de 134; caixa fixo.")

if __name__ == "__main__":
    main()
