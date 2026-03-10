import requests
from bs4 import BeautifulSoup
import json
import os
import re
import math
from datetime import datetime

TOKEN="8748185653:AAG5nXSBrbay_34zVtd7dUJFblvDy7XsaNc"
CHAT_ID="8248415390"

PRECO_MAX=200000

UNI_LAT=41.561
UNI_LON=-8.397
VEL_PE=4.5

HISTORICO_FILE="historico.json"

HEADERS={"User-Agent":"Mozilla/5.0"}

# =========================
# TELEGRAM
# =========================

def telegram(msg):

    try:

        url=f"https://api.telegram.org/bot{TOKEN}/sendMessage"

        requests.post(url,data={
        "chat_id":CHAT_ID,
        "text":msg
        })

    except:

        pass


# =========================
# HISTORICO
# =========================

if os.path.exists(HISTORICO_FILE):

    try:
        with open(HISTORICO_FILE,"r") as f:
            historico=json.load(f)
    except:
        historico=[]

else:
    historico=[]

historico=historico[-10000:]


# =========================
# DISTANCIA UNIVERSIDADE
# =========================

def distancia():

    lat=41.55
    lon=-8.42

    R=6371

    dlat=math.radians(lat-UNI_LAT)
    dlon=math.radians(lon-UNI_LON)

    a=math.sin(dlat/2)**2 + math.cos(math.radians(UNI_LAT))*math.cos(math.radians(lat))*math.sin(dlon/2)**2

    c=2*math.atan2(math.sqrt(a),math.sqrt(1-a))

    dist=R*c

    dist_m=int(dist*1000)

    tempo=int((dist/VEL_PE)*60)

    return dist_m,tempo


# =========================
# EXTRAIR PREÇO INTELIGENTE
# =========================

def extrair_preco(html):

    valores=re.findall(r"\d[\d\.\s]{4,}",html)

    numeros=[]

    for v in valores:

        try:

            n=int(v.replace(".","").replace(" ",""))

            numeros.append(n)

        except:

            pass

    numeros=sorted(numeros,reverse=True)

    for valor in numeros:

        if valor<20000:
            continue

        if valor>2000000:
            continue

        return valor

    return None


# =========================
# SCRAPE IMOVIRTUAL
# =========================

def imovirtual():

    print("A analisar: imovirtual")

    links=[]

    url="https://www.imovirtual.com/comprar/apartamento/braga/"

    try:

        r=requests.get(url,headers=HEADERS)

        soup=BeautifulSoup(r.text,"html.parser")

        for a in soup.select("article a"):

            link=a.get("href")

            if link and "ID" in link:

                links.append(link)

    except:

        pass

    return links


# =========================
# DUCKDUCKGO SEARCH
# =========================

def duck():

    print("A analisar: duckduckgo")

    queries=[

    "site:idealista.pt apartamento braga venda",
    "site:supercasa.pt apartamento braga",
    "site:casa.sapo.pt apartamento braga",
    "site:olx.pt apartamento braga"

    ]

    links=[]

    for q in queries:

        url="https://duckduckgo.com/html/?q="+q.replace(" ","+")

        try:

            r=requests.get(url,headers=HEADERS)

            soup=BeautifulSoup(r.text,"html.parser")

            for a in soup.select("a"):

                link=a.get("href")

                if not link:
                    continue

                if "http" not in link:
                    continue

                if "duckduckgo" in link:
                    continue

                if "braga" not in link.lower():
                    continue

                links.append(link)

        except:

            pass

    return links


# =========================
# RECOLHER LINKS
# =========================

links=[]

links+=imovirtual()

links+=duck()

links=list(set(links))

print("Links encontrados:",len(links))


# =========================
# ANALISAR LINKS
# =========================

total=0

for link in links:

    if link in historico:
        continue

    try:

        r=requests.get(link,headers=HEADERS,timeout=10)

        preco=extrair_preco(r.text)

        if preco:

            if preco>PRECO_MAX:
                continue

        else:

            preco="Preço não detectado"

        dist_m,tempo=distancia()

        msg=f"""
🏠 IMÓVEL DETECTADO

Preço: {preco}

Distância universidade: {dist_m} m
Tempo a pé: {tempo} min

{link}
"""

        telegram(msg)

        historico.append(link)

        total+=1

    except:

        pass


# =========================
# GUARDAR HISTORICO
# =========================

with open(HISTORICO_FILE,"w") as f:

    json.dump(historico,f)


telegram(f"""
📊 RELATÓRIO AGENTE BRAGA

Links encontrados: {len(links)}
Imóveis enviados: {total}

Hora: {datetime.now()}
""")

print("Fim execução")
