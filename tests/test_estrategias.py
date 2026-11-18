"""Testes de distancia_sshape. Parâmetros de exemplo: N=8, L=20, w=3."""

import pytest

from estrategias import distancia_sshape

N, L, W = 8, 20, 3


def test_exemplo_calculado_a_mao():
    # Pedido com itens nos corredores 2, 5 e 7 -> m=3 (ímpar), a1=2, am=7.
    #   caixa -> corredor 2 pela frente:  3*(2-1) =  3
    #   percorrer 3 corredores:           3*20    = 60
    #   travessas entre 2 e 7:            3*(7-2) = 15
    #   m ímpar, terminou no fundo:       + 20    = 20
    #   frente do corredor 7 -> caixa:    3*(7-1) = 18
    #                                     total   = 116
    assert distancia_sshape([2, 5, 7], L, W) == 116


def test_m_par():
    # Corredores 3 e 6: m=2, a1=3, am=6.
    # 3*2 + 2*20 + 3*3 + 0 + 3*5 = 6 + 40 + 9 + 0 + 15 = 70
    assert distancia_sshape([3, 6], L, W) == 70


def test_m_impar():
    # Corredores 1, 4 e 8: m=3, a1=1, am=8.
    # 0 + 3*20 + 3*7 + 20 + 3*7 = 0 + 60 + 21 + 20 + 21 = 122
    assert distancia_sshape([1, 4, 8], L, W) == 122


def test_um_unico_corredor_no_caixa():
    # Só o corredor 1: entra, vai ao fundo e volta pelo mesmo corredor.
    # 0 + 20 + 0 + 20 + 0 = 40
    assert distancia_sshape([1], L, W) == 40


def test_um_unico_corredor_longe_do_caixa():
    # Só o corredor 4: 3*3 + 20 + 0 + 20 + 3*3 = 58
    assert distancia_sshape([4], L, W) == 58


def test_ordem_e_repeticoes_nao_importam():
    assert distancia_sshape([7, 2, 5, 5, 2], L, W) == distancia_sshape([2, 5, 7], L, W)


def test_pedido_vazio():
    assert distancia_sshape([], L, W) == 0


def test_corredor_invalido():
    with pytest.raises(ValueError):
        distancia_sshape([0, 3], L, W)


@pytest.mark.parametrize("corredores", [
    [1], [8], [2, 3], [1, 8], [2, 5, 7], [1, 2, 3, 4], list(range(1, N + 1)),
])
def test_bate_com_forma_fechada_do_relatorio(corredores):
    # Forma equivalente (Seção 3 do relatório): 2w*(am-1) + L*(m arredondado p/ par).
    m = len(corredores)
    m_par = m + (m % 2)
    esperado = 2 * W * (max(corredores) - 1) + L * m_par
    assert distancia_sshape(corredores, L, W) == esperado
