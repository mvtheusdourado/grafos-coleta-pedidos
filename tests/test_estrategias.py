"""Testes das estratégias de coleta na loja em grade (9 x 15)."""

import random
from itertools import permutations

import pytest

from estrategias import (
    CAIXA,
    LAYOUT_PADRAO,
    criar_layout,
    custo_rota,
    distancia,
    paradas,
    rota_aleatoria,
    rota_carrinho,
    rota_otima,
    rota_vizinho_mais_proximo,
)

TODOS_AISLES = sorted(a for a in LAYOUT_PADRAO if a != CAIXA)

# Loja de brinquedo: uma única linha, caixa na coluna 5, itens nos aisles 3, 6 e 10
# (o id do aisle coincide com a coluna, para facilitar a conta).
#   colunas:  0   1   2   3   4    5     6   7   8   9   10
LOJA_LINHA = [[20, 21, 22, 3, 23, None, 6, 24, 25, 26, 10]]
LAYOUT_LINHA = criar_layout(LOJA_LINHA)


def forca_bruta(aisles, layout=LAYOUT_PADRAO):
    """Menor custo testando TODAS as ordens. Só para conferir o ótimo (n pequeno)."""
    return min(custo_rota(ordem, layout) for ordem in permutations(set(aisles)))


def pedido_sorteado(n, semente):
    return random.Random(semente).sample(TODOS_AISLES, n)


# --- Layout -----------------------------------------------------------------

def test_layout_padrao_tem_134_aisles_e_o_caixa_no_canto():
    assert TODOS_AISLES == list(range(1, 135))
    assert LAYOUT_PADRAO[CAIXA] == (8, 14)
    assert LAYOUT_PADRAO[34] == (0, 0)  # canto superior esquerdo


def test_layout_recusa_aisle_repetido():
    with pytest.raises(ValueError):
        criar_layout([[1, 1, None]])


def test_layout_exige_caixa():
    with pytest.raises(ValueError):
        criar_layout([[1, 2, 3]])


# --- Distância e custo ------------------------------------------------------

def test_distancia_manhattan():
    assert distancia(34, CAIXA) == 8 + 14  # (0,0) até (8,14)
    assert distancia(100, CAIXA) == 1      # vizinho do caixa
    assert distancia(34, 34) == 0


def test_custo_rota_calculado_a_mao():
    # caixa(8,14) -> 93(0,14): 8 -> 34(0,0): 14 -> 46(8,0): 8 -> caixa: 14  = 44
    assert custo_rota([93, 34, 46]) == 44


def test_custo_rota_vazia_e_um_aisle():
    assert custo_rota([]) == 0
    assert custo_rota([34]) == 44  # ida e volta: 22 + 22


def test_paradas_remove_repetidos_e_valida():
    assert paradas([34, 100, 34, 93]) == [34, 100, 93]
    with pytest.raises(ValueError):
        paradas([999])
    with pytest.raises(ValueError):
        paradas([CAIXA])


# --- Carrinho ---------------------------------------------------------------

def test_carrinho_segue_ordem_de_insercao():
    assert rota_carrinho([46, 93, 46, 34]) == [46, 93, 34]


# --- Aleatória --------------------------------------------------------------

def test_aleatoria_e_permutacao_do_pedido():
    pedido = pedido_sorteado(10, semente=1)
    assert sorted(rota_aleatoria(pedido, semente=7)) == sorted(pedido)


def test_aleatoria_reproduzivel_com_semente():
    pedido = pedido_sorteado(10, semente=1)
    assert rota_aleatoria(pedido, semente=7) == rota_aleatoria(pedido, semente=7)
    rotas = {tuple(rota_aleatoria(pedido, semente=s)) for s in range(10)}
    assert len(rotas) > 1  # sementes diferentes dão ordens diferentes


# --- Vizinho mais próximo ---------------------------------------------------

def test_vizinho_mais_proximo_exemplo_a_mao():
    # caixa(5) -> 6: 1 -> 3: 3 (o 10 está a 4) -> 10: 7 -> caixa: 5  = 16
    rota = rota_vizinho_mais_proximo([3, 6, 10], LAYOUT_LINHA)
    assert rota == [6, 3, 10]
    assert custo_rota(rota, LAYOUT_LINHA) == 16


def test_vizinho_mais_proximo_visita_todos():
    pedido = pedido_sorteado(12, semente=3)
    assert sorted(rota_vizinho_mais_proximo(pedido)) == sorted(pedido)


# --- Ótimo exato ------------------------------------------------------------

def test_otimo_exemplo_a_mao_bate_vizinho():
    # Ótimo: caixa(5) -> 3 -> 6 -> 10 -> caixa  =  2 + 3 + 4 + 5 = 14 (< 16 do guloso)
    rota = rota_otima([3, 6, 10], LAYOUT_LINHA)
    assert custo_rota(rota, LAYOUT_LINHA) == 14


def test_otimo_casos_triviais():
    assert rota_otima([]) == []
    assert rota_otima([34, 34]) == [34]


@pytest.mark.parametrize("n", range(1, 8))
@pytest.mark.parametrize("semente", range(5))
def test_otimo_igual_forca_bruta(n, semente):
    pedido = pedido_sorteado(n, semente)
    rota = rota_otima(pedido)
    assert sorted(rota) == sorted(pedido)
    assert custo_rota(rota) == forca_bruta(pedido)


@pytest.mark.parametrize("semente", range(10))
def test_otimo_nunca_perde_para_as_heuristicas(semente):
    pedido = pedido_sorteado(10, semente)
    melhor = custo_rota(rota_otima(pedido))
    assert melhor <= custo_rota(rota_carrinho(pedido))
    assert melhor <= custo_rota(rota_aleatoria(pedido, semente=semente))
    assert melhor <= custo_rota(rota_vizinho_mais_proximo(pedido))


def test_otimo_recusa_pedido_acima_do_limite():
    with pytest.raises(ValueError):
        rota_otima(pedido_sorteado(4, semente=0), limite=3)
