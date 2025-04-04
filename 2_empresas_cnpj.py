import pandas as pd
import unicodedata
import re
import getDataCVM
from rapidfuzz import fuzz
from janitor import clean_names
from pathlib import Path


def normalizar_texto(texto: str) -> str:
    """
    Remove acentos, caracteres especiais e converte para maiúsculas.
    """
    texto = texto.upper()
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    return re.sub(r"\W+", " ", texto).strip()


def formatar_cnpj(cnpj) -> str:
    """
    Formata o CNPJ para o padrão XX.XXX.XXX/XXXX-XX.
    """
    try:
        cnpj = f"{int(cnpj):014d}"
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    except ValueError:
        return None


# Criar diretório para saída de arquivos se não existir
Path("aux_database").mkdir(exist_ok=True)

# Carregar base de empresas
empresas = pd.read_csv("aux_database/cnpj_codisin.csv")
empresas.columns = [
    "id",
    "codigo",
    "nome_social",
    "nome_resumido",
    "cnpj",
    "situacao_ativa",
    "codigo_isin",
]

# Normalizar nome social
empresas["nome_social"] = empresas["nome_social"].apply(normalizar_texto)

# Identificar empresas sem CNPJ
empresas_sem_cnpj = empresas[empresas["cnpj"].isna()]

# Criar um dicionário de similaridade para preenchimento de CNPJs
similaridade_dict = {}

for empresa in empresas_sem_cnpj["nome_social"].unique():
    similaridades = empresas["nome_social"].apply(lambda x: fuzz.ratio(x, empresa))
    match_idx = similaridades[similaridades >= 95].index

    if len(match_idx) > 1:
        cnpjs_validos = empresas.loc[match_idx, "cnpj"].dropna()
        if not cnpjs_validos.empty:
            similaridade_dict[empresa] = cnpjs_validos.iloc[0]

# Preencher CNPJs faltantes com os valores encontrados
empresas["cnpj"] = (
    empresas["nome_social"].map(similaridade_dict).combine_first(empresas["cnpj"])
)

empresas[empresas["codigo"].isin(["WEGE", "ELMJ"])]


# Tratamento específico para WEG
weg_cnpj = empresas.loc[empresas["codigo"] == "WEGE", "cnpj"].dropna().iloc[0]
empresas.loc[empresas["nome_social"].str.contains("WEG"), "cnpj"] = weg_cnpj

# Buscar dados da CVM
registro_cvm = getDataCVM.RegData().get_data()
registro_cvm = clean_names(registro_cvm)
registro_cvm = registro_cvm[["cnpj_cia", "denom_social", "denom_comerc"]]
registro_cvm["cnpj_cia"] = registro_cvm["cnpj_cia"].astype(str).str.zfill(14)
registro_cvm["denom_social"] = registro_cvm["denom_social"].apply(normalizar_texto)
registro_cvm["denom_comerc"] = registro_cvm["denom_comerc"].apply(normalizar_texto)

# Atualizar os CNPJs ausentes
for empresa in empresas.loc[empresas["cnpj"].isna(), "nome_social"].unique():
    similaridades = registro_cvm["denom_social"].apply(lambda x: fuzz.ratio(x, empresa))
    match_idx = similaridades[similaridades >= 90].index

    if not match_idx.any():
        similaridades = registro_cvm["denom_comerc"].apply(
            lambda x: fuzz.ratio(x, empresa)
        )
        match_idx = similaridades[similaridades >= 90].index

    if match_idx.any():
        empresas.loc[empresas["nome_social"] == empresa, "cnpj"] = registro_cvm.loc[
            match_idx[0], "cnpj_cia"
        ]

# Salvar base com CNPJs, mesmo com valores ausentes
empresas.to_csv("aux_database/empresas_cnpj_com_na.csv", index=False)

# Formatar CNPJs e remover NAs
empresas.dropna(subset=["cnpj"], inplace=True)
empresas["cnpj"] = empresas["cnpj"].apply(formatar_cnpj)

# Salvar base final sem NAs
empresas.to_csv("aux_database/empresas_cnpj_sem_na.csv", index=False)
