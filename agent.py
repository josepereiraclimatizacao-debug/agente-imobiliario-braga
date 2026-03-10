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

PRECO_MAX = 125000

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
"(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

HISTORICO_FILE = "historico.json"

TIPOLOGIAS = ["t0","t1","t2"]

ZONAS_UNIVERSIDADE = [
"gualtar",
"universidade",
"campus",
"são vítor",
"são vicente"
]

PALAVRAS_OPORTUNIDADE = [
"remodelar",
"renovar",
"recuperar",
"obras",
"urgente",
"oportunidade",
"negociável",
"abaixo do mercado"
]

PALAVRAS_PREMERCADO = [
"herança",
"banco",
"leilão",
"venda urgente",
"particular"
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
        requests.post(url,data=data)
    except:
        pass

enviar_telegram("🤖 Agente Braga iniciado")

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

    try:

        print("A analisar:",url)

        response = requests.get(url,headers=HEADERS,timeout=15)

        if response.status_code != 200:
            print("Erro acesso:",url)
            continue

        soup = BeautifulSoup(response.text,"html.parser")

        anuncios = soup.select("article, .item, .offer-item, .listing-item")

        print("Anuncios encontrados:",len(anuncios))

        for anuncio in anuncios[:80]:

            link_elem = anuncio.select_one("a")

            if not link_elem:
                continue

            link = link_elem.get("href")

            if not link:
                continue

            link = urljoin(url,link)

            titulo = link_elem.text.strip()

            if not titulo:
                titulo = "Imóvel Braga"

            texto = titulo.lower()

            # ============================
            # TIPologia
            # ============================

            if not any(t in texto for t in TIPOLOGIAS):
                continue

            # ============================
            # ZONA UNIVERSIDADE
            # ============================

            if not any(z in texto for z in ZONAS_UNIVERSIDADE):
                continue

            # ============================
            # PREÇO
            # ============================

            preco_elem = anuncio.select_one(".price,.value,.listing-price")

            preco = 0

            if preco_elem:

                texto_preco = preco_elem.text.replace("€","").replace(".","").replace(" ","")

                try:
                    preco = int(texto_preco)
                except:
                    preco = 0

            if preco > PRECO_MAX:
                continue

            # ============================
            # HISTORICO
            # ============================

            if link in historico:
                continue

            historico.append(link)

            novos.append(link)

            total += 1

            mensagem = f"""
🏠 Novo apartamento encontrado

{titulo}

Preço: {preco}€

{link}
"""

            enviar_telegram(mensagem)

            # ============================
            # OPORTUNIDADES
            # ============================

            if any(p in texto for p in PALAVRAS_OPORTUNIDADE):

                oportunidades += 1

                alerta = f"""
🚨 OPORTUNIDADE

{titulo}

Preço: {preco}€

{link}
"""

                enviar_telegram(alerta)

            # ============================
            # PRÉ MERCADO
            # ============================

            if any(p in texto for p in PALAVRAS_PREMERCADO):

                alerta = f"""
💰 POSSÍVEL NEGÓCIO PRÉ-MERCADO

{titulo}

Preço: {preco}€

{link}
"""

                enviar_telegram(alerta)

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

Analisados: {total}

Novos: {len(novos)}

Oportunidades: {oportunidades}

Hora: {datetime.now()}
"""

enviar_telegram(mensagem)
