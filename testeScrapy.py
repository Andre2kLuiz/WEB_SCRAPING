import time
import scrapy
from scrapy.crawler import CrawlerProcess

class WikipediaSpider(scrapy.Spider):
    name = "wikipedia_spider"

    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "LOG_ENABLED": False,  # evita poluir a saída com logs do Scrapy
    }

    def __init__(self, urls, resultado, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = urls
        self.resultado = resultado  # lista compartilhada para guardar os textos

    def parse(self, response):
        paragrafos = response.css("div.mw-parser-output > p::text").getall()
        texto_pagina = " ".join(paragrafos)
        self.resultado.append(texto_pagina)


def coletar_texto_scrapy(urls):
    resultado = []

    inicio = time.perf_counter()

    process = CrawlerProcess()
    process.crawl(WikipediaSpider, urls=urls, resultado=resultado)
    process.start()  # bloqueia até todas as URLs serem processadas

    fim = time.perf_counter()
    tempo_execucao = fim - inicio

    texto_final = " ".join(resultado)

    print(f"[Scrapy] Tempo: {tempo_execucao:.4f}s")

    return texto_final


# --- uso ---
urls = [
    "https://pt.wikipedia.org/wiki/Ciência_de_dados",
    "https://pt.wikipedia.org/wiki/Aprendizado_de_máquina",
    # ... demais URLs dos 5 termos
]

texto = coletar_texto_scrapy(urls)