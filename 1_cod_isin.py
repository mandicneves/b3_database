import pyarrow.parquet as pq
import requests
import base64
import json
import pandas as pd
from time import sleep
from random import randint


cotacoes = (
    pq.ParquetFile("parquet_database/cotacoes_historicas")
    .read()
    .to_pandas()
    .reset_index(drop=True)
)

# criando tabela EMPRESA com id_empresa, codigo_recente, codigos_anteriores
df_empresas = cotacoes[cotacoes["tipo_mercado"] == 10]
df_empresas = df_empresas.loc[
    (cotacoes["codigo_isin"].apply(lambda x: x[6:9]) == "ACN"),  # apenas acoes
    ["data_pregao", "ticker", "nome_empresa", "codigo_isin"],
]


df_empresas["codigo"] = df_empresas["ticker"].apply(lambda x: x[:4])
lista_codisin = list(df_empresas.groupby("codigo_isin").size().index)


def build_isin_detail_url(isin):
    # isin = "BRAFLTACNOR1"
    # Cria um dicionário com o parâmetro 'isin'
    params = {"isin": isin}
    # Converte o dicionário para uma string JSON
    json_str = json.dumps(params)
    # Codifica a string JSON em Base64
    encoded_str = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
    # Monta a URL com a string codificada
    url = f"https://sistemaswebb3-listados.b3.com.br/isinProxy/IsinCall/GetDetail/{encoded_str}"
    # Faz a requisicao no endpoint codificado
    response = requests.get(url)
    # Printa o status code
    # if response.status_code != 200:
    print(isin, response.status_code)
    return response.json()["emissor"]


lista_resultados = []


while len(lista_codisin) > 1:

    try:
        for i, cod_isin in enumerate(lista_codisin):

            resultado = build_isin_detail_url(cod_isin)
            resultado["codigo_isin"] = cod_isin

            lista_resultados.append(pd.DataFrame([resultado]))

            print(f"{i+1} de {len(lista_codisin)}")
            sleep(randint(1, 2))

    except Exception as e:
        lista_codisin = lista_codisin[i:]
        print(f"{e} | {cod_isin}")


dim_empresas = pd.concat(lista_resultados)
dim_empresas = dim_empresas.drop_duplicates().reset_index(drop=True)
dim_empresas.to_csv("aux_database/cnpj_codisin.csv", index=False)
