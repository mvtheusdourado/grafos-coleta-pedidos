"""Testes para o experimento do Modelo 1."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from experimento_modelo1 import avaliar_pedido, carregar_pedidos, resumir


def test_mesma_instancia_todas_as_estrategias():
    dados = avaliar_pedido(25, (1, 13, 48, 21), 10, 15)
    assert dados["otimo_passos"] <= dados["vizinho_passos"]
    assert dados["otimo_passos"] <= dados["carrinho_passos"]
    assert dados["otimo_passos"] <= dados["aleatoria_media_passos"]


def test_resumo_comparacao_fechada():
    linhas = [avaliar_pedido(1, (1, 2), 3, 15), avaliar_pedido(2, (1, 25, 3), 3, 15)]
    resumo = resumir(linhas, 3, 15, False)
    assert sum(resumo["comparacao_vizinho_carrinho"].values()) == 2
    assert resumo["pedidos_com_otimo"] == 2


def test_parser_aisles_distintos_ordem_primeira_compra(tmp_path):
    p = tmp_path / "products.csv"
    p.write_text("product_id,aisle_id\n1,8\n2,12\n3,8\n", encoding="utf-8")
    i = tmp_path / "order_products__train.csv"
    i.write_text("order_id,product_id,add_to_cart_order\n2,2,4\n2,1,2\n2,3,3\n", encoding="utf-8")
    assert carregar_pedidos(p, i) == {2: (8, 12)}
