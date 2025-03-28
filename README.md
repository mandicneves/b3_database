# Cotação histórica dos ativos financeiros negociados na B3

A B3 disponibiliza as séries de cotação histórica (essas cotações não estão ajustadas as trocas de ticker, CNPJ, desdobramento, agrupamentos, etc). Os dados são disponibilizados em `.txt` com uma formatação nada amigável. As especifições da formatação são disponiblizadas aqui: https://www.b3.com.br/data/files/33/67/B9/50/D84057102C784E47AC094EA8/SeriesHistoricas_Layout.pdf

---

## Estruturar os arquivos em um só

A primeira coisa que eu fiz foi fazer o download das séries históricas anuais, e organizei-os nessa estrutura:

```bash
raw_database/
├── COTAHIST_A1986.TXT
├── COTAHIST_A1987.TXT
├── ...
├── COTAHIST_A2024.TXT
├── COTAHIST_A2025.TXT
```

Em seguida apliquei o algoritmo em `0_parquet_db.py` que faz a leitura de todos os arquivos na pasta `raw_database` e os salva num formato `parquet` na pasta `parquet_dabase/cotacoes_historicas`.

**OBS:** Em virtude do tamanho dos arquivos `COTAHIST` não faz sentido em subir os arquivos aqui. Deixarei apenas o arquivo `cotacoes_historicas`. Para chegar no mesmo resultado, é só seguir o passo anterior.

---

## Encontrar o cnpj para cada código ISIN

A norma ISO 6166 ou **ISIN (International Securities Identification Number)** foi criada visando a estabelecer uma padronização internacional na codificação de títulos financeiros, atribuindo a cada ativo um código único de identificação.

A B3 disponibiliza a consulta de empresas informando o código ISIN através do link: https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/consultas/mercado-a-vista/codigo-isin/pesquisa/

Contudo, através desse link, se informado o código ISIN, não é possível obter o CNPJ da companhia. Utilizando a ferramenta **DevTools** do navegador, na aba **Network** eu consegui buscar o **endpoint** da api de códigos **ISIN**. O algoritimo em `1_cod_isin.py` realiza a tarefa de codificar e decodificar os **endpoints** para cada código **ISIN**. Enfim, o resultado final foi guardado em `aux_database/cnpj_codisin.csv`.

---

## Verificar nomes de empresas semelhantes

Algumas empresas ficaram sem CNPJ, então minha tentativa aqui é comparar o nome de empresas dentro do próprio arquivo `cnpj_codisin` quanto em comparação com os demonstrativos contábeis de envio obrigatório à **CVM**. Aqui eu fiz uso de uma biblioteca que eu mesmo criei (`getDataCVM`) que pega esses demonstrativos direto da CVM: https://dados.cvm.gov.br/dataset/?q=cias+abertas.

O algoritimo em `2_empresas_cnpj.py` dá conta desse processo. No final, ainda assim, algumas empresas ficaram sem CNPJ. Minha solução, por enquanto, foi salvar dois arquivos, um desconsiderando essas empresas - `aux_database/empresas_cnpj_sem_na.csv` - e outro contendo-as - `aux_database/empresas_cnpj_com_na.csv`. Num momento futuro minha intenção é completar essa tabela.

**OBS:** a biblioteca `getDataCVM` está disponível no Pypi.org: https://pypi.org/project/getDataCVM/#description. E também no meu Github: https://github.com/mandicneves/getDataCVM

---
