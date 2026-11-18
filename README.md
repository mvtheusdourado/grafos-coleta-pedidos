# Coleta Eficiente de Pedidos de Supermercado Online

Projeto da disciplina **SMAC03 – Grafos** (UNIFEI, 2º semestre de 2026), Cenário 5.

O problema estudado é o percurso do funcionário que separa um pedido de supermercado online. Hoje ele percorre os corredores sem critério definido. O projeto modela a loja e os pedidos como **grafos** e mede quanto um roteamento baseado nesses modelos reduz o percurso, usando pedidos reais do dataset *Instacart Market Basket Analysis*.

> **Status:** em desenvolvimento. Entrega em 22/11/2026.

---

## Integrantes

| Integrante | Papel |
|---|---|
| Matheus Dourado | Coordenador |
| *Lucas Melo* | Modelador A |
| *João Pedro Sabino* | Modelador B |
| *Caio Lene* | Desenvolvedor A |
| *Renan Stockler* | Desenvolvedor B |

---

## As duas modelagens

**Modelo 1, grafo da loja.** Os vértices são as pontas dos corredores e o caixa. As arestas são os corredores e os trechos das travessas, com peso em metros. Cada produto pertence a um corredor inteiro, então os corredores que têm itens do pedido viram **arestas obrigatórias**, e a melhor rota é um problema do **Carteiro Rural**.

**Modelo 2, grafo de coocorrência.** Os vértices são as categorias de produtos. As arestas ligam categorias compradas juntas, com peso dado pelo **índice de Jaccard**. Esse grafo é usado para caracterizar os pedidos e para gerar um layout alternativo da loja.

---

## Estrutura do repositório

```
grafos-coleta-pedidos/
├── README.md
├── requirements.txt         # bibliotecas Python usadas
├── .gitignore
│
├── data/
│   ├── raw/                 # CSVs originais do Instacart (não versionados)
│   └── processed/           # amostra limpa, mapeamento categoria → corredor,
│                            # divisão entre pedidos de construção e de avaliação
│
├── src/                     # código-fonte
│   └── legacy/              # simulação preliminar do modelo antigo (só referência)
│
├── tests/                   # testes automáticos
├── results/                 # CSVs com os resultados dos experimentos
├── figs/                    # figuras em PDF usadas no relatório e nos slides
│
├── relatorio/               # relatório em LaTeX (template da disciplina) e PDF final
└── slides/                  # apresentação
```

| Pasta | Conteúdo | Responsável principal |
|---|---|---|
| `data/processed/` | Dados prontos para os experimentos | Modelador B |
| `src/` | Grafo da loja, estratégias de roteamento, layout por coocorrência, experimentos | Desenvolvedores A e B |
| `tests/` | Testes de correção (distâncias, S-shape igual ao ótimo etc.) | Desenvolvedor A |
| `results/` | Números usados no relatório, gerados por código | Desenvolvedor B |
| `figs/` | Figuras dos modelos e dos resultados | Modeladores e Desenvolvedor B |
| `relatorio/` | Fonte LaTeX e PDF entregue | Coordenador |
| `slides/` | Apresentação | Coordenador |

Os números do relatório saem de `results/`, e as figuras saem de `figs/`. Nada é digitado à mão.

---

## Como obter os dados

O dataset original **não está no repositório** porque os arquivos passam do limite de tamanho do GitHub.

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

> *A preencher pelo Desenvolvedor A quando o código estiver pronto.*

```bash
pip install -r requirements.txt

# 1. preparar os dados (gera data/processed/)
# 2. rodar os experimentos (gera results/)
# 3. gerar as figuras (gera figs/)
# 4. rodar os testes
```

---

## Fluxo de trabalho do grupo

- O texto do relatório é escrito num **Google Docs compartilhado**, uma seção por pessoa. Só o coordenador passa o texto para o LaTeX em `relatorio/`.
- No Git:
  - rodar `git pull` antes de começar;
  - fazer commits pequenos, com mensagens claras;
  - **duas pessoas não editam o mesmo arquivo ao mesmo tempo**.
- Os dados originais ficam só em `data/raw/` na máquina de cada um. Nenhum arquivo acima de 100 MB vai para o repositório.

---

## Entregáveis

- Relatório em PDF: `relatorio/`
- Slides: `slides/`
- Código-fonte: `src/` e `tests/`
