# Web Scraping

import time
import requests
import numpy as np
from bs4 import BeautifulSoup
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from PIL import Image

inicio = time.perf_counter()

url = "https://pt.wikipedia.org/wiki/Ciência_de_dados"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

pagina = requests.get(url, headers=headers)

if pagina.status_code == 200:
    print("Página acessada com sucesso!")
else:
    print("Erro:", pagina.status_code)

dados_pagina = BeautifulSoup(pagina.text, 'html.parser')

div = dados_pagina.find('div', class_='mw-parser-output')

paragrafos = div.find_all('p')  # pega os parágrafos, não <section>

# concatena o texto de todos os parágrafos em uma única string
texto = " ".join(p.get_text() for p in paragrafos)

mascara = np.array(Image.open("wiki.jpeg").convert("RGB"))  # substitua pelo caminho da sua imagem de máscara

stopwords_pt = set([
    "de", "a", "o", "que", "e", "é", "do", "da", "em", "um", "uma", "para",
    "com", "não", "os", "as", "se", "na", "no", "por", "mais", "as", "dos",
    "como", "mas", "ao", "ele", "das", "à", "seu", "sua", "ou", "quando",
    "muito", "nos", "já", "eu", "também", "só", "pelo", "pela", "até",
    "isso", "ela", "entre", "depois", "sem", "mesmo", "aos", "seus",
    "quem", "nas", "me", "esse", "eles", "essa", "num", "nem", "suas",
    "meu", "às", "minha", "numa", "pelos", "elas", "qual", "nós", "lhe",
    "deles", "essas", "esses", "pelas", "este", "dele", "tu", "te", "vocês",
    "vos", "lhes", "meus", "minhas", "teu", "tua", "teus", "tuas", "nosso",
    "nossa", "nossos", "nossas", "dela", "delas", "esta", "estes", "estas",
    "aquele", "aquela", "aqueles", "aquelas", "isto", "aquilo", "estou",
    "está", "estamos", "estão", "estive", "esteve", "estivemos", "estiveram",
    "foi", "são", "ser", "sendo", "sido", "tem", "há", "onde"
])

wordcloud = WordCloud(
    width=800,
    height=400,
    background_color='white',
    mask=mascara,
    stopwords=stopwords_pt,
    contour_width=1,
    contour_color='steelblue'
).generate(texto)

plt.imshow(mascara, cmap='gray')
plt.axis('off')
plt.savefig('debug_mascara.png')

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.savefig('nuvem_palavras.png', bbox_inches='tight')
print("Imagem salva como nuvem_palavras.png")

fim = time.perf_counter()
tempo_execucao = fim - inicio

print(f"Tempo de execução (requests+BS4): {tempo_execucao:.4f} segundos")


