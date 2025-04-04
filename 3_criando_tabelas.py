import pandas as pd
from pathlib import Path

# Criar diretórios automaticamente, se não existirem
Path("database_tables").mkdir(exist_ok=True)
Path("parquet_database").mkdir(exist_ok=True)

# Leitura eficiente dos dados
cotacoes = pd.read_parquet("parquet_database/cotacoes_mercado_avista")
dim_empresas = pd.read_csv("aux_database/empresas_cnpj_sem_na.csv")

# Filtrando cotações apenas das empresas presentes na dimensão
df_cotacoes = cotacoes.loc[
    cotacoes["codigo_isin"].isin(dim_empresas["codigo_isin"]),
    [
        "data_pregao",
        "ticker",
        "nome_empresa",
        "preco_fechamento",
        "volume_total_negociado",
        "codigo_isin",
    ],
].merge(dim_empresas[["cnpj", "codigo_isin"]], on="codigo_isin")

# Criando código base do ticker
df_cotacoes["codigo"] = df_cotacoes["ticker"].str[:4]

# Obtendo o código e nome mais recente de cada empresa
df_codigo_recente = df_cotacoes.groupby("cnpj")[["codigo", "nome_empresa"]].agg("last")
df_codigo_recente = df_codigo_recente.rename(
    columns={"codigo": "codigo_recente", "nome_empresa": "nome_recente"}
)

# Merge com os dados de cotações
df_cotacoes = df_cotacoes.merge(df_codigo_recente, on="cnpj")

# Criando `ticker_recente`
df_cotacoes["ticker_recente"] = (
    df_cotacoes["codigo_recente"] + df_cotacoes["ticker"].str[-1]
)

# Removendo colunas desnecessárias
df_cotacoes.drop(columns=["ticker", "codigo", "codigo_isin"], inplace=True)

# ==================== Criando tabelas dimensão e fato ====================

# Tabela dimCompany
dimCompany = df_codigo_recente.merge(
    df_cotacoes.groupby("cnpj")["ticker_recente"].unique().reset_index(), on="cnpj"
).reset_index(names="id_empresa")
dimCompany["id_empresa"] += 1  # Criando IDs sequenciais

# Tabela dimTickers
dimTickers = df_cotacoes.groupby("ticker_recente")["cnpj"].last().reset_index()
dimTickers = dimTickers.merge(dimCompany[["id_empresa", "cnpj"]], on="cnpj").drop(
    "cnpj", axis=1
)
dimTickers.insert(0, "id_ticker", range(1, len(dimTickers) + 1))

# Tabela dimTime
dimTime = df_cotacoes[["data_pregao"]].drop_duplicates().reset_index(drop=True)
dimTime.insert(0, "id_data", range(1, len(dimTime) + 1))

# Criando a tabela fatoCotacao
fatoCotacao = (
    df_cotacoes.merge(dimTime, on="data_pregao")
    .merge(dimCompany[["id_empresa", "cnpj"]], on="cnpj")
    .merge(dimTickers[["id_ticker", "ticker_recente"]], on="ticker_recente")
)[["id_data", "id_empresa", "id_ticker", "preco_fechamento", "volume_total_negociado"]]

# Salvando tabelas em CSV
dimCompany.to_csv("database_tables/dimCompany.csv", index=False)
dimTickers.to_csv("database_tables/dimTickers.csv", index=False)
dimTime.to_csv("database_tables/dimTime.csv", index=False)
fatoCotacao.sort_values("id_data").to_csv(
    "database_tables/fatoCotacao.csv", index=False
)

# Salvando cotacoes_cnpj em formato Parquet
df_cotacoes = (
    df_cotacoes[
        [
            "data_pregao",
            "cnpj",
            "nome_recente",
            "codigo_recente",
            "ticker_recente",
            "preco_fechamento",
            "volume_total_negociado",
        ]
    ]
    .sort_values(["data_pregao", "codigo_recente"])
    .reset_index(drop=True)
)

df_cotacoes.to_parquet("parquet_database/cotacoes_cnpj")
