import time
import re
import multiprocessing
import requests
import scrapy
import numpy as np

from scrapy.crawler import CrawlerProcess

import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from PIL import Image


# ============================================================
# CONFIGURAÇÃO DO STREAMLIT
# ============================================================

st.set_page_config(
    page_title="Web Scraping com Scrapy",
    page_icon="🕷️",
    layout="wide"
)


# ============================================================
# STOPWORDS
# ============================================================

stopwords_pt = {
    "de", "a", "o", "que", "e", "é", "do", "da", "em", "um", "uma",
    "para", "com", "não", "os", "as", "se", "na", "no", "por", "mais",
    "dos", "como", "mas", "ao", "ele", "das", "à", "seu", "sua", "ou",
    "quando", "muito", "nos", "já", "eu", "também", "só", "pelo",
    "pela", "até", "isso", "ela", "entre", "depois", "sem", "mesmo",
    "aos", "seus", "quem", "nas", "me", "esse", "eles", "essa", "num",
    "nem", "suas", "meu", "às", "minha", "numa", "pelos", "elas",
    "qual", "nós", "lhe", "deles", "essas", "esses", "pelas", "este",
    "dele", "tu", "te", "vocês", "vos", "lhes", "meus", "minhas",
    "teu", "tua", "teus", "tuas", "nosso", "nossa", "nossos", "nossas",
    "dela", "delas", "esta", "estes", "estas", "aquele", "aquela",
    "aqueles", "aquelas", "isto", "aquilo", "estou", "está", "estamos",
    "estão", "estive", "esteve", "estivemos", "estiveram", "foi",
    "são", "ser", "sendo", "sido", "tem", "há", "onde"
}


# ============================================================
# USER AGENT
# ============================================================

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0 Safari/537.36"
)


# ============================================================
# FUNÇÃO PARA ENCONTRAR A PÁGINA DA WIKIPÉDIA
# ============================================================

def buscar_pagina(termo):

    api_url = "https://pt.wikipedia.org/w/api.php"

    parametros = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": termo,
        "srlimit": 1
    }

    resposta = requests.get(
        api_url,
        params=parametros,
        headers={
            "User-Agent": USER_AGENT
        },
        timeout=20
    )

    resposta.raise_for_status()

    dados = resposta.json()

    resultados = (
        dados
        .get("query", {})
        .get("search", [])
    )

    if not resultados:
        return None, None

    titulo = resultados[0]["title"]

    # URL correta da Wikipédia
    from urllib.parse import quote

    titulo_url = quote(
        titulo.replace(" ", "_")
    )

    url = (
        "https://pt.wikipedia.org/wiki/"
        + titulo_url
    )

    return titulo, url


# ============================================================
# SPIDER
# ============================================================

class WikipediaSpider(scrapy.Spider):

    name = "wikipedia_spider"

    custom_settings = {
        "USER_AGENT": USER_AGENT,
        "LOG_ENABLED": False,
        "ROBOTSTXT_OBEY": False,
        "DOWNLOAD_TIMEOUT": 20,
        "CONCURRENT_REQUESTS": 5,
        "HTTPERROR_ALLOW_ALL": True,
        "DOWNLOAD_DELAY": 0.2
    }

    def __init__(
        self,
        urls=None,
        fila=None,
        *args,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        self.start_urls = urls or []

        self.fila = fila


    # ========================================================
    # PARSE
    # ========================================================

    def parse(self, response):

        # ----------------------------------------------------
        # MOSTRA STATUS HTTP
        # ----------------------------------------------------

        if response.status != 200:

            self.fila.put({
                "tipo": "erro",
                "url": response.url,
                "mensagem": f"HTTP {response.status}"
            })

            return


        # ----------------------------------------------------
        # VERIFICA SE É UMA PÁGINA DA WIKIPÉDIA
        # ----------------------------------------------------

        if "wikipedia.org/wiki/" not in response.url:

            self.fila.put({
                "tipo": "erro",
                "url": response.url,
                "mensagem": "URL não pertence à Wikipédia"
            })

            return


        # ----------------------------------------------------
        # TENTA ENCONTRAR O CONTEÚDO PRINCIPAL
        # ----------------------------------------------------

        seletores = [

            # Principal
            "#mw-content-text .mw-parser-output > p",

            # Alternativa
            ".mw-parser-output > p",

            # Outra alternativa
            "#mw-content-text p",

            # Último recurso
            "main p"
        ]


        paragrafos = []

        seletor_usado = None


        # ----------------------------------------------------
        # TESTA OS SELETORES
        # ----------------------------------------------------

        for seletor in seletores:

            encontrados = response.css(seletor)

            if encontrados:

                paragrafos = encontrados

                seletor_usado = seletor

                break


        # ----------------------------------------------------
        # EXTRAI TEXTO
        # ----------------------------------------------------

        textos = []


        for paragrafo in paragrafos:

            texto = paragrafo.xpath(
                "string(.)"
            ).get()


            if not texto:
                continue


            # Remove espaços duplicados
            texto = re.sub(
                r"\s+",
                " ",
                texto
            )


            texto = texto.strip()


            if not texto:
                continue


            # Evita parágrafos muito pequenos
            if len(texto) < 30:
                continue


            textos.append(texto)


        # ----------------------------------------------------
        # SE NÃO ENCONTROU PARÁGRAFOS
        # ----------------------------------------------------

        if not textos:

            # Tenta extrair diretamente do conteúdo principal
            conteudo = response.css(
                "#mw-content-text .mw-parser-output"
            )


            if conteudo:

                texto_alternativo = conteudo.xpath(
                    "string(.)"
                ).get()


                if texto_alternativo:

                    texto_alternativo = re.sub(
                        r"\s+",
                        " ",
                        texto_alternativo
                    ).strip()


                    if texto_alternativo:

                        textos = [
                            texto_alternativo
                        ]

                        seletor_usado = (
                            "#mw-content-text "
                            ".mw-parser-output"
                        )


        # ----------------------------------------------------
        # JUNTA OS PARÁGRAFOS
        # ----------------------------------------------------

        texto_pagina = " ".join(textos)


        # ----------------------------------------------------
        # ENVIA RESULTADO
        # ----------------------------------------------------

        if texto_pagina:

            self.fila.put({

                "tipo": "sucesso",

                "url": response.url,

                "texto": texto_pagina,

                "quantidade_paragrafos": len(textos),

                "seletor": seletor_usado
            })

        else:

            self.fila.put({

                "tipo": "erro",

                "url": response.url,

                "mensagem": (
                    "A página respondeu HTTP 200, "
                    "mas nenhum texto foi encontrado."
                )
            })


# ============================================================
# FUNÇÃO EXECUTADA PELO PROCESSO SEPARADO
# ============================================================

def executar_scrapy(urls, fila):

    inicio = time.perf_counter()


    processo = CrawlerProcess(
        settings={

            "USER_AGENT": USER_AGENT,

            "LOG_ENABLED": False,

            "ROBOTSTXT_OBEY": False,

            "DOWNLOAD_TIMEOUT": 20,

            "CONCURRENT_REQUESTS": 5,

            "HTTPERROR_ALLOW_ALL": True,

            "DOWNLOAD_DELAY": 0.2
        }
    )


    processo.crawl(
        WikipediaSpider,
        urls=urls,
        fila=fila
    )


    processo.start()


    fim = time.perf_counter()

    tempo = fim - inicio


    fila.put({

        "tipo": "finalizado",

        "tempo": tempo
    })


# ============================================================
# FUNÇÃO PRINCIPAL DE COLETA
# ============================================================

def coletar_texto_scrapy(urls):

    fila = multiprocessing.Queue()


    processo = multiprocessing.Process(

        target=executar_scrapy,

        args=(
            urls,
            fila
        )
    )


    processo.start()


    resultados = []

    tempo_execucao = 0


    while True:

        resultado = fila.get()


        if resultado["tipo"] == "sucesso":

            resultados.append(
                resultado
            )


        elif resultado["tipo"] == "erro":

            resultados.append(
                resultado
            )


        elif resultado["tipo"] == "finalizado":

            tempo_execucao = resultado["tempo"]

            break


    processo.join()


    # --------------------------------------------------------
    # JUNTA OS TEXTOS
    # --------------------------------------------------------

    textos = []


    for resultado in resultados:

        if resultado["tipo"] == "sucesso":

            if resultado.get("texto"):

                textos.append(
                    resultado["texto"]
                )


    texto_final = " ".join(textos)


    return {

        "texto": texto_final,

        "resultados": resultados,

        "tempo": tempo_execucao
    }


# ============================================================
# LIMPAR TEXTO
# ============================================================

def limpar_texto(texto):

    texto = texto.lower()


    # Remove URLs
    texto = re.sub(
        r"https?://\S+|www\.\S+",
        " ",
        texto
    )


    # Remove pontuação
    texto = re.sub(
        r"[^\w\s]",
        " ",
        texto,
        flags=re.UNICODE
    )


    # Divide em palavras
    palavras = texto.split()


    # Remove stopwords
    palavras_limpas = [

        palavra

        for palavra in palavras

        if palavra not in stopwords_pt

        and len(palavra) > 2
    ]


    return " ".join(
        palavras_limpas
    )


# ============================================================
# INTERFACE
# ============================================================

st.title(
    "🕷️ Web Scraping com Scrapy + Wikipédia"
)


st.write(
    """
    Digite **5 termos separados por vírgula**.

    O aplicativo encontrará as páginas correspondentes na Wikipédia,
    utilizará o **Scrapy** para extrair os parágrafos,
    juntará os textos, removerá as stopwords e permitirá
    pesquisar a frequência de uma palavra.
    """
)


# ============================================================
# ENTRADA
# ============================================================

entrada = st.text_input(

    "Digite 5 termos separados por vírgula:",

    placeholder=(
        "Universidade Federal do Rio Grande do Norte, "
        "Ciência de Dados, "
        "Aprendizado de Máquina, "
        "Engenharia de Software, "
        "Armazém de Dados"
    )
)


# ============================================================
# BOTÃO
# ============================================================

if st.button(
    "🕷️ Coletar e Processar",
    type="primary"
):

    if not entrada.strip():

        st.warning(
            "Digite os 5 termos."
        )

    else:

        # ----------------------------------------------------
        # SEPARA OS TERMOS
        # ----------------------------------------------------

        termos = [

            termo.strip()

            for termo in entrada.split(",")

            if termo.strip()
        ]


        # ----------------------------------------------------
        # VERIFICA QUANTIDADE
        # ----------------------------------------------------

        if len(termos) != 5:

            st.error(

                f"Você informou {len(termos)} termos. "

                "É necessário informar exatamente 5."
            )

        else:

            st.session_state["termos"] = termos


            # ------------------------------------------------
            # PROCURA AS PÁGINAS
            # ------------------------------------------------

            paginas = []


            with st.spinner(
                "🔎 Procurando as 5 páginas..."
            ):

                for termo in termos:

                    try:

                        titulo, url = buscar_pagina(
                            termo
                        )


                        if titulo and url:

                            paginas.append({

                                "termo": termo,

                                "titulo": titulo,

                                "url": url
                            })

                        else:

                            st.warning(
                                f"Nenhuma página encontrada para '{termo}'."
                            )


                    except Exception as erro:

                        st.error(
                            f"Erro ao buscar '{termo}': {erro}"
                        )


            # ------------------------------------------------
            # VERIFICA
            # ------------------------------------------------

            if not paginas:

                st.error(
                    "Nenhuma página foi encontrada."
                )

                st.stop()


            # ------------------------------------------------
            # URLs
            # ------------------------------------------------

            urls = [

                pagina["url"]

                for pagina in paginas
            ]


            # ------------------------------------------------
            # SCRAPY
            # ------------------------------------------------

            with st.spinner(
                "🕷️ Scrapy está extraindo os textos..."
            ):

                resultado = coletar_texto_scrapy(
                    urls
                )


            # ------------------------------------------------
            # TEXTO COMPLETO
            # ------------------------------------------------

            texto_completo = resultado["texto"]


            # ------------------------------------------------
            # LIMPA O TEXTO
            # ------------------------------------------------

            texto_limpo = limpar_texto(
                texto_completo
            )


            # ------------------------------------------------
            # SALVA NA SESSION
            # ------------------------------------------------

            st.session_state["paginas"] = paginas

            st.session_state["texto_completo"] = (
                texto_completo
            )

            st.session_state["texto_limpo"] = (
                texto_limpo
            )

            st.session_state["resultados_scrapy"] = (
                resultado["resultados"]
            )

            st.session_state["tempo_scrapy"] = (
                resultado["tempo"]
            )

            st.session_state["processado"] = True


            # ------------------------------------------------
            # MENSAGEM
            # ------------------------------------------------

            if texto_completo:

                st.success(
                    "✅ Coleta concluída! "
                    "Os textos foram extraídos pelo Scrapy."
                )

            else:

                st.error(
                    "❌ O Scrapy não conseguiu extrair texto "
                    "das páginas."
                )


# ============================================================
# RESULTADOS
# ============================================================

if st.session_state.get(
    "processado",
    False
):

    paginas = st.session_state["paginas"]

    texto_completo = (
        st.session_state["texto_completo"]
    )

    texto_limpo = (
        st.session_state["texto_limpo"]
    )

    resultados_scrapy = (
        st.session_state["resultados_scrapy"]
    )

    tempo_scrapy = (
        st.session_state["tempo_scrapy"]
    )


    # ========================================================
    # PÁGINAS
    # ========================================================

    st.divider()

    st.subheader(
        "📚 Páginas encontradas"
    )


    for pagina in paginas:

        st.markdown(
            f"**{pagina['titulo']}**"
        )

        st.caption(
            pagina["url"]
        )


    # ========================================================
    # RESULTADOS DO SCRAPY
    # ========================================================

    st.subheader(
        "🕷️ Resultado da coleta"
    )


    for resultado in resultados_scrapy:

        if resultado["tipo"] == "sucesso":

            st.success(

                f"✅ {resultado['url']} — "

                f"{resultado['quantidade_paragrafos']} "

                "blocos de texto extraídos"
            )


            if resultado.get("seletor"):

                st.caption(
                    f"Seletor utilizado: "
                    f"`{resultado['seletor']}`"
                )


        elif resultado["tipo"] == "erro":

            st.error(

                f"❌ {resultado['url']} — "

                f"{resultado['mensagem']}"
            )


    # ========================================================
    # MÉTRICAS
    # ========================================================

    palavras_originais = (
        texto_completo.split()
    )

    palavras_limpas = (
        texto_limpo.split()
    )


    st.divider()


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Páginas",
            len(paginas)
        )


    with col2:

        st.metric(
            "Palavras originais",
            f"{len(palavras_originais):,}".replace(
                ",",
                "."
            )
        )


    with col3:

        st.metric(
            "Palavras após limpeza",
            f"{len(palavras_limpas):,}".replace(
                ",",
                "."
            )
        )


    with col4:

        st.metric(
            "Tempo Scrapy",
            f"{tempo_scrapy:.4f} s"
        )


    # ========================================================
    # CONTADOR
    # ========================================================

    st.divider()

    st.subheader(
        "🔎 Contar palavra"
    )


    palavra = st.text_input(
        "Digite uma palavra:",
        placeholder="Exemplo: dados"
    )


    if palavra.strip():

        palavra_busca = (
            palavra
            .lower()
            .strip()
        )


        palavra_busca = re.sub(
            r"[^\w]",
            "",
            palavra_busca,
            flags=re.UNICODE
        )


        palavras = texto_limpo.split()


        quantidade = palavras.count(
            palavra_busca
        )


        st.info(

            f"A palavra **{palavra_busca}** "

            f"aparece **{quantidade} vezes** "

            "no texto das páginas."
        )


    # ========================================================
    # TEXTO ORIGINAL
    # ========================================================

    st.divider()


    with st.expander(
        "📄 Ver texto completo extraído pelo Scrapy"
    ):

        st.text_area(
            "Texto original:",
            texto_completo,
            height=400
        )


    # ========================================================
    # TEXTO LIMPO
    # ========================================================

    with st.expander(
        "🧹 Ver texto após remoção das stopwords"
    ):

        st.text_area(
            "Texto limpo:",
            texto_limpo,
            height=400
        )


    # ========================================================
    # NUVEM DE PALAVRAS
    # ========================================================

    mascara = np.array(Image.open("wiki.jpeg").convert("RGB"))

    st.divider()

    st.subheader(
        "☁️ Nuvem de Palavras"
    )


    if texto_limpo:

        wordcloud = WordCloud(

            width=1200,

            height=600,

            background_color="white",

            stopwords=stopwords_pt,

            collocations=False,

            min_font_size=10,
            mask=mascara,
            contour_width=1,
            contour_color='steelblue'

        ).generate(
            texto_limpo
        )


        fig, ax = plt.subplots(
            figsize=(14, 7)
        )


        ax.imshow(
            wordcloud,
            interpolation="bilinear"
        )


        ax.axis("off")


        st.pyplot(
            fig,
            use_container_width=True
        )


        plt.close(fig)


    else:

        st.warning(
            "Não existe texto suficiente para "
            "gerar a nuvem de palavras."
        )