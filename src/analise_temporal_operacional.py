"""Cenário 5 — perfil de pedidos e estimativa operacional.

A estimativa física não é observação real nem tempo de execução do algoritmo.
"""
from __future__ import annotations

import csv
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "data" / "raw"
RESULTADOS = RAIZ / "results"
FIGURAS = RAIZ / "figs"

# Hipóteses de cenário, NÃO medidas do Instacart.
# Altere apenas se o grupo justificar valores diferentes no relatório.
METROS_POR_PASSO = 1.5
VELOCIDADE_M_POR_S = 1.2
SEGUNDOS_POR_ITEM = 20.0
SEGUNDOS_FIXOS_POR_PEDIDO = 120.0  # preparação, conferência e embalagem
HORAS_EFETIVAS_POR_TURNO = 7.0  # disponibilidade líquida de um funcionário


def exigir_arquivo(caminho: Path) -> None:
    if not caminho.is_file():
        raise FileNotFoundError(f"Arquivo necessário não encontrado: {caminho}")


def carregar_caracterizacao():
    """Contagens de itens e aisles distintos por pedido do recorte train."""
    produtos = {}
    with (DADOS / "products.csv").open(newline="", encoding="utf-8-sig") as f:
        for linha in csv.DictReader(f):
            produtos[int(linha["product_id"])] = int(linha["aisle_id"])

    itens = Counter()
    aisles = defaultdict(set)
    with (DADOS / "order_products__train.csv").open(newline="", encoding="utf-8-sig") as f:
        for linha in csv.DictReader(f):
            pid = int(linha["order_id"])
            produto = int(linha["product_id"])
            itens[pid] += 1
            aisles[pid].add(produtos[produto])
    if not itens:
        raise ValueError("Nenhum pedido encontrado em order_products__train.csv.")
    return itens, aisles


def carregar_periodos(ids):
    """Filtra orders.csv para o mesmo recorte; campos referem-se à COMPRA."""
    dias = Counter()
    horas = Counter()
    grade = [[0] * 24 for _ in range(7)]
    encontrados = set()

    with (DADOS / "orders.csv").open(newline="", encoding="utf-8-sig") as f:
        leitor = csv.DictReader(f)
        obrigatorios = {"order_id", "order_dow", "order_hour_of_day"}
        if not obrigatorios.issubset(set(leitor.fieldnames or ())):
            raise ValueError(f"orders.csv precisa das colunas {sorted(obrigatorios)}")
        for linha in leitor:
            pid = int(linha["order_id"])
            if pid not in ids:
                continue
            if pid in encontrados:
                raise ValueError(f"order_id duplicado em orders.csv: {pid}")
            dia, hora = int(linha["order_dow"]), int(linha["order_hour_of_day"])
            if not (0 <= dia <= 6 and 0 <= hora <= 23):
                raise ValueError(f"Dia ou hora fora da faixa no pedido {pid}.")
            encontrados.add(pid)
            dias[dia] += 1
            horas[hora] += 1
            grade[dia][hora] += 1

    faltantes = len(ids) - len(encontrados)
    if faltantes:
        raise ValueError(f"orders.csv não contém {faltantes} dos pedidos do recorte train.")
    return dias, horas, grade


def estimar_operacao(avaliacao, media_itens):
    """Converte distâncias médias em estimativas de tempo/capacidade, não medidas."""
    modelos = {}
    for estrategia, indicadores in avaliacao.items():
        modelos[estrategia] = {}
        for rotulo, chave in (
            ("layout_original", "media_layout_original_passos"),
            ("layout_coocorrencia", "media_layout_coocorrencia_passos"),
        ):
            passos = float(indicadores[chave])
            segundos_deslocamento = passos * METROS_POR_PASSO / VELOCIDADE_M_POR_S
            segundos_separacao = media_itens * SEGUNDOS_POR_ITEM
            total = segundos_deslocamento + segundos_separacao + SEGUNDOS_FIXOS_POR_PEDIDO
            capacidade = math.floor(HORAS_EFETIVAS_POR_TURNO * 3600 / total)
            modelos[estrategia][rotulo] = {
                "distancia_media_passos": round(passos, 4),
                "deslocamento_estimado_segundos": round(segundos_deslocamento, 2),
                "separacao_estimada_segundos": round(segundos_separacao, 2),
                "tempo_total_estimado_minutos": round(total / 60, 3),
                "pedidos_por_turno_estimados": capacidade,
            }
    return modelos


def gerar_figura(grade, dias, horas, total):
    FIGURAS.mkdir(parents=True, exist_ok=True)
    fig, eixos = plt.subplots(1, 2, figsize=(14, 5.2), layout="constrained")
    fig.suptitle("Distribuição temporal dos pedidos — recorte Instacart train", fontsize=14, fontweight="bold")

    im = eixos[0].imshow(grade, cmap="Blues", aspect="auto", interpolation="nearest")
    eixos[0].set_title("Pedidos por dia (código) e hora")
    eixos[0].set_xlabel("Hora em que o pedido foi realizado")
    eixos[0].set_ylabel("order_dow (0 a 6)")
    eixos[0].set_xticks(range(0, 24, 2))
    eixos[0].set_yticks(range(7))
    fig.colorbar(im, ax=eixos[0], shrink=.80, label="Quantidade de pedidos")

    eixos[1].bar(range(24), [horas[h] / total * 100 for h in range(24)], color="#47749F")
    eixos[1].set_title("Participação por hora no recorte")
    eixos[1].set_xlabel("Hora em que o pedido foi realizado")
    eixos[1].set_ylabel("Percentual dos pedidos (%)")
    eixos[1].set_xticks(range(0, 24, 2))
    eixos[1].grid(axis="y", alpha=.2)
    eixos[1].set_axisbelow(True)

    fig.text(.01, -.015,
             "Fonte: Instacart, orders.csv combinado a order_products__train.csv. "
             "Horário de compra não equivale ao de coleta. "
             "Códigos 0–6 sem atribuir nomes de dias.",
             fontsize=8, color="#455468")
    fig.savefig(
        FIGURAS / "padroes_temporais.png",
        dpi=190,
        bbox_inches="tight")
    plt.close(fig)

def main():
    for nome in ("products.csv", "order_products__train.csv", "orders.csv"):
        exigir_arquivo(DADOS / nome)
    comparacao_path = RESULTADOS / "comparacao_layouts.json"
    exigir_arquivo(comparacao_path)
    comparacao = json.loads(comparacao_path.read_text(encoding="utf-8"))
    if "avaliacao" not in comparacao:
        raise ValueError("comparacao_layouts.json sem a seção 'avaliacao'.")

    itens, aisles = carregar_caracterizacao()
    ids = set(itens)
    dias, horas, grade = carregar_periodos(ids)

    # Reproduz exatamente a divisão 80/20 e a semente do Modelo 2.
    ids_ordenados = sorted(ids)
    semente = int(comparacao["semente"])
    random.Random(semente).shuffle(ids_ordenados)
    n_treino = int(len(ids_ordenados) * 0.8)
    ids_teste = ids_ordenados[n_treino:]
    if len(ids) != int(comparacao["pedidos_total"]) or len(ids_teste) != int(comparacao["pedidos_teste"]):
        raise ValueError("Recorte de pedidos difere do experimento de coocorrência.")

    media_itens_teste = sum(itens[i] for i in ids_teste) / len(ids_teste)
    media_aisles_teste = sum(len(aisles[i]) for i in ids_teste) / len(ids_teste)
    total = len(ids)

    saida = {
        "escopo": "Somente pedidos de order_products__train.csv (não todo orders.csv)",
        "periodo": "Dia e hora da realização dos pedidos, não da coleta",
        "pedidos_analisados": total,
        "pedidos_teste_operacional": len(ids_teste),
        "media_itens_por_pedido_todos": round(sum(itens.values()) / total, 4),
        "media_aisles_distintos_todos": round(sum(map(len, aisles.values())) / total, 4),
        "media_itens_por_pedido_teste": round(media_itens_teste, 4),
        "media_aisles_distintos_teste": round(media_aisles_teste, 4),
        "pedidos_por_dia_codigo_0_a_6": {str(i): dias[i] for i in range(7)},
        "pedidos_por_hora_0_a_23": {str(i): horas[i] for i in range(24)},
        "hipoteses_operacionais_nao_observadas": {
            "metros_por_passo_de_grade": METROS_POR_PASSO,
            "velocidade_metros_por_segundo": VELOCIDADE_M_POR_S,
            "segundos_por_item": SEGUNDOS_POR_ITEM,
            "segundos_fixos_por_pedido": SEGUNDOS_FIXOS_POR_PEDIDO,
            "horas_efetivas_por_turno": HORAS_EFETIVAS_POR_TURNO,
            "funcionarios": 1,
        },
        "estimativas_por_estrategia_e_layout": estimar_operacao(comparacao["avaliacao"], media_itens_teste),
        "limitacoes": [
            "A hora do pedido não informa a hora da coleta física.",
            "A grade 9x15 é hipotética; metros por passo são premissa, não medida.",
            "Velocidade, tempo por item, preparo e horas efetivas são premissas ilustrativas.",
            "Capacidade é idealizada por funcionário, sem variabilidade, congestionamento ou demanda.",
            "As métricas operacionais usam as mesmas distâncias médias do conjunto de teste do Modelo 2.",
            "A capacidade por turno é estimativa e não resultado observado na operação Instacart.",
        ],
    }
    RESULTADOS.mkdir(parents=True, exist_ok=True)
    (RESULTADOS / "analise_temporal_operacional.json").write_text(
        json.dumps(saida, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    gerar_figura(grade, dias, horas, total)

    print(f"Pedidos no recorte: {total}; pedidos de teste: {len(ids_teste)}")
    print(f"Média de itens/teste: {media_itens_teste:.2f}; aisles distintos/teste: {media_aisles_teste:.2f}")
    print(f"Hora com mais pedidos: {max(range(24), key=lambda h: horas[h]):02d}h")
    for nome, variantes in saida["estimativas_por_estrategia_e_layout"].items():
        print(f"\nEstratégia: {nome}")
        for variante, valores in variantes.items():
            print(f"  {variante}: {valores['tempo_total_estimado_minutos']:.2f} min/pedido; "
                  f"{valores['pedidos_por_turno_estimados']} pedidos/turno (estimados)")
    print("\nArquivo: results/analise_temporal_operacional.json")
    print("Figuras: figs/padroes_temporais.png")
    print("AVISO: tempo e capacidade são estimativas sob hipóteses, não observações reais.")

if __name__ == "__main__":
    main()
