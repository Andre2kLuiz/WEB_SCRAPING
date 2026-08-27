# 🔎 Web Scraping — Contador de Palavras e Nuvem de Palavras

Aplicação desenvolvida em **Python + Streamlit** para realizar Web Scraping de páginas da **Wikipédia**, extrair seus textos, remover palavras irrelevantes (*stopwords*), contar a frequência de palavras e gerar uma **nuvem de palavras**.

O projeto possui duas implementações diferentes:

* `app_beautifulsoup.py` — utiliza **Requests + BeautifulSoup**.
* `app_scrapy.py` — utiliza **Scrapy** para realizar a extração dos textos.

Ambas as versões possuem uma interface gráfica desenvolvida com **Streamlit**.

---

## 📌 Funcionalidades

O sistema permite:

* 🔎 Pesquisar páginas da Wikipédia a partir de termos informados pelo usuário.
* 📚 Processar exatamente **5 termos por execução**.
* 🌐 Utilizar a API da Wikipédia para encontrar as páginas correspondentes.
* 🕷️ Realizar Web Scraping das páginas encontradas.
* 🧹 Limpar os textos extraídos.
* 🚫 Remover *stopwords* da língua portuguesa.
* 🔢 Contar a quantidade de palavras antes e depois da limpeza.
* 🔍 Pesquisar quantas vezes uma palavra aparece no texto.
* 📄 Visualizar o texto original extraído.
* 🧹 Visualizar o texto após a remoção das *stopwords*.
* ☁️ Gerar uma nuvem de palavras.
* 🖼️ Utilizar uma imagem como máscara para a nuvem de palavras.
* ⏱️ Na versão com Scrapy, visualizar o tempo utilizado na coleta.
* 🕷️ Na versão com Scrapy, visualizar informações sobre os blocos de texto extraídos e os seletores utilizados.

---

## Estrutura do projeto

Uma estrutura recomendada para o projeto é:

```text
web-scraping/
│
├── app_beautifulsoup.py
├── app_scrapy.py
├── wiki.jpeg
├── requirements.txt
└── README.md
```

## Arquivos

| Arquivo                | Descrição                                          |
| ---------------------- | -------------------------------------------------- |
| `app_beautifulsoup.py` | Aplicação utilizando Requests e BeautifulSoup      |
| `app_scrapy.py`        | Aplicação utilizando Scrapy                        |
| `wiki.jpeg`            | Imagem utilizada como máscara da nuvem de palavras |
| `requirements.txt`     | Dependências necessárias para executar o projeto   |
| `README.md`            | Documentação do projeto                            |

> **Importante:** o arquivo `wiki.jpeg` deve estar no mesmo diretório dos arquivos Python, pois ele é carregado diretamente pelo programa.

---

## Tecnologias utilizadas

* **Python 3**
* **Streamlit**
* **Requests**
* **BeautifulSoup4**
* **Scrapy**
* **WordCloud**
* **NumPy**
* **Matplotlib**
* **Pillow**
* **API da Wikipédia**

---

## Instalação

## 1. Clonar o projeto

Caso o projeto esteja hospedado no GitHub:

```bash
git clone URL_DO_REPOSITORIO
cd web-scraping
```

---

## 2. Criar um ambiente virtual

Linux/macOS:

```bash
python3 -m venv venv
```

Windows:

```bash
python -m venv venv
```

---

## 3. Ativar o ambiente virtual

### Linux/macOS

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

## 4. Instalar as dependências

Crie um arquivo `requirements.txt` com:

```text
streamlit
requests
beautifulsoup4
scrapy
numpy
wordcloud
matplotlib
pillow
```

Depois execute:

```bash
pip install -r requirements.txt
```

---

## Executando a aplicação

O projeto possui duas versões independentes.

## 🥣 Versão 1 — Requests + BeautifulSoup

Para executar a versão que utiliza **Requests + BeautifulSoup**:

```bash
streamlit run app_beautifulsoup.py
```

O Streamlit iniciará o servidor local e exibirá um endereço semelhante a:

```text
http://localhost:8501
```

Essa versão utiliza `requests` para acessar as páginas e `BeautifulSoup` para analisar o HTML.

### Fluxo da coleta com Scrapy

```text
Usuário
   ↓
Informa 5 termos
   ↓
API da Wikipédia
   ↓
Encontra as páginas
   ↓
Requests acessa as páginas
   ↓
BeautifulSoup analisa o HTML
   ↓
Extrai os parágrafos
   ↓
Junta os textos
   ↓
Remove stopwords
   ↓
Conta palavras
   ↓
Gera nuvem de palavras
```

---

## Versão 2 — Scrapy

Para executar a versão utilizando **Scrapy**:

```bash
streamlit run app_scrapy.py
```

Essa versão utiliza o framework **Scrapy** para realizar a coleta das páginas.

O Scrapy é executado em um **processo separado**, utilizando `multiprocessing`. Uma fila (`multiprocessing.Queue`) é utilizada para enviar os resultados da coleta para a aplicação Streamlit.

### Fluxo da aplicação

```text
Usuário
   ↓
Informa 5 termos
   ↓
API da Wikipédia
   ↓
Encontra as páginas
   ↓
URLs são enviadas para o Scrapy
   ↓
WikipediaSpider
   ↓
Requisições HTTP
   ↓
Seletores CSS
   ↓
Extração dos parágrafos
   ↓
Resultados enviados pela Queue
   ↓
Texto completo
   ↓
Limpeza e stopwords
   ↓
Contagem de palavras
   ↓
Nuvem de palavras
```

---

## Como utilizar

Depois de iniciar uma das aplicações, será exibido um campo semelhante a:

```text
Digite 5 termos separados por vírgula:
```

Informe exatamente cinco termos.

### Exemplo

```text
Universidade Federal do Rio Grande do Norte,
Ciência de Dados,
Aprendizado de Máquina,
Engenharia de Software,
Armazém de Dados
```

Depois clique no botão de execução.

O sistema irá pesquisar cada termo na Wikipédia e tentar encontrar a página mais relevante.

---

## Páginas encontradas

Depois da pesquisa, a aplicação apresenta as páginas encontradas.

Cada página possui:

* Termo pesquisado;
* Título da página encontrada;
* URL da Wikipédia.

Na versão com Scrapy também são exibidas informações sobre o processo de coleta.

---

## Estatísticas

Após a extração dos textos, o sistema apresenta métricas como:

### Versão BeautifulSoup

* Quantidade de páginas processadas;
* Quantidade de palavras originais;
* Quantidade de palavras após a limpeza.

### Versão Scrapy

Além das métricas anteriores:

* Tempo de execução do Scrapy;
* Quantidade de blocos de texto extraídos;
* Seletor utilizado para encontrar os parágrafos.

---

## Limpeza dos textos

Antes de gerar a nuvem de palavras, o texto passa por um processo de limpeza.

São realizadas operações como:

1. Conversão para letras minúsculas;
2. Remoção de URLs;
3. Remoção de pontuação;
4. Separação do texto em palavras;
5. Remoção das *stopwords*;
6. Remoção de palavras muito pequenas na versão Scrapy.

Exemplo:

```text
"A Universidade Federal do Rio Grande do Norte é uma instituição de ensino."
```

Após a limpeza:

```text
"universidade federal rio grande norte instituição ensino"
```

---

## Stopwords

O projeto possui um conjunto de palavras comuns da língua portuguesa que normalmente não são relevantes para a análise de frequência.

Exemplos:

```text
de
a
o
que
e
em
para
com
uma
um
os
as
do
da
```

Essas palavras são removidas antes da geração da nuvem de palavras.

---

## Contador de palavras

Após o processamento, existe um campo

```text
🔎 Contar palavra
```

O usuário pode informar uma palavra, por exemplo

```text
dados
```

O sistema procura a palavra no texto já processado e informa a quantidade de ocorrências.

Exemplo

```text
A palavra dados aparece 37 vezes no texto das páginas.
```

A contagem considera a palavra inteira, e não apenas partes de outras palavras.

---

## Visualização dos textos

A aplicação disponibiliza duas áreas expansíveis.

### Texto original

Mostra o conteúdo extraído das páginas antes da limpeza.

### Texto limpo

Mostra o conteúdo depois da remoção das URLs, pontuação e *stopwords*.

Isso permite comparar o resultado da coleta com o resultado do processamento textual.

---

## Nuvem de palavras

A aplicação utiliza a biblioteca **WordCloud** para gerar uma representação visual das palavras mais frequentes.

Quanto maior a palavra apresentada na imagem, maior tende a ser sua frequência no texto analisado.

A imagem:

```text
wiki.jpeg
```

é utilizada como máscara da nuvem de palavras.

O código carrega a imagem através do Pillow:

```python
Image.open("wiki.jpeg")
```

e transforma a imagem em um array utilizando NumPy.

---

## Funcionamento do Scrapy

Na segunda implementação, a classe:

```python
class WikipediaSpider(scrapy.Spider):
```

é responsável pela coleta.

O Spider utiliza diferentes seletores CSS para tentar localizar os parágrafos da Wikipédia:

```text
#mw-content-text .mw-parser-output > p
.mw-parser-output > p
#mw-content-text p
main p
```

Os seletores são testados em sequência.

Isso torna a extração mais resistente a pequenas diferenças na estrutura HTML da página.

Caso os seletores principais não encontrem conteúdo, o programa possui uma estratégia alternativa utilizando

```text
#mw-content-text .mw-parser-output
```

---

## Configurações do Scrapy

A versão Scrapy utiliza configurações como:

```python
"CONCURRENT_REQUESTS": 5
```

permitindo até cinco requisições concorrentes.

Também são utilizados:

```python
"DOWNLOAD_TIMEOUT": 20
```

para definir o tempo máximo de espera de uma requisição, e:

```python
"DOWNLOAD_DELAY": 0.2
```

para adicionar um pequeno intervalo entre as requisições.

O User-Agent utilizado simula um navegador comum.

---

## Comunicação entre Streamlit e Scrapy

Como o Scrapy possui seu próprio mecanismo de execução, a aplicação utiliza `multiprocessing`.

A arquitetura simplificada é:

```text
Streamlit
   │
   ├── Processo principal
   │
   └── Processo Scrapy
           │
           ├── WikipediaSpider
           │
           ├── Requisições
           │
           └── Extração
                  │
                  ↓
          multiprocessing.Queue
                  │
                  ↓
              Streamlit
```

A `Queue` permite que os resultados da coleta sejam enviados do processo do Scrapy para o processo principal da aplicação.

---

## BeautifulSoup x Scrapy

| Característica                    | Requests + BeautifulSoup | Scrapy              |
| --------------------------------- | ------------------------ | ------------------- |
| Requisições HTTP                  | Requests                 | Scrapy              |
| Análise HTML                      | BeautifulSoup            | Seletores do Scrapy |
| Estrutura                         | Mais simples             | Mais estruturada    |
| Facilidade para projetos pequenos | ⭐⭐⭐⭐⭐               | ⭐⭐⭐              |
| Escalabilidade                    | ⭐⭐⭐                   | ⭐⭐⭐⭐⭐          |
| Requisições concorrentes          | Manual                   | Nativa              |
| Spider                            | ❌                       | ✅                  |
| Pipeline de Scraping              | ❌                       | ✅                  |
| Controle de coleta                | Básico                   | Avançado            |
| Tempo de coleta                   | Não medido               | Medido              |
| Complexidade                      | Menor                    | Maior               |

---

## Exemplo de teste

Uma entrada recomendada para testar o sistema:

```text
Python,
Inteligência Artificial,
Machine Learning,
Ciência de Dados,
Banco de Dados
```

O sistema deverá:

1. Pesquisar os cinco termos;
2. Encontrar as páginas correspondentes;
3. Extrair os textos;
4. Juntar os conteúdos;
5. Remover as *stopwords*;
6. Apresentar as estatísticas;
7. Permitir pesquisar uma palavra;
8. Exibir o texto original;
9. Exibir o texto limpo;
10. Gerar a nuvem de palavras.

---

## Possíveis problemas

## `ModuleNotFoundError`

Caso apareça:

```text
ModuleNotFoundError: No module named 'streamlit'
```

instale as dependências:

```bash
pip install -r requirements.txt
```

---

## Imagem `wiki.jpeg` não encontrada

Caso apareça um erro relacionado a:

```text
wiki.jpeg
```

verifique se a imagem está no mesmo diretório do arquivo Python:

```text
web-scraping/
├── app_beautifulsoup.py
├── app_scrapy.py
└── wiki.jpeg
```

---

## Nenhuma página encontrada

A busca é realizada através da API da Wikipédia. Termos muito específicos ou inexistentes podem não retornar resultados.

Também é necessário possuir conexão com a Internet para acessar a API e as páginas da Wikipédia.

---

## Erro HTTP

Problemas de conexão, indisponibilidade temporária ou respostas HTTP diferentes de `200` podem impedir a extração.

A versão Scrapy apresenta esses erros individualmente na interface.

---

## User-Agent

As requisições utilizam um User-Agent semelhante ao de um navegador:

```text
Mozilla/5.0 (Windows NT 10.0; Win64; x64)
AppleWebKit/537.36
Chrome/120.0 Safari/537.36
```

Isso identifica a aplicação perante o servidor da Wikipédia como uma requisição HTTP realizada por um cliente semelhante a um navegador.

---

## Objetivo acadêmico

O projeto foi desenvolvido com o objetivo de demonstrar conceitos de:

* Web Scraping;
* Requisições HTTP;
* Consumo de API;
* Análise de HTML;
* Seletores CSS;
* Processamento de texto;
* *Stopwords*;
* Contagem de palavras;
* Visualização de dados;
* Nuvem de palavras;
* Streamlit;
* Scrapy;
* Processamento concorrente.

A existência de duas implementações permite comparar uma abordagem mais simples, utilizando **Requests + BeautifulSoup**, com uma abordagem baseada em framework de Web Scraping, utilizando **Scrapy**.

---

## Licença

Este projeto pode ser utilizado para fins acadêmicos e de estudo.

Ao realizar Web Scraping, respeite os termos de uso, políticas e regras dos sites acessados, além de evitar requisições excessivas aos servidores.

---

## Autor

André Luiz dos S. Cruz

Projeto desenvolvido para estudos de **Web Scraping, Python, processamento de texto e desenvolvimento de aplicações com Streamlit**.
