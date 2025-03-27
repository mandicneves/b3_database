import pandas as pd
import os

tamanho_campos = [
    2,
    8,
    2,
    12,
    3,
    12,
    10,
    3,
    4,
    13,
    13,
    13,
    13,
    13,
    13,
    13,
    5,
    18,
    18,
    13,
    1,
    8,
    7,
    13,
    12,
    3,
]
lista_dados = []

for dir, subdir, files in os.walk("raw_database/"):

    files.sort()

    for file in files:

        arquivo = os.path.join(dir, file)

        dados_acoes = pd.read_fwf(arquivo, widths=tamanho_campos, header=0)

        ## Nomear as colunas

        dados_acoes.columns = [
            "tipo_registro",
            "data_pregao",
            "cod_bdi",
            "ticker",
            "tipo_mercado",
            "nome_empresa",
            "especificacao_papel",
            "prazo_dias_merc_termo",
            "moeda_referencia",
            "preco_abertura",
            "preco_maximo",
            "preco_minimo",
            "preco_medio",
            "preco_fechamento",
            "preco_melhor_oferta_compra",
            "preco_melhor_oferta_venda",
            "numero_negocios",
            "quantidade_papeis_negociados",
            "volume_total_negociado",
            "preco_exercicio",
            "ìndicador_correcao_precos",
            "data_vencimento",
            "fator_cotacao",
            "preco_exercicio_pontos",
            "codigo_isin",
            "num_distribuicao_papel",
        ]

        # Eliminar a última linha
        linha = len(dados_acoes["data_pregao"])
        dados_acoes = dados_acoes.drop(linha - 1)

        # Ajustar valores com virgula (dividir os valores dessas colunas por 100)
        listaVirgula = [
            "preco_abertura",
            "preco_maximo",
            "preco_minimo",
            "preco_medio",
            "preco_fechamento",
            "preco_melhor_oferta_compra",
            "preco_melhor_oferta_venda",
            "volume_total_negociado",
            "preco_exercicio",
            "preco_exercicio_pontos",
        ]

        for coluna in listaVirgula:
            dados_acoes[coluna] = [i / 100.0 for i in dados_acoes[coluna]]

        lista_dados.append(dados_acoes)
        print(f"Leitura do arquivo {file} finalizada")

dados_historicos = pd.concat(lista_dados)

dados_historicos["data_pregao"] = pd.to_datetime(
    dados_historicos["data_pregao"], format="%Y%m%d"
)

dados_historicos.sort_values("data_pregao", inplace=True)  # ordenando por data

dados_historicos.to_parquet("parquet_database/cotacoes_historicas")