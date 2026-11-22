"""Testes do Modelo 2 sem depender dos CSVs reais do Instacart."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from estrategias import CAIXA, criar_layout
from modelo_coocorrencia import (
    avaliar_layouts,
    construir_grafo,
    dividir_pedidos,
    matriz_do_layout,
    objetivo,
    otimizar_layout,
)


def test_jaccard_por_pedido_e_nao_por_item():
    pedidos = [(1, 1, 2), (1, 3), (2, 3), (2,)]
    frequencias, pares, pesos = construir_grafo(pedidos, [1, 2, 3], suporte_minimo=1)
    assert frequencias[1] == 2
    assert frequencias[2] == 3
    assert pares[(1, 2)] == 1
    assert abs(pesos[(1, 2)] - 0.25) < 1e-12
    assert abs(pesos[(1, 3)] - (1 / 3)) < 1e-12


def test_otimizacao_preserva_caixa_e_vertices():
    padrao = criar_layout([[1, 2, 3], [4, 5, None]])
    pesos = {(1, 5): 0.8, (2, 4): 0.6, (1, 3): 0.2}
    novo, info = otimizar_layout(padrao, pesos, max_trocas=10)
    assert novo[CAIXA] == (1, 2)
    assert set(novo) == set(padrao)
    assert set(novo.values()) == set(padrao.values())
    assert objetivo(novo, pesos) <= objetivo(padrao, pesos)
    assert criar_layout(matriz_do_layout(novo, 2, 3)) == novo
    assert info["objetivo_final"] <= info["objetivo_inicial"]


def test_divisao_deterministica_sem_vazamento():
    pedidos = {i: (1, 2) for i in range(1, 101)}
    a, b = dividir_pedidos(pedidos, semente=2026)
    c, d = dividir_pedidos(pedidos, semente=2026)
    assert (a, b) == (c, d)
    assert len(a) == 80 and len(b) == 20
    assert set(a).isdisjoint(b)


def test_comparacao_mesmo_layout_sem_ganho():
    layout = criar_layout([[1, 2, 3], [4, 5, None]])
    pedidos = {1: (1, 3, 4), 2: (2, 4), 3: (5,)}
    r = avaliar_layouts(pedidos, sorted(pedidos), layout, layout)
    for v in r.values():
        assert v["reducao_percentual"] == 0
        assert v["pedidos_empatados"] == 3