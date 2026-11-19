"""Gera a figura do grafo-grade da loja (9 x 15).

- Atrás: ilhas quadradas coloridas (cor do departamento) com nº e nome do corredor.
- Na frente: grafo-grade (cada vértice conecta com os 4 vizinhos adjacentes).
- Legenda: [bolinha com a cor] [nº do depto] [nome do depto].
- Última célula (canto inferior direito) = "PARTIDA".

Uso:  python figura_mapa_loja.py   ->  gera grafo_loja.png
"""
import re
import textwrap

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

COLS, ROWS = 15, 9  # 15 colunas x 9 linhas

DADOS = """
[1 - frozen]
[34] [frozen meat seafood]
[37] [ice cream ice]
[38] [frozen meals]
[42] [frozen vegan vegetarian]
[52] [frozen breakfast]
[58] [frozen breads doughs]
[79] [frozen pizza]
[113] [frozen juice]
[116] [frozen produce]
[119] [frozen dessert]
[129] [frozen appetizers sides]

[2 - other]
[6] [other]

[3 - bakery]
[8] [bakery desserts]
[43] [buns rolls]
[93] [breakfast bakery]
[112] [bread]
[128] [tortillas flat bread]

[4 - produce]
[16] [fresh herbs]
[24] [fresh fruits]
[32] [packaged produce]
[83] [fresh vegetables]
[123] [packaged vegetables fruits]

[5 - alcohol]
[27] [beers coolers]
[28] [red wines]
[62] [white wines]
[124] [spirits]
[134] [specialty wines champagnes]

[6 - international]
[30] [latino foods]
[33] [kosher foods]
[66] [asian foods]
[76] [indian foods]

[7 - beverages]
[26] [coffee]
[31] [refrigerated]
[64] [energy sports drinks]
[77] [soft drinks]
[90] [cocoa drink mixes]
[94] [tea]
[98] [juice nectars]
[115] [water seltzer sparkling water]

[8 - pets]
[40] [dog food care]
[41] [cat food care]

[9 - dry goods pasta]
[4] [instant foods]
[9] [pasta sauce]
[12] [fresh pasta]
[63] [grains rice dried goods]
[131] [dry pasta]

[10 - bulk]
[18] [bulk dried fruits vegetables]
[68] [bulk grains rice dried goods]

[11 - personal care]
[11] [cold flu allergy]
[20] [oral hygiene]
[22] [hair care]
[25] [soap]
[44] [eye ear care]
[47] [vitamins supplements]
[55] [shave needs]
[65] [protein meal replacements]
[70] [digestion]
[73] [facial care]
[80] [deodorants]
[109] [skin care]
[118] [first aid]
[126] [feminine care]
[127] [body lotions soap]
[132] [beauty]
[133] [muscles joints pain relief]

[12 - meat seafood]
[7] [packaged meat]
[15] [packaged seafood]
[35] [poultry counter]
[39] [seafood counter]
[49] [packaged poultry]
[106] [hot dogs bacon sausage]
[122] [meat counter]

[13 - pantry]
[5] [marinades meat preparation]
[17] [baking ingredients]
[19] [oils vinegars]
[29] [honeys syrups nectars]
[51] [preserved dips spreads]
[72] [condiments]
[88] [spreads]
[89] [salad dressing toppings]
[97] [baking supplies decor]
[104] [spices seasonings]
[105] [doughs gelatins bake mixes]
[110] [pickled goods olives]

[14 - breakfast]
[48] [breakfast bars pastries]
[57] [granola]
[121] [cereal]
[130] [hot cereal pancake mixes]

[15 - canned goods]
[59] [canned meals beans]
[69] [soup broth bouillon]
[81] [canned jarred vegetables]
[95] [canned meat seafood]
[99] [canned fruit applesauce]

[16 - dairy eggs]
[2] [specialty cheeses]
[21] [packaged cheese]
[36] [butter]
[53] [cream]
[71] [refrigerated pudding desserts]
[84] [milk]
[86] [eggs]
[91] [soy lactosefree]
[108] [other creams cheeses]
[120] [yogurt]

[17 - household]
[10] [kitchen supplies]
[54] [paper goods]
[60] [trash bags liners]
[74] [dish detergents]
[75] [laundry]
[85] [food storage]
[87] [more household]
[101] [air fresheners candles]
[111] [plates bowls cups flatware]
[114] [cleaning products]

[18 - babies]
[56] [diapers wipes]
[82] [baby accessories]
[92] [baby food formula]
[102] [baby bath body care]

[19 - snacks]
[3] [energy granola bars]
[23] [popcorn jerky]
[45] [candy chocolate]
[46] [mint gum]
[50] [fruit vegetable snacks]
[61] [cookies cakes]
[78] [crackers]
[103] [ice cream toppings]
[107] [chips pretzels]
[117] [nuts seeds dried fruit]
[125] [trail mix snack mix]

[20 - deli]
[1] [prepared soups salads]
[13] [prepared meals]
[14] [tofu meat alternatives]
[67] [fresh dips tapenades]
[96] [lunch meat]

[21 - missing]
[100] [missing]
"""

# 21 cores distintas, uma por departamento
CORES = [
    "#1f77b4", "#ff7f0e", "#e0b068", "#2ca02c", "#9b1c31", "#d62728",
    "#17becf", "#8c564b", "#bcbd22", "#7f7f7f", "#e377c2", "#c0392b",
    "#f1c40f", "#ffbb78", "#9467bd", "#aec7e8", "#16a085", "#ff9896",
    "#d35400", "#98df8a", "#555555",
]


def parse(texto):
    """Devolve (lista de deptos [(num, nome)], lista de corredores [(depto, id, nome)])."""
    deptos, corredores, atual = [], [], None
    for linha in texto.strip().splitlines():
        linha = linha.strip()
        if not linha:
            continue
        m = re.match(r"\[(\d+)\s*-\s*(.+?)\]$", linha)
        if m:
            atual = int(m.group(1))
            deptos.append((atual, m.group(2).strip()))
            continue
        m = re.match(r"\[(\d+)\]\s*\[(.+?)\]$", linha)
        if m:
            corredores.append((atual, int(m.group(1)), m.group(2).strip()))
    return deptos, corredores


def main(saida="grafo_loja.png", mostrar=False):
    deptos, corredores = parse(DADOS)
    cor_depto = {num: CORES[i % len(CORES)] for i, (num, _) in enumerate(deptos)}

    total = COLS * ROWS
    assert len(corredores) == total - 1, (
        f"Esperava {total - 1} corredores (+ partida), recebi {len(corredores)}"
    )

    fig, ax = plt.subplots(figsize=(COLS * 1.25 + 5, ROWS * 1.0 + 1))
    ax.set_xlim(0, COLS)
    ax.set_ylim(ROWS, 0)  # linha 0 no topo
    ax.set_aspect("equal")
    ax.axis("off")

    # --- camada de trás: ilhas quadradas ---
    for idx in range(total):
        r, c = divmod(idx, COLS)
        if idx < len(corredores):
            depto, aid, nome = corredores[idx]
            cor, txt, txt_cor = cor_depto[depto], f"{aid}\n" + textwrap.fill(nome, 12, break_long_words=False), "black"
        else:  # último quadrado: partida
            cor, txt, txt_cor = "#222222", "PARTIDA", "white"
        ax.add_patch(Rectangle((c + 0.06, r + 0.06), 0.88, 0.88,
                               facecolor=cor, alpha=0.55 if idx < len(corredores) else 1.0,
                               edgecolor=cor, linewidth=1.2, zorder=1))
        ax.text(c + 0.5, r + 0.26, txt, ha="center", va="center", fontsize=5.5,
                color=txt_cor, zorder=6, linespacing=1.05,
                bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                          edgecolor="none", alpha=0.75) if idx < len(corredores) else None)

    # --- camada da frente: grafo-grade ---
    for r in range(ROWS):
        for c in range(COLS):
            x, y = c + 0.5, r + 0.5
            if c + 1 < COLS:
                ax.plot([x, x + 1], [y, y], color="#333333", lw=1.2, zorder=3)
            if r + 1 < ROWS:
                ax.plot([x, x], [y, y + 1], color="#333333", lw=1.2, zorder=3)
    xs = [c + 0.5 for r in range(ROWS) for c in range(COLS)]
    ys = [r + 0.5 for r in range(ROWS) for c in range(COLS)]
    ax.scatter(xs, ys, s=28, color="white", edgecolor="#333333", linewidth=1.2, zorder=4)
    ax.scatter([COLS - 0.5], [ROWS - 0.5], s=60, color="#ff2d2d",
               edgecolor="white", linewidth=1.2, zorder=5)

    # --- legenda: [bolinha] [nº depto] [nome depto] ---
    handles = [
        Line2D([], [], marker="o", linestyle="", markersize=10,
               markerfacecolor=cor_depto[num], markeredgecolor=cor_depto[num],
               label=f"{num}  {nome}")
        for num, nome in deptos
    ]
    handles.append(Line2D([], [], marker="o", linestyle="", markersize=10,
                          markerfacecolor="#222222", markeredgecolor="#222222",
                          label="—  partida"))
    ax.legend(handles=handles, loc="center left", bbox_to_anchor=(1.02, 0.5),
               frameon=False, fontsize=10, labelspacing=0.9, handletextpad=0.8,
               title="Departamentos", title_fontsize=12)

    fig.savefig(saida, dpi=200, bbox_inches="tight", facecolor="white")
    print(f"Figura salva em {saida}")
    if mostrar:
        plt.show()


if __name__ == "__main__":
    main()
