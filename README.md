# Cotação histórica dos ativos financeiros negociados na B3

A B3 disponibiliza as séries de cotação histórica (essas cotações não estão ajustadas as trocas de ticker, CNPJ, desdobramento, agrupamentos, etc). Os dados são disponibilizados em `.txt` com uma formatação nada amigável. As especifições da formatação são disponiblizadas aqui: https://www.b3.com.br/data/files/33/67/B9/50/D84057102C784E47AC094EA8/SeriesHistoricas_Layout.pdf

A primeira coisa que eu fiz foi fazer o download das séries históricas anuais, e organizei-os nessa estrutura:

```bash
raw_database/
├── COTAHIST_A1986.TXT
├── COTAHIST_A1987.TXT
├── ...
├── COTAHIST_A2024.TXT
├── COTAHIST_A2025.TXT
```

Em seguida apliquei o algoritmo em `0_parquet_db.py` que faz a leitura de todos os arquivos na pasta `raw_database` e os salva num formato `parquet` na pasta `parquet_dabase/cotacoes_historicas`
