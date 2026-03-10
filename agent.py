import requests
from bs4 import BeautifulSoup
import json
import os
import math
import re
from urllib.parse import urljoin
from datetime import datetime

# ===============================
# TELEGRAM
# ===============================

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


# ===============================
# CONFIG
# ===============================

PRECO_MAX = 150000

UNI_LAT = 41.561
UNI_LON = -8.397

VEL_PE = 4.5

HISTORICO_FILE = "historico.json"


# ===============================
# SITES
# ===============================

SITES = {

"imovirtual":"https://www.imovirtual.com/comprar/apartamento/braga/",
"idealista":"https://www.idealista.pt/comprar-casas/braga/",
"supercasa":"https://supercasa.pt/comprar-casas/braga/",
"casa_sapo":"https://casa.sapo.pt/comprar-apartamentos/braga/",
"olx":"https://www.olx.pt/imoveis/apartamentos-casas-a-venda/braga/",
"remax":"https://www.remax.pt/comprar/apartamentos/braga",
"era":"https://www.era.pt/imoveis/comprar/braga",
"chavenova":"https://www.chavenova.pt/imoveis/braga",
"casayes":"https://www.casayes.pt/imoveis/braga"

}

HEADERS = {
"User-Agent":"Mozilla/5.0",
"Accept-Language":"pt-PT,pt;q=0.9"
}


# ===============================
# HISTÓRICO
# ===============================

if os.path.exists(HISTORICO_FILE):

    try:

        with open(HISTORICO_FILE,"r") as f:
            historico=json.load(f)

    except:
        historico=[]

else:

    historico=[]

historico=historico[-6000:]


# ===============================
# DISTÂNCIA
# ===============================

def distancia(lat,lon):

    R=6371

    dlat=math.radians(lat-UNI_LAT)
    dlon=math.radians(lon-UNI_LON)

    a=math.sin(dlat/2)**2 + math.cos(math.radians(UNI_LAT))*math.cos(math.radians(lat))*math.sin(dlon/2)**2

    c=2*math.atan2(math.sqrt(a),math.sqrt(1-a))

    return R*c


# ===============================
# EXTRAIR PREÇO
# ===============================

def extrair_preco(texto):

    texto=texto.replace("\xa0"," ")

    matches=re.findall(r"(\d[\d\s\.]{3,})\s*€",texto)

    for m in matches:

        valor=int(m.replace(" ","").replace(".",""))

        if valor<20000:
            continue

        if valor>2000000:
            continue

        return valor

    return None


# ===============================
# EXTRAIR ANÚNCIOS
# ===============================

def extrair_anuncios(site,soup):

    if site=="imovirtual":
        return soup.select("article")

    if site=="idealista":
        return soup.select(".item")

    if site=="supercasa":
        return soup.select(".property")

    if site=="casa_sapo":
        return soup.select(".searchResultItem")

    if site=="olx":
        return soup.select("article")

    return soup.select("article,div")


# ===============================
# START
# ===============================

print("AGENTE IMOBILIARIO BRAGA V21")

total=0

for nome,url in SITES.items():

    print("A analisar:",nome)

    try:

        r=requests.get(url,headers=HEADERS,timeout=20)

        if r.status_code!=200:
            continue

        soup=BeautifulSoup(r.text,"html.parser")

        anuncios=extrair_anuncios(nome,soup)

        print("Anuncios encontrados:",len(anuncios))

        for anuncio in anuncios:

            link_elem=anuncio.select_one("a")

            if not link_elem:
                continue

            link=link_elem.get("href")

            if not link:
                continue

            link=urljoin(url,link)

            if link in historico:
                continue

            texto=anuncio.get_text(" ",strip=True)

            preco=extrair_preco(texto)

            if not preco:
                continue

            lat=41.55
            lon=-8.42

            dist=distancia(lat,lon)

            dist_m=int(dist*1000)

            tempo=int((dist/VEL_PE)*60)

            if preco <= PRECO_MAX:
                status="💰 ABAIXO DO PREÇO LIMITE"
            else:
                status="⚠ ACIMA DO PREÇO LIMITE"

            mensagem=f"""
🏠 IMÓVEL DETECTADO

Preço: {preco} €

{status}

Distância universidade: {dist_m} m
Tempo a pé: {tempo} min

Fonte: {nome}

{link}
"""

            telegram(mensagem)

            historico.append(link)

            total+=1

    except Exception as e:

        print("Erro:",nome)


# ===============================
# GUARDAR HISTÓRICO
# ===============================

try:

    with open(HISTORICO_FILE,"w") as f:
        json.dump(historico,f)

except:
    pass


# ===============================
# RELATÓRIO
# ===============================

telegram(f"""
📊 RELATÓRIO AGENTE BRAGA

Imóveis encontrados: {total}

Hora: {datetime.now()}
""")

print("Fim execução")
