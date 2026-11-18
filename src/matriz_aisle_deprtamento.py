import pandas as pd
#aisles por departamento

# 1. Carregar os arquivos CSV
products = pd.read_csv('../data/raw/products.csv')
aisles = pd.read_csv('../data/raw/aisles.csv')
departments = pd.read_csv('../data/raw/departments.csv')

# 2. Fazer os merges para juntar as tabelas
# products tem product_id, product_name, aisle_id, department_id
df = products.merge(aisles, on='aisle_id', how='left')
df = df.merge(departments, on='department_id', how='left')

# 3. Obter combinações únicas de (department_id, department, aisle_id, aisle)
# Como um aisle pode ter produtos em múltiplos departamentos (conforme vimos na consulta anterior), 
# agrupamos para listar quais corredores pertencem a cada departamento.
depto_aisles = (
    df[['department_id', 'department', 'aisle_id', 'aisle']]
    .drop_duplicates()
    .sort_values(by=['department_id', 'aisle_id'])
)

# 4. Agrupar por departamento e exibir no formato desejado
grouped = depto_aisles.groupby(['department_id', 'department'])

for (dept_id, dept_name), group in grouped:
    print(f"[{dept_id} - {dept_name}]")
    for _, row in group.iterrows():
        print(f"[{row['aisle_id']}] [{row['aisle']}]")
    print()  # Linha em branco para separar os departamentos