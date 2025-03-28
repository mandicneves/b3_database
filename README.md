# Cotação histórica dos ativos financeiros negociados na B3

A B3 disponibiliza as séries de cotação histórica (essas cotações não estão ajustadas às trocas de ticker, CNPJ, desdobramentos, agrupamentos, etc). Os dados são disponibilizados em `.txt` com uma formatação pouco amigável. As especificações da formatação estão disponíveis aqui:  
[SeriesHistoricas_Layout.pdf](https://www.b3.com.br/data/files/33/67/B9/50/D84057102C784E47AC094EA8/SeriesHistoricas_Layout.pdf)

---

## Estruturar os arquivos em um só

A primeira coisa que fiz foi fazer o download das séries históricas anuais e organizá-las nesta estrutura:

```bash
raw_database/
├── COTAHIST_A2000.TXT
├── COTAHIST_A2001.TXT
├── ...
├── COTAHIST_A2024.TXT
├── COTAHIST_A2025.TXT
```

Em seguida, apliquei o algoritmo em `0_parquet_db.py`, que faz a leitura de todos os arquivos na pasta `raw_database` e os salva no formato `parquet` na pasta `parquet_database/cotacoes_historicas`.

**OBS:** Devido ao tamanho dos arquivos `COTAHIST`, não faz sentido subi-los aqui. Deixarei apenas o arquivo `cotacoes_historicas`. Para obter o mesmo resultado, basta seguir o passo anterior.

---

## Encontrar o CNPJ para cada código ISIN

A norma ISO 6166 ou **ISIN (International Securities Identification Number)** foi criada para estabelecer uma padronização internacional na codificação de títulos financeiros, atribuindo a cada ativo um código único de identificação.

A B3 disponibiliza a consulta de empresas informando o código ISIN através do link:  
[Pesquisa Código ISIN - B3](https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/consultas/mercado-a-vista/codigo-isin/pesquisa/)

Contudo, por esse link, ao informar um código ISIN, não é possível obter o CNPJ da companhia. Utilizando a ferramenta **DevTools** do navegador, na aba **Network**, consegui identificar o **endpoint** da API de códigos **ISIN**. O algoritmo em `1_cod_isin.py` realiza a tarefa de codificar e decodificar os **endpoints** para cada código **ISIN**. O resultado final foi salvo em `aux_database/cnpj_codisin.csv`.

---

## Verificar nomes de empresas semelhantes

Algumas empresas ficaram sem CNPJ. Minha tentativa aqui foi comparar os nomes das empresas dentro do próprio arquivo `cnpj_codisin` e também com os demonstrativos contábeis de envio obrigatório à **CVM**. Para isso, utilizei uma biblioteca que eu mesmo criei, chamada `getDataCVM`, que extrai esses demonstrativos diretamente da CVM:  
[Dados CVM](https://dados.cvm.gov.br/dataset/?q=cias+abertas).

O algoritmo em `2_empresas_cnpj.py` executa esse processo. No final, ainda assim, algumas empresas ficaram sem CNPJ. Minha solução, por enquanto, foi salvar dois arquivos:  
- `aux_database/empresas_cnpj_sem_na.csv` (excluindo as empresas sem CNPJ)  
- `aux_database/empresas_cnpj_com_na.csv` (incluindo as empresas sem CNPJ)  

Minha intenção futura é completar essa tabela.

**OBS:** A biblioteca `getDataCVM` está disponível no PyPI e no meu GitHub:

- [PyPI - getDataCVM](https://pypi.org/project/getDataCVM/#description)  
- [GitHub - getDataCVM](https://github.com/mandicneves/getDataCVM)

---

## Criar tabelas de dimensão e fato

A ideia é criar tabelas de dimensão para **Empresa, Tickers e Tempo**, além de uma **tabela fato** para armazenar as negociações.

O algoritmo em `3_criando_tabelas.py` realiza esse processo e salva as tabelas na pasta `database_tables`.

---

## Ajustar cotação histórica (em desenvolvimento)

A ideia aqui é ajustar o preço de fechamento considerando desdobramentos, agrupamentos e distribuição de lucros.
