import requests
from bs4 import BeautifulSoup
import telegram
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
"https://www.idealista.pt/comprar-casas/braga/",
"https://www.imovirtual.com/comprar/apartamento/braga/",
"https://www.olx.pt/imoveis/apartamentos-casas-a-venda/braga/",
"https://casa.sapo.pt/comprar-apartamentos/braga/",
"https://supercasa.pt/comprar-casas/braga/"
]

HEADERS = {
"User-Agent": "Mozilla/5.0",
"Accept-Language": "pt-PT,pt;q=0.9"
}

HISTORICO_FILE = "historico.json"

PALAVRAS_RENOVAR = [
"remodelar",
"renovar",
"recuperar",
"obras",
"investimento",
"para renovar"
]

PALAVRAS_OPORTUNIDADE = [
"urgente",
"oportunidade",
"abaixo do mercado",
"preço negociável"
]

# ============================
# TELEGRAM
# ============================

bot = telegram.Bot(token=TOKEN)

bot.send_message(chat_id=CHAT_ID, text="✅ Teste agente Braga iniciado")

# ============================
# HISTORICO
# ============================

if os.path.exists(HISTORICO_FILE):

    try:
        with open(HISTORICO_FILE,"r") as f:
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

    for url in URLS:

        try:
            response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        continue

    soup = BeautifulSoup(response.text, "html.parser")

    anuncios = soup.select("article")

    print("ANUNCIOS ENCONTRADOS:", len(anuncios))

except Exception as e:
    print("Erro scraping:", e)
    continue

        print("ANUNCIOS ENCONTRADOS:", len(anuncios))

        for anuncio in anuncios:

            link_elem = anuncio.select_one("a")

            if not link_elem:
                continue

            link = link_elem.get("href")

except Exception as e:
   print("Erro scraping:", e)

        for anuncio in anuncios[:50]:

            link_elem = anuncio.select_one("a")

            if not link_elem:
                continue

            link = link_elem.get("href")

            if not link:
                continue

            link = urljoin(url,link)

            titulo = link_elem.text.strip()

            if not titulo:
                titulo = "Imóvel em Braga"

            texto = titulo.lower()

            if link in historico:
                continue

            historico.append(link)
            novos.append(link)

            total += 1

            if any(p in texto for p in PALAVRAS_RENOVAR) or any(p in texto for p in PALAVRAS_OPORTUNIDADE):

                oportunidades += 1

                mensagem = f"""
🏚 OPORTUNIDADE DETECTADA

{titulo}

{link}
"""

                try:
                    bot.send_message(chat_id=CHAT_ID,text=mensagem)
                except:
                    pass

    except Exception as e:
        print("Erro scraping:",e)

# ============================
# GUARDAR HISTORICO
# ============================

try:
    with open(HISTORICO_FILE,"w") as f:
        json.dump(historico,f)
except:
    pass

# ============================
# RELATORIO
# ============================

mensagem = f"""
📊 RELATÓRIO AGENTE BRAGA

Anúncios analisados: {total}

Novos encontrados: {len(novos)}

Oportunidades: {oportunidades}

Hora: {datetime.now()}
"""

try:
    bot.send_message(chat_id=CHAT_ID,text=mensagem)
except:
    pass
