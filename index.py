import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


file_path = 'BASEESTPRODFL1.csv'

# Carregar o conjunto de dados com uma codificação diferente para lidar com possíveis problemas de caracteres
data = pd.read_csv(file_path, encoding='latin1')

# Exibir as primeiras linhas para entender sua estrutura
data.head()

# Selecionar colunas relevantes para análise: descrição do produto e quantidades de vendas dos últimos três meses
sales_data = data[['DESCRICAO', 'QTVENDMES1', 'QTVENDMES2', 'QTVENDMES3']].copy()

# Converter colunas de vendas em numéricas, substituindo vírgulas e tratando valores não numéricos como NaN
for col in ['QTVENDMES1', 'QTVENDMES2', 'QTVENDMES3']:
    sales_data[col] = pd.to_numeric(sales_data[col].str.replace(',', '.'), errors='coerce')

# Eliminar linhas com valores NaN em todas as três colunas de vendas, pois elas não são úteis para a análise
sales_data.dropna(subset=['QTVENDMES1', 'QTVENDMES2', 'QTVENDMES3'], how='all', inplace=True)

# Exibir dados limpos
sales_data.head()

# Para cada mês, calcular os 10 principais produtos por vendas
top_products = {}
for month in ['QTVENDMES1', 'QTVENDMES2', 'QTVENDMES3']:
    # Classificar os produtos por vendas e selecionar os 10 principais
    top_products[month] = sales_data.nlargest(10, month)[['DESCRICAO', month]]

# Definir rótulos de mês para os últimos três meses
month_labels = {
    'QTVENDMES1': 'Setembro',
    'QTVENDMES2': 'Agosto',
    'QTVENDMES3': 'Julho'
}

# Identificar o produto que mais vendeu em agosto ('QTVENDMES2') e filtra-lo
outlier_product = 'ESCOVA DENTALS CLASSIC CONFORT MACIA12X1'
filtered_sales_data = sales_data[sales_data['DESCRICAO'] != outlier_product]

# Recalcular os 10 principais produtos de cada mês sem valores discrepantes
top_products_filtered = {}
for month in ['QTVENDMES1', 'QTVENDMES2', 'QTVENDMES3']:
    top_products_filtered[month] = filtered_sales_data.nlargest(10, month)[['DESCRICAO', month]]

# Traçar os 10 principais produtos de cada um dos últimos 3 meses com nomes de meses personalizados e dados filtrados
plt.figure(figsize=(15, 10))

for i, (month, df) in enumerate(top_products_filtered.items(), 1):
    plt.subplot(3, 1, i)
    plt.barh(df['DESCRICAO'], df[month], color='skyblue')
    plt.xlabel('Quantidade Vendida')
    plt.ylabel('Produtos')
    plt.title(f'Top 10 Produtos - {month_labels[month]}')
    plt.gca().invert_yaxis()

plt.tight_layout()
plt.show()



# Somar as vendas dos três meses para obter o total de vendas dos últimos três meses
sales_data['TotalSales'] = sales_data[['QTVENDMES1', 'QTVENDMES2', 'QTVENDMES3']].sum(axis=1)

# Obter os 10 principais produtos por vendas totais nos últimos três meses
top_10_products_total = sales_data.nlargest(10, 'TotalSales')[['DESCRICAO', 'TotalSales']]

# Filtrar o produto outlier "ESCOVA DENTALS CLASSIC CONFORT MACIA12X1" dos dados totais de vendas
filtered_sales_data_total = sales_data[sales_data['DESCRICAO'] != outlier_product]

# Recalcular os 10 principais produtos pelo total de vendas nos últimos três meses sem valores discrepantes
top_10_products_total_filtered = filtered_sales_data_total.nlargest(10, 'TotalSales')[['DESCRICAO', 'TotalSales']]

# Traçar os 10 principais produtos por vendas totais nos últimos três meses com o valor discrepante removido
plt.figure(figsize=(10, 8))
plt.barh(top_10_products_total_filtered['DESCRICAO'], top_10_products_total_filtered['TotalSales'], color='skyblue')
plt.xlabel('Total Quantidade Vendida (Útimos 3 Meses)')
plt.ylabel('Produto')
plt.title('Top 10 Produtos por Total de Vendas - Últimos 3 Meses')
plt.gca().invert_yaxis()

plt.tight_layout()
plt.show()



# Recalcular o total de vendas mensais excluindo o produto outlier "ESCOVA DENTALS CLASSIC CONFORT MACIA12X1"
filtered_sales_data_no_outlier = sales_data[sales_data['DESCRICAO'] != outlier_product]

# Somar as vendas de cada mês para obter o total de vendas mensais sem valores discrepantes
monthly_sales_no_outlier = {
    'Julho': filtered_sales_data_no_outlier['QTVENDMES3'].sum(),
    'Agosto': filtered_sales_data_no_outlier['QTVENDMES2'].sum(),
    'Setembro': filtered_sales_data_no_outlier['QTVENDMES1'].sum()
}

# Converter para DataFrame para plotagem
monthly_sales_no_outlier_df = pd.DataFrame(list(monthly_sales_no_outlier.items()), columns=['Month', 'TotalSales'])

# Traçar o total de vendas por mês como um gráfico de linhas com formatação ajustada do eixo y
plt.figure(figsize=(10, 6))
plt.plot(monthly_sales_no_outlier_df['Month'], monthly_sales_no_outlier_df['TotalSales'], marker='o', linestyle='-', color='b')
plt.xlabel('Mês')
plt.ylabel('Total Vendas')
plt.title('Total de Vendas por Mês (Últimos 3 Meses)')

# Formate o eixo y para exibir números inteiros para melhor legibilidade
plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
plt.grid(True)

plt.tight_layout()
plt.show()