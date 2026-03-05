import requests
from bs4 import BeautifulSoup
from datetime import datetime
import telegram
import asyncio
import json
import os

TOKEN = "COLE_AQUI_O_TESEU_TOKEN"
CHAT_ID = "8248415390"

bot = telegram.Bot(token=TOKEN)

URL = "https://www.idealista.pt/comprar-casas/braga/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

# carregar histórico
historico_file = "historico.json"

if os.path.exists(historico_file):
    with open(historico_file, "r") as f:
        historico = json.load(f)
else:
    historico = []

response = requests.get(URL, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

anuncios = soup.select(".item")

novos_anuncios = []

for anuncio in anuncios[:20]:

    titulo_tag = anuncio.select_one(".item-link")
    preco_tag = anuncio.select_one(".item-price")
    link_tag = anuncio.select_one(".item-link")

    if titulo_tag and preco_tag and link_tag:

        titulo = titulo_tag.text.strip()
        preco = preco_tag.text.strip()

        link = link_tag.get("href")

        if link.startswith("/"):
            link = "https://www.idealista.pt" + link

        if link not in historico:

            novos_anuncios.append({
                "titulo": titulo,
                "preco": preco,
                "link": link
            })

            historico.append(link)

# guardar histórico
with open(historico_file, "w") as f:
    json.dump(historico, f)

mensagem = "🏠 NOVOS IMÓVEIS EM BRAGA\n\n"

if novos_anuncios:

    for imovel in novos_anuncios[:10]:

        mensagem += f"{imovel['titulo']}\n"
        mensagem += f"💰 {imovel['preco']}\n"
        mensagem += f"{imovel['link']}\n\n"

else:
    mensagem += "Nenhum novo imóvel encontrado."

mensagem += f"\nData: {datetime.now()}"

async def enviar():
    await bot.send_message(chat_id=CHAT_ID, text=mensagem)

asyncio.run(enviar())
