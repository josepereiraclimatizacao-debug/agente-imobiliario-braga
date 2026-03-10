import requests
from bs4 import BeautifulSoup
import re
import math
import time
from datetime import datetime

# =========================
# TELEGRAM
# =========================

TOKEN = "8748185653:AAG5nXSBrbay_34zVtd7dUJFblvDy7XsaNc"
CHAT_ID = "8248415390"

def telegram(msg):

    try:

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

        requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": msg
            },
            timeout=10
        )

    except:
        pass


# =========================
# CONFIG
# =========================

PRECO_MAX = 200000

UNI_LAT = 41.561
UNI_LON = -8.397

VEL_PE = 4.5


# =========================
# DISTÂNCIA
# =========================

def distancia(lat1, lon1, lat2, lon2):

    R = 6371000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c


# =========================
# EXTRAIR PREÇO CORRECTO
# =========================

def extrair_preco(html):

    valores = re.findall(r"\d[\d\.\s]*\s?€", html)

    precos = []

    for v in valores:

        numero = re.sub(r"[^\d]", "", v)

        if numero:

            valor = int(numero)

            if 20000 < valor < 2000000:

                precos.append(valor)

    if not precos:
        return None

    return max(precos)


# =========================
# EXTRAIR ÁREA
# =========================

def extrair_area(html):

    m = re.search(r"(\d{2,4})\s?m²", html)

    if m:

        return int(m.group(1))

    return None


# =========================
# SCRAPE LINK
# =========================

def analisar_link(link):

    try:

        r = requests.get(link, timeout=15, headers={"User-Agent":"Mozilla/5.0"})

        html = r.text

        preco = extrair_preco(html)

        if not preco:
            return None

        if preco > PRECO_MAX:
            return None

        area = extrair_area(html)

        return preco, area

    except:

        return None


# =========================
# BUSCA LINKS DUCKDUCKGO
# =========================

def procurar_links():

    query = "apartamento braga site:imovirtual.com OR site:idealista.pt OR site:supercasa.pt OR site:casa.sapo.pt"

    url = "https://duckduckgo.com/html/?q=" + query.replace(" ","+")

    r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})

    soup = BeautifulSoup(r.text,"html.parser")

    links = []

    for a in soup.select("a.result__a"):

        link = a.get("href")

        if link:

            links.append(link)

    return links


# =========================
# AGENTE
# =========================

print("AGENTE IMOBILIARIO BRAGA V29")

links = procurar_links()

print("Links encontrados:", len(links))

enviados = 0


for link in links:

    print("Analisar:", link)

    dados = analisar_link(link)

    if not dados:
        continue

    preco, area = dados

    distancia_m = 0
    tempo = 0

    msg = f"""
🏠 IMÓVEL DETECTADO

Preço: {preco} €

Área: {area if area else "N/D"} m²

Distância Universidade: {int(distancia_m)} m

Tempo a pé: {tempo} min

{link}
"""

    telegram(msg)

    enviados += 1

    time.sleep(2)


telegram(f"""
📊 RELATÓRIO AGENTE BRAGA

Links analisados: {len(links)}

Imóveis enviados: {enviados}

Hora: {datetime.now()}
""")

print("Fim execução")
