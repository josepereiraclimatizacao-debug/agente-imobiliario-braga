import requests
from bs4 import BeautifulSoup
import telegram
import asyncio
import json
import os
from datetime import datetime

# =========================
# CONFIG
# =========================

TOKEN = "8748185653:AAG5nXSBrbay_34zVtd7dUJFblvDy7XsaNc"
CHAT_ID = "8248415390"

URLS = [
"https://www.idealista.pt/comprar-casas/braga/",
"https://www.imovirtual.com/comprar/apartamento/braga/",
"https://www.olx.pt/imoveis/apartamentos-casas-a-venda/braga/",
"https://casa.sapo.pt/comprar-apartamentos/braga/",
"https://supercasa.pt/comprar-casas/braga"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive"
}

HISTORICO_FILE = "historico.json"

PALAVRAS_RENOVAR = [
    "remodelar",
    "renovar",
    "recuperar",
    "obras",
    "investimento"
]

bot = telegram.Bot(token=TOKEN)

# =========================
# HISTÓRICO
# =========================

if os.path.exists(HISTORICO_FILE):

    with open(HISTORICO_FILE, "r") as f:
        historico = json.load(f)

else:

    historico = []

# =========================
# SCRAPING
# =========================

for URL in URLS:
    response = requests.get(URL, headers=HEADERS)

    soup = BeautifulSoup(response.text, "html.parser")

    anuncios = soup.select(".item")

soup = BeautifulSoup(response.text, "html.parser")

anuncios = soup.select(".item")

novos = []

total = 0
oportunidades = 0

for anuncio in anuncios[:30]:

    total += 1

    titulo_elem = anuncio.select_one(".item-link")
    preco_elem = anuncio.select_one(".item-price")
    local_elem = anuncio.select_one(".item-location")
    detalhe_elem = anuncio.select_one(".item-detail")

    if titulo_elem and preco_elem:

        titulo = titulo_elem.text.strip()
        preco_txt = preco_elem.text.strip()

        preco = int(preco_txt.replace("€","").replace(".","").strip())

        if local_elem:
            local = local_elem.text.strip()
        else:
            local = "Braga"

        area = None

        if detalhe_elem:
            detalhes = detalhe_elem.text
            if "m²" in detalhes:
                try:
                    area = int(detalhes.split("m²")[0].split()[-1])
                except:
                    area = None

        if area:
            preco_m2 = round(preco / area)
        else:
            preco_m2 = "?"

        link = titulo_elem.get("href")
        link = "https://www.idealista.pt" + link

        if link not in historico:

            oportunidade = False

            if preco < 120000:
                oportunidade = True

            for palavra in PALAVRAS_RENOVAR:
                if palavra in titulo.lower():
                    oportunidade = True

            rent_estudante = round((preco * 0.06) / 12)

            if oportunidade:

                oportunidades += 1

                texto = f"""
🔥 OPORTUNIDADE

🏠 {titulo}

📍 {local}

💰 {preco_txt}

📐 {area} m²
💰 €/m² {preco_m2}

🏫 Renda estudante estimada
≈ {rent_estudante} €/mês

🔗 {link}
"""

            else:

                texto = f"""
🏠 Apartamento novo

{titulo}

📍 {local}

💰 {preco_txt}

📐 {area} m²
💰 €/m² {preco_m2}

🔗 {link}
"""

            novos.append(texto)

            historico.append(link)

# =========================
# GUARDAR HISTÓRICO
# =========================

with open(HISTORICO_FILE, "w") as f:
    json.dump(historico, f)

# =========================
# RELATÓRIO
# =========================

relatorio = f"""
📊 RELATÓRIO AGENTE BRAGA

Anúncios analisados: {total}

Novos encontrados: {len(novos)}

Oportunidades: {oportunidades}

Hora: {datetime.now()}
"""

# =========================
# TELEGRAM
# =========================

async def enviar():

    if novos:

        for msg in novos:

            await bot.send_message(
                chat_id=CHAT_ID,
                text=msg
            )

    await bot.send_message(
        chat_id=CHAT_ID,
        text=relatorio
    )

asyncio.run(enviar())
