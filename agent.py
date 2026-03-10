import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from urllib.parse import urljoin

# ============================
# CONFIG
# ============================

TOKEN = "8748185653:AAG5nXSBrbay_34zVtd7dUJFblvDy7XsaNc"
CHAT_ID = "8248415390"

URLS = [
    "https://www.imovirtual.com/comprar/apartamento/braga/",
    "https://www.idealista.pt/comprar-casas/braga/",
    "https://www.olx.pt/imoveis/apartamentos-casas-a-venda/braga/",
    "https://casa.sapo.pt/comprar-apartamentos/braga/",
    "https://supercasa.pt/comprar-casas/braga/"
]

HEADERS = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "pt-PT,pt;q=0.9"
}

HISTORICO_FILE = "historico.json"

PALAVRAS_OPORTUNIDADE = [
    "remodelar",
    "renovar",
    "recuperar",
    "obras",
    "urgente",
    "oportunidade",
    "abaixo do mercado",
    "negociável"
]

# ============================
# TELEGRAM
# ============================

def enviar_telegram(texto):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": texto
    }

    try:
        requests.post(url, data=data)
    except:
        pass


enviar_telegram("🤖 Agente imobiliário Braga iniciado")

# ============================
# HISTÓRICO
# ============================

if os.path.exists(HISTORICO_FILE):

    try:
        with open(HISTORICO_FILE, "r") as f:
            historico = json.load(f)
    except:
        historico = []

else:
    historico = []

historico = historico[-2000:]

# ============================
# SCRAPING
# ============================

total = 0
novos = []
oportunidades = 0

for url in URLS:

    try:

        print("A analisar:", url)

        response = requests.get(url, headers=HEADERS, timeout=15)

        if response.status_code != 200:
            print("Erro acesso:", url)
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        anuncios = soup.select("article, .item, .offer-item, .listing-item")

        print("ANUNCIOS ENCONTRADOS:", len(anuncios))

        for anuncio in anuncios[:60]:

            link_elem = anuncio.select_one("a")

            if not link_elem:
                continue

            link = link_elem.get("href")

            if not link:
                continue

            link = urljoin(url, link)

            titulo = link_elem.text.strip()

            if not titulo:
                titulo = "Imóvel em Braga"

            texto = titulo.lower()

            if link in historico:
                continue

            historico.append(link)
            novos.append(link)

            total += 1

            mensagem = f"""
🏠 Novo anúncio encontrado

{titulo}

{link}
"""

            enviar_telegram(mensagem)

            if any(p in texto for p in PALAVRAS_OPORTUNIDADE):

                oportunidades += 1

                alerta = f"""
🚨 OPORTUNIDADE DETECTADA

{titulo}

{link}
"""

                enviar_telegram(alerta)

    except Exception as e:

        print("Erro scraping:", e)

        continue

# ============================
# GUARDAR HISTÓRICO
# ============================

try:

    with open(HISTORICO_FILE, "w") as f:
        json.dump(historico, f)

except:
    pass

# ============================
# RELATÓRIO
# ============================

mensagem = f"""
📊 RELATÓRIO AGENTE BRAGA

Anúncios analisados: {total}

Novos encontrados: {len(novos)}

Oportunidades: {oportunidades}

Hora: {datetime.now()}
"""

enviar_telegram(mensagem)
