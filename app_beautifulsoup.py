
import streamlit as st
import requests
import re
import unicodedata
import numpy as np
import time

from bs4 import BeautifulSoup
from wordcloud import WordCloud
from PIL import Image
import matplotlib.pyplot as plt


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Contador de Palavras - Web Scraping",
    page_icon="🔎",
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
# CONFIGURAÇÃO DO REQUEST
# ============================================================

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


# ============================================================
# FUNÇÃO PARA LIMPAR TEXTO
# ============================================================

def limpar_texto(texto):
    """
    Remove pontuação, transforma em minúsculo
    e remove as stopwords.
    """

    # Coloca tudo em minúsculo
    texto = texto.lower()

    # Remove pontuação, mantendo letras acentuadas
    texto = re.sub(r"[^\w\s]", " ", texto, flags=re.UNICODE)

    # Divide o texto em palavras
    palavras = texto.split()

    # Remove stopwords
    palavras_limpas = [
        palavra
        for palavra in palavras
        if palavra not in stopwords_pt
    ]

    return " ".join(palavras_limpas)


# ============================================================
# FUNÇÃO PARA BUSCAR PÁGINA DA WIKIPÉDIA
# ============================================================

def buscar_pagina(termo):
    """
    Busca uma página correspondente ao termo na Wikipédia
    utilizando a API da Wikipédia.

    Retorna:
        titulo
        url
        tempo_busca
    """

    # Início da medição do tempo da pesquisa
    inicio = time.perf_counter()

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
        headers=headers,
        timeout=15
    )

    resposta.raise_for_status()

    dados = resposta.json()

    resultados = dados.get("query", {}).get("search", [])

    # Final da medição
    fim = time.perf_counter()

    tempo_busca = fim - inicio

    if not resultados:
        return None, None, tempo_busca

    titulo = resultados[0]["title"]

    # Monta a URL da página
    titulo_url = titulo.replace(" ", "_")

    url = f"https://pt.wikipedia.org/wiki/{titulo_url}"

    return titulo, url, tempo_busca


# ============================================================
# FUNÇÃO PARA EXTRAIR TEXTO
# ============================================================

def extrair_texto(url):
    """
    Acessa uma página da Wikipédia e extrai
    os parágrafos do conteúdo principal.

    Retorna:
        texto
        tempo_extracao
    """

    # Início da medição da extração
    inicio = time.perf_counter()

    resposta = requests.get(
        url,
        headers=headers,
        timeout=15
    )

    resposta.raise_for_status()

    soup = BeautifulSoup(
        resposta.text,
        "html.parser"
    )

    # Conteúdo principal da Wikipédia
    div = soup.find(
        "div",
        class_="mw-parser-output"
    )

    if not div:

        fim = time.perf_counter()

        return "", fim - inicio

    paragrafos = div.find_all("p")

    texto = " ".join(
        paragrafo.get_text(" ", strip=True)
        for paragrafo in paragrafos
    )

    # Final da medição da extração
    fim = time.perf_counter()

    tempo_extracao = fim - inicio

    return texto, tempo_extracao


# ============================================================
# INTERFACE
# ============================================================

st.title("🔎 Web Scraping - Contador de Palavras")

st.write(
    """
    Digite **5 termos separados por vírgula**. 
    O aplicativo buscará as páginas correspondentes na Wikipédia,
    extrairá seus conteúdos e juntará tudo em um único texto.
    """
)


# ============================================================
# ENTRADA DOS 5 TERMOS
# ============================================================

entrada_termos = st.text_input(
    "Digite 5 termos separados por vírgula:",
    placeholder=(
        "Digite 5 termos, por exemplo: dados, machine learning, python, web scraping, inteligência artificial"
    )
)


# ============================================================
# BOTÃO DE EXECUÇÃO
# ============================================================

if st.button("🚀 Buscar páginas", type="primary"):

    if not entrada_termos.strip():

        st.warning("Digite os 5 termos.")

    else:

        # Separa os termos usando vírgula
        termos = [
            termo.strip()
            for termo in entrada_termos.split(",")
            if termo.strip()
        ]

        # Verifica quantidade
        if len(termos) != 5:

            st.error(
                f"Você informou {len(termos)} termos. "
                "É necessário informar exatamente 5."
            )

        else:

            # ====================================================
            # INÍCIO DO TEMPO TOTAL
            # ====================================================

            inicio_total = time.perf_counter()

            textos = []
            paginas = []
            tempos_busca = []

            progresso = st.progress(0)

            # ====================================================
            # BUSCA DOS 5 TERMOS
            # ====================================================

            for i, termo in enumerate(termos):

                # Tempo total deste termo
                inicio_termo = time.perf_counter()

                try:

                    # ------------------------------------------------
                    # BUSCA NA API DA WIKIPÉDIA
                    # ------------------------------------------------

                    titulo, url, tempo_busca = buscar_pagina(termo)

                    tempos_busca.append({
                        "termo": termo,
                        "tempo_busca": tempo_busca
                    })

                    if titulo is None:

                        st.warning(
                            f"Nenhuma página encontrada para: {termo}"
                        )

                        progresso.progress(
                            (i + 1) / len(termos)
                        )

                        continue

                    # ------------------------------------------------
                    # EXTRAÇÃO DA PÁGINA
                    # ------------------------------------------------

                    texto, tempo_extracao = extrair_texto(url)

                    # ------------------------------------------------
                    # TEMPO TOTAL DO TERMO
                    # ------------------------------------------------

                    fim_termo = time.perf_counter()

                    tempo_total_termo = (
                        fim_termo - inicio_termo
                    )

                    if texto:

                        textos.append(texto)

                        paginas.append({
                            "termo": termo,
                            "titulo": titulo,
                            "url": url,
                            "texto": texto,
                            "tempo_busca": tempo_busca,
                            "tempo_extracao": tempo_extracao,
                            "tempo_total": tempo_total_termo
                        })

                        st.success(
                            f"Página encontrada: {titulo}"
                        )

                        # ------------------------------------------------
                        # MOSTRA O TEMPO DO TERMO
                        # ------------------------------------------------

                        st.caption(
                            f"⏱️ Pesquisa: {tempo_busca:.4f} s | "
                            f"Extração: {tempo_extracao:.4f} s | "
                            f"Total: {tempo_total_termo:.4f} s"
                        )

                    else:

                        st.warning(
                            f"A página '{titulo}' não possui texto."
                        )

                except requests.RequestException as erro:

                    fim_termo = time.perf_counter()

                    tempo_total_termo = (
                        fim_termo - inicio_termo
                    )

                    st.error(
                        f"Erro ao acessar '{termo}': {erro}"
                    )

                    st.caption(
                        f"⏱️ Tempo até o erro: "
                        f"{tempo_total_termo:.4f} s"
                    )

                progresso.progress(
                    (i + 1) / len(termos)
                )


            # ====================================================
            # FINAL DO TEMPO TOTAL
            # ====================================================

            fim_total = time.perf_counter()

            tempo_total = fim_total - inicio_total


            # ====================================================
            # RESULTADO DO TEMPO DE BUSCA
            # ====================================================

            st.divider()

            st.subheader("⏱️ Desempenho da busca")

            # ----------------------------------------------------
            # MÉTRICAS
            # ----------------------------------------------------

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Tempo total",
                    f"{tempo_total:.4f} s"
                )

            with col2:

                if paginas:

                    tempo_medio = (
                        sum(
                            pagina["tempo_total"]
                            for pagina in paginas
                        )
                        / len(paginas)
                    )

                else:

                    tempo_medio = 0

                st.metric(
                    "Tempo médio por página",
                    f"{tempo_medio:.4f} s"
                )

            with col3:

                st.metric(
                    "Páginas processadas",
                    len(paginas)
                )


            # ----------------------------------------------------
            # DETALHAMENTO DOS TEMPOS
            # ----------------------------------------------------

            for pagina in paginas:

                with st.expander(
                    f"🔎 {pagina['termo']}"
                ):

                    st.write(
                        f"**Página:** {pagina['titulo']}"
                    )

                    st.write(
                        f"**⏱️ Tempo de pesquisa na API:** "
                        f"{pagina['tempo_busca']:.4f} segundos"
                    )

                    st.write(
                        f"**🌐 Tempo de extração:** "
                        f"{pagina['tempo_extracao']:.4f} segundos"
                    )

                    st.write(
                        f"**⚡ Tempo total:** "
                        f"{pagina['tempo_total']:.4f} segundos"
                    )


            # ====================================================
            # JUNTA OS TEXTOS
            # ====================================================

            if textos:

                texto_completo = " ".join(textos)

                # Limpa o texto
                texto_limpo = limpar_texto(
                    texto_completo
                )

                # Salva na sessão
                st.session_state["texto_completo"] = texto_completo
                st.session_state["texto_limpo"] = texto_limpo
                st.session_state["paginas"] = paginas
                st.session_state["tempo_total"] = tempo_total

                st.success(
                    f"{len(textos)} páginas foram processadas!"
                )


# ============================================================
# RESULTADOS
# ============================================================

if "paginas" in st.session_state:

    st.divider()

    st.subheader("📚 Páginas encontradas")

    for pagina in st.session_state["paginas"]:

        st.markdown(
            f"- **{pagina['titulo']}** "
            f"([abrir página]({pagina['url']}))"
        )


    # ========================================================
    # ESTATÍSTICAS
    # ========================================================

    texto_completo = st.session_state["texto_completo"]
    texto_limpo = st.session_state["texto_limpo"]

    palavras_original = texto_completo.split()
    palavras_limpo = texto_limpo.split()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Páginas processadas",
            len(st.session_state["paginas"])
        )

    with col2:

        st.metric(
            "Palavras originais",
            len(palavras_original)
        )

    with col3:

        st.metric(
            "Palavras após limpeza",
            len(palavras_limpo)
        )


    # ========================================================
    # TEMPO TOTAL
    # ========================================================

    st.info(
        f"⏱️ **Tempo total da busca:** "
        f"{st.session_state['tempo_total']:.4f} segundos"
    )


    # ========================================================
    # PALAVRA PARA PESQUISA
    # ========================================================

    st.divider()

    st.subheader("🔍 Contar palavra")

    palavra = st.text_input(
        "Digite uma palavra:",
        placeholder="Exemplo: dados"
    )


    if palavra.strip():

        # Normaliza a palavra pesquisada
        palavra_busca = palavra.lower().strip()

        # Remove pontuação
        palavra_busca = re.sub(
            r"[^\w\s]",
            "",
            palavra_busca,
            flags=re.UNICODE
        )

        # Divide o texto limpo em palavras
        palavras = texto_limpo.split()

        # Conta ocorrências exatas
        quantidade = palavras.count(
            palavra_busca
        )

        st.success(
            f"A palavra **{palavra_busca}** "
            f"aparece **{quantidade} vezes** "
            f"no texto das páginas processadas."
        )


    # ========================================================
    # MOSTRAR TEXTO
    # ========================================================

    with st.expander("📄 Ver texto completo original"):

        st.text_area(
            "Texto extraído:",
            texto_completo,
            height=300
        )


    with st.expander("🧹 Ver texto após remoção das stopwords"):

        st.text_area(
            "Texto limpo:",
            texto_limpo,
            height=300
        )


    # ============================================================
    # NUVEM DE PALAVRAS
    # ============================================================

    mascara = np.array(
        Image.open("wiki.jpeg").convert("RGB")
    )

    st.divider()

    st.subheader("☁️ Nuvem de Palavras")

    if texto_limpo:

        wordcloud = WordCloud(
            width=800,
            height=600,
            background_color="white",
            stopwords=stopwords_pt,
            collocations=False,
            mask=mascara,
            contour_width=1,
            contour_color='steelblue'
        ).generate(texto_limpo)

        fig, ax = plt.subplots(figsize=(14, 7))

        ax.imshow(
            wordcloud,
            interpolation="bilinear"
        )

        ax.axis("off")

        st.pyplot(fig)

        plt.close(fig)

    else:

        st.warning(
            "Não foi possível gerar a nuvem de palavras."
        )
