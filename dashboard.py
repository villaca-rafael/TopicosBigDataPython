import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Configurar estilo global do Seaborn para tema escuro
sns.set_theme(style="darkgrid")

# Configurar tema do Streamlit
st.set_page_config(page_title="Dashboard de Vendas", layout="wide", page_icon="📊")

# Carregar o conjunto de dados
file_path = "BASEESTPRODFL1.csv"
data = pd.read_csv(file_path, encoding="latin1")

# Processamento dos dados
sales_data = data[["DESCRICAO", "QTVENDMES1", "QTVENDMES2", "QTVENDMES3"]].copy()

# Converter colunas de vendas em numéricas
for col in ["QTVENDMES1", "QTVENDMES2", "QTVENDMES3"]:
    sales_data[col] = pd.to_numeric(sales_data[col].str.replace(",", "."), errors="coerce")

# Remover linhas com todas as colunas de vendas NaN
sales_data.dropna(subset=["QTVENDMES1", "QTVENDMES2", "QTVENDMES3"], how="all", inplace=True)

# Criar a coluna TotalSales (soma das vendas dos últimos três meses)
sales_data["TotalSales"] = sales_data[["QTVENDMES1", "QTVENDMES2", "QTVENDMES3"]].sum(axis=1)

# Identificar o produto outlier
outlier_product = "ESCOVA DENTALS CLASSIC CONFORT MACIA12X1"

# Sidebar Configurações
st.sidebar.header("Configurações")

# Seleção de meses
selected_months = st.sidebar.multiselect(
    "Selecione os meses para análise",
    options=["Setembro", "Agosto", "Julho"],
    default=["Setembro", "Agosto", "Julho"]
)

# Limite de produtos
top_n = st.sidebar.slider(
    "Número de produtos a exibir no gráfico",
    min_value=5,
    max_value=20,
    value=10
)

# Escolha de paleta
color_palette = st.sidebar.selectbox(
    "Escolha a paleta de cores para os gráficos",
    options=["rocket", "mako", "coolwarm", "viridis", "plasma"],
    index=0
)

# Excluir outlier
exclude_outliers = st.sidebar.checkbox(
    "Excluir produto outlier",
    value=True
)

# Mostrar dados brutos
show_raw_data = st.sidebar.checkbox("Mostrar dados brutos")

# Download dos dados filtrados
st.sidebar.download_button(
    label="Baixar Dados Filtrados",
    data=sales_data.to_csv(index=False),
    file_name="dados_filtrados.csv",
    mime="text/csv"
)

# Aplicar filtros de dados
if exclude_outliers:
    filtered_sales_data = sales_data[sales_data["DESCRICAO"] != outlier_product]
else:
    filtered_sales_data = sales_data

# Filtrar meses selecionados
month_labels = {
    "QTVENDMES1": "Setembro",
    "QTVENDMES2": "Agosto",
    "QTVENDMES3": "Julho",
}
selected_month_labels = {k: v for k, v in month_labels.items() if v in selected_months}

# Exibir dados brutos se selecionado
if show_raw_data:
    st.subheader("Dados Brutos")
    st.dataframe(filtered_sales_data)

# Função para criar gráficos
def plot_top_10_products_individual(top_products_filtered, selected_month_labels):
    for month, df in top_products_filtered.items():
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(
            x=df[month],
            y=df["DESCRICAO"],
            palette=color_palette,
            ax=ax,
        )
        ax.set_title(f"Top {top_n} Produtos - {selected_month_labels[month]}", fontsize=16, fontweight="bold", color="white")
        ax.set_xlabel("Quantidade Vendida", fontsize=12, color="white")
        ax.set_ylabel("Produtos", fontsize=12, color="white")
        ax.tick_params(colors="white")
        fig.patch.set_facecolor("#303030")
        ax.set_facecolor("#404040")
        st.pyplot(fig)

def plot_total_sales(top_10_products_total_filtered):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x="TotalSales",
        y="DESCRICAO",
        data=top_10_products_total_filtered,
        palette=color_palette,
        ax=ax,
    )
    ax.set_title("Top Produtos por Total de Vendas - Últimos 3 Meses", fontsize=16, fontweight="bold", color="white")
    ax.set_xlabel("Total Quantidade Vendida (Últimos 3 Meses)", fontsize=12, color="white")
    ax.set_ylabel("Produto", fontsize=12, color="white")
    ax.tick_params(colors="white")
    fig.patch.set_facecolor("#303030")
    ax.set_facecolor("#404040")
    st.pyplot(fig)

def plot_monthly_sales_pie_chart(monthly_sales_no_outlier_df):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(
        monthly_sales_no_outlier_df["Total de Vendas"],
        labels=monthly_sales_no_outlier_df["Mês"],
        autopct="%1.1f%%",
        startangle=140,
        colors=sns.color_palette("viridis", len(monthly_sales_no_outlier_df)),
        textprops={"color": "white", "fontsize": "12"}
    )
    ax.set_title("Distribuição de Vendas por Mês (Últimos 3 Meses)", fontsize=16, fontweight="bold", color="white")
    fig.patch.set_facecolor("#303030")
    st.pyplot(fig)

# Dashboard
st.title("Dashboard de Análise de Vendas 📊", anchor="center")

# Mostrar gráficos com filtros aplicados
if selected_month_labels:
    st.subheader("Top Produtos por Mês")
    top_products_filtered = {}
    for month in selected_month_labels.keys():
        top_products_filtered[month] = filtered_sales_data.nlargest(top_n, month)[
            ["DESCRICAO", month]
        ]
    plot_top_10_products_individual(top_products_filtered, selected_month_labels)
else:
    st.warning("Nenhum mês selecionado.")

# Total de vendas nos últimos 3 meses
st.subheader("Top Produtos por Total de Vendas nos Últimos 3 Meses")
top_10_products_total_filtered = filtered_sales_data.nlargest(
    top_n, "TotalSales"
)[["DESCRICAO", "TotalSales"]]
plot_total_sales(top_10_products_total_filtered)

# Total de vendas por mês
monthly_sales_no_outlier = {
    "Julho": filtered_sales_data["QTVENDMES3"].sum(),
    "Agosto": filtered_sales_data["QTVENDMES2"].sum(),
    "Setembro": filtered_sales_data["QTVENDMES1"].sum(),
}
monthly_sales_no_outlier_df = pd.DataFrame(
    list(monthly_sales_no_outlier.items()), columns=["Mês", "Total de Vendas"]
)
st.subheader("Distribuição de Vendas por Mês")
plot_monthly_sales_pie_chart(monthly_sales_no_outlier_df)