# Coleta Eficiente de Pedidos de Supermercado Online

Projeto da disciplina **SMAC03 – Grafos** (UNIFEI, 2º semestre de 2026), referente ao Cenário 5.

O projeto investiga rotas para a coleta de pedidos de supermercado online. Como o dataset *Instacart Market Basket Analysis* não informa uma planta física da loja nem a localização exata dos produtos, o grupo utiliza um layout hipotético modelado por meio de **grafos** e compara diferentes estratégias de visita aos pontos de coleta.

> **Status:** em desenvolvimento. Entrega prevista para 22/11/2026.

---

## Integrantes

| Integrante | Papel |
|---|---|
| *Matheus Dourado* | Coordenador |
| *Renan Morais* | Modelador A |
| *Lucas Melo* | Modelador B |
| *Caio Lene* | Desenvolvedor A |
| *João Pedro Sabino* | Desenvolvedor B |

---

## As duas modelagens

### Modelo 1 — Grafo da Loja

A loja é representada por um **grafo simples**, **não direcionado** e **não ponderado** $G=(V,E)$, construído como uma grade ortogonal de **9 linhas por 15 colunas**.

Há **135 vértices**: **134 pontos hipotéticos de coleta associados aos 134 aisles (categorias de produtos)** do dataset Instacart e um **vértice adicional ($v_0$), correspondente ao caixa**, na posição (8,14) com indexação iniciada em zero.

Os **aisles são distribuídos sequencialmente na matriz**, da esquerda para a direita e de cima para baixo, agrupados por departamento.

As 246 arestas ligam somente vértices vizinhos na horizontal ou na vertical; atravessar uma aresta equivale a um passo. **Não são considerados obstáculos, diagonais, outras entradas da loja ou distâncias físicas em metros**.

A distância mínima entre dois vértices é a **distância de Manhattan**:
$$
d(u,v)=|r_u-r_v|+|c_u-c_v|
$$

Para cada pedido, os aisles distintos dos produtos solicitados definem o **conjunto de vértices obrigatórios $V_R(P)$**. A rota parte do caixa, visita esses vértices e retorna ao caixa, podendo passar por outros vértices e repetir arestas.

O problema é modelado como uma **instância do Steiner Traveling Salesman Problem (STSP)**. Na grade completa, pode-se calcular a **melhor ordem de visita por meio de um TSP utilizando as distâncias mínimas entre os vértices obrigatórios e o caixa**.

A implementação atual contempla as estratégias **ordem do carrinho, ordem aleatória, vizinho mais próximo e ótimo exato por Held-Karp**. A estratégia exata é limitada, por decisão de implementação, a pedidos de até 15 aisles distintos.

A função de custo considera a saída e o retorno ao caixa.

### Modelo 2 — Grafo de Coocorrência

O Modelo 2 estuda relações de coocorrência entre categorias de produtos e a possibilidade de utilizá-las para construir um layout alternativo.

---

## Estrutura do repositório

```
grafos-coleta-pedidos/
├── .github/
│   └── workflows/
│       └── testes.yml                 # execução automática dos testes
├── .gitignore                         # arquivos ignorados pelo Git
├── README.md                          # apresentação e documentação geral
├── pyproject.toml                     # configuração do pytest
├── data/                              # dados utilizados pelo projeto
│   └── processed/                     # dados processados
├── src/                               # código-fonte do projeto
│   ├── estrategias.py                 # estratégias de roteamento
│   ├── figura_mapa_loja.py            # geração da figura da loja
│   ├── grafo_loja.py                  # matriz 9 × 15 do supermercado
│   └── matriz_aisle_departamento.py   # associação entre aisles e departamentos
├── tests/                             # testes automatizados
│   └── test_estrategias.py            # testes das estratégias de coleta
├── results/                           # resultados dos experimentos
├── figs/                              # figuras utilizadas no relatório
├── relatorio/                         # relatório acadêmico em LaTeX
└── slides/                            # apresentação do projeto
```

Os arquivos CSV originais do dataset Instacart devem ser armazenados localmente em `data/raw/`, sem versionamento no Git.

| Pasta | Conteúdo | Responsável principal |
|---|---|---|
| `data/processed/` | Dados preparados para os experimentos | Modelador B |
| `src/` | Grafo da loja, estratégias e experimentos | Desenvolvedores A e B |
| `tests/` | Testes de distâncias, rotas e algoritmos | Desenvolvedor A |
| `results/` | Resultados dos experimentos | Desenvolvedor B |
| `figs/` | Figuras dos modelos e dos resultados | Modeladores e Desenvolvedor B |
| `relatorio/` | Relatório em LaTeX | Coordenador |
| `slides/` | Apresentação | Coordenador |

As pastas `results/` e `figs/` são destinadas, respectivamente, aos resultados dos experimentos e às figuras utilizadas no relatório e na apresentação.

---

## Como obter os dados

O dataset original **não está versionado neste repositório** devido ao volume dos arquivos e à decisão de manter os dados brutos fora do controle de versão.

1. Acesse https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis (é preciso uma conta gratuita no Kaggle).
2. Baixe e coloque em `data/raw/`:
   - `orders.csv`
   - `order_products__train.csv`
   - `products.csv`
   - `aisles.csv`
   - `departments.csv`

O arquivo `order_products__prior.csv` não é necessário: o projeto usa os pedidos do conjunto `train`.

---

## Como executar

O projeto utiliza Python. Para executar os testes automatizados, utilize os seguintes comandos na raiz do repositório:

```bash
python -m pip install pytest
python -m pytest -v
```

Para gerar a figura do grafo da loja:

```bash
python -m pip install matplotlib
python src/figura_mapa_loja.py
```

A figura gerada é salva como `grafo_loja.png` no diretório de execução.

A execução completa dos experimentos com pedidos reais depende da integração dos scripts de processamento dos dados e de geração dos resultados.

---

## Fluxo de trabalho do grupo

- O rascunho colaborativo do relatório é escrito no Google Docs. Cada integrante escreve a sua parte, e após ser finalizado e revisado, o coordenador transfere o texto aprovado para `relatorio/` em LaTeX.
- Para alterações no GitHub, cada integrante utiliza uma branch específica, realiza os commits necessários e abre um Pull Request para o coordenador revisar antes de integrar à main.
- São evitadas edições simultâneas em arquivos sob responsabilidade de outros integrantes.
- Os CSVs originais do dataset Instacart permanecem em `data/raw/` na máquina de cada integrante, sem inclusão no repositório.

---

## Entregáveis

- Relatório final em PDF: `relatorio/`
- Apresentação em slides: `slides/`
- Código-fonte: `src/` e `tests/`
- Figuras e resultados experimentais: `figs/` e `results/`