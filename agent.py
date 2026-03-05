import requests
from bs4 import BeautifulSoup
from datetime import datetime
import telegram

TOKEN =8748185653:AAEPBPxz5Qfc_W5PtyWEJmTWG_AQowYTBwY
CHAT_ID ="8248415390"

bot = telegram.Bot(token=TOKEN)

URL = "https://www.idealista.pt/comprar-casas/braga/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(URL, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

anuncios = soup.select(".item")

relatorio = "RELATORIO IA IMOVEIS BRAGA\n\n"

palavras_remodelar = [
"remodelar",
"recuperar",
"obras",
"para renovar",
"investimento"
]

for anuncio in anuncios:

    titulo = anuncio.select_one(".item-link")
    preco = anuncio.select_one(".item-price")

    if titulo and preco:

        titulo = titulo.text.strip()
        preco = preco.text.strip()

        oportunidade = False

        for palavra in palavras_remodelar:
            if palavra in titulo.lower():
                oportunidade = True

        if oportunidade:

            relatorio += f"🏚 Remodelação: {titulo}\n"
            relatorio += f"Preço: {preco}\n\n"

        else:

            relatorio += f"Imóvel: {titulo}\n"
            relatorio += f"Preço: {preco}\n\n"

relatorio += f"\nData: {datetime.now()}"

import asyncio

async def enviar():
    await bot.send_message(chat_id=CHAT_ID, text=relatorio)

asyncio.run(enviar())
