"""Estratégias de coleta de pedidos (Cenário 5, SMAC03 Grafos).

Modelo da loja:
    - N corredores paralelos, numerados 1, 2, ..., N a partir do caixa;
    - cada corredor tem comprimento L (metros);
    - corredores vizinhos estão a w metros de distância;
    - há uma travessa na frente e outra no fundo ligando os corredores;
    - o caixa fica na frente do corredor 1.

Um corredor com item do pedido é "obrigatório" e, como não sabemos a posição
do produto dentro dele, precisa ser percorrido inteiro (de uma ponta à outra).
"""


def distancia_sshape(corredores, L, w):
    """Distância total (m) da rota S-shape, do caixa de volta ao caixa.

    Parâmetros
    ----------
    corredores : lista de int
        Números dos corredores que têm itens do pedido. Pode vir fora de
        ordem ou com repetições (um corredor com 3 itens aparece 1 vez na
        conta).
    L : float
        Comprimento de cada corredor.
    w : float
        Distância entre dois corredores vizinhos.

    Fórmula (m = nº de corredores obrigatórios, a1 = primeiro, am = último):

        w*(a1 - 1)      ir do caixa, pela frente, até o 1º corredor obrigatório
      + m*L             atravessar cada corredor obrigatório uma vez (zigue-zague)
      + w*(am - a1)     andar pelas travessas entre o 1º e o último obrigatório
      + L, se m ímpar   com m ímpar terminamos no fundo: volta-se por um corredor
      + w*(am - 1)      voltar pela frente do último corredor até o caixa
    """
    # set() remove repetições; sorted() coloca em ordem crescente.
    obrigatorios = sorted(set(corredores))

    # Pedido sem itens: o separador não sai do caixa.
    if not obrigatorios:
        return 0

    if obrigatorios[0] < 1:
        raise ValueError("Corredores são numerados a partir de 1.")

    m = len(obrigatorios)
    a1 = obrigatorios[0]
    am = obrigatorios[-1]

    ida_ate_primeiro = w * (a1 - 1)
    dentro_dos_corredores = m * L
    entre_corredores = w * (am - a1)
    corredor_extra = L if m % 2 == 1 else 0
    volta_ao_caixa = w * (am - 1)

    return (ida_ate_primeiro + dentro_dos_corredores + entre_corredores
            + corredor_extra + volta_ao_caixa)
