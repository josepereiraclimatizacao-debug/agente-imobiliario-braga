import requests
from bs4 import BeautifulSoup
import json
import os
import re
import math
from datetime import datetime
from urllib.parse import urljoin

TOKEN="8748185653:AAG5nXSBrbay_34zVtd7dUJFblvDy7XsaNc"
CHAT_ID="8248415390"

def telegram(msg):

    try:

        url=f"https://api.telegram.org/bot{TOKEN}/sendMessage"

        requests.post(url,data={
        "chat_id":CHAT_ID,
        "text":msg
        },timeout=10)

    except:

        pass


# =========================
# CONFIG
# =========================

PRECO_MAX=200000
RENDA_ESTUDANTE=450
PRECO_MEDIO_M2=2000

TIPOLOGIAS=["t0","t1","t2","t3"]

# coordenadas universidade minho
UNI_LAT=41.561
UNI_LON=-8.397

# velocidade média a pé
VEL_PE=4.5


# =========================
# SITES
# =========================

URLS=[

"https://www.imovirtual.com/comprar/apartamento/braga/",
"https://www.idealista.pt/comprar-casas/braga/",
"https://casa.sapo.pt/comprar-apartamentos/braga/",
"https://supercasa.pt/comprar-casas/braga/",
"https://www.olx.pt/imoveis/apartamentos-casas-a-venda/braga/"

]

FACEBOOK_URL="https://www.facebook.com/marketplace/braga/search?query=apartamento"


HEADERS={
"User-Agent":"Mozilla/5.0"
}


# =========================
# HISTORICO
# =========================

HISTORICO_FILE="historico.json"

if os.path.exists(HISTORICO_FILE):

    with open(HISTORICO_FILE,"r") as f:

        historico=json.load(f)

else:

    historico=[]

historico=historico[-5000:]


# =========================
# PREÇO
# =========================

def extrair_preco(texto):

    precos=re.findall(r"\d[\d\. ]+\s?€",texto)

    for p in precos:

        if "/m" in p.lower():

            continue

        valor=p.replace("€","").replace(".","").replace(" ","")

        try:

            valor=int(valor)

            if valor>20000:

                return valor

        except:

            pass

    return 0


# =========================
# AREA
# =========================

def extrair_area(texto):

    m=re.search(r"(\d+)\s*m",texto.lower())

    if m:

        return int(m.group(1))

    return 0


# =========================
# DISTANCIA
# =========================

def distancia(lat,lon):

    R=6371000

    phi1=math.radians(lat)
    phi2=math.radians(UNI_LAT)

    dphi=math.radians(UNI_LAT-lat)
    dlambda=math.radians(UNI_LON-lon)

    a=(math.sin(dphi/2)**2 +
       math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2)

    c=2*math.atan2(math.sqrt(a),math.sqrt(1-a))

    return R*c


def tempo_pe(dist):

    return int((dist/1000)/VEL_PE*60)


# =========================
# SCORE
# =========================

def yield_estimada(preco):

    return (RENDA_ESTUDANTE*12)/preco*100


def calcular_score(preco_m2,yield_anual):

    score=0

    if preco_m2<PRECO_MEDIO_M2:

        score+=2

    if preco_m2<PRECO_MEDIO_M2*0.8:

        score+=3

    if yield_anual>5:

        score+=2

    if yield_anual>7:

        score+=3

    return score


# =========================
# START
# =========================

print("AGENTE IMOBILIARIO V13")

telegram("🤖 Scanner imobiliário Braga iniciado")

novos=[]
top=[]


# =========================
# SCRAPING PORTAIS
# =========================

for url in URLS:

    try:

        print("A analisar:",url)

        r=requests.get(url,headers=HEADERS,timeout=20)

        soup=BeautifulSoup(r.text,"html.parser")

        anuncios=soup.select("article,.item,.offer-item,.listing")

        for a in anuncios[:200]:

            link_elem=a.select_one("a")

            if not link_elem:

                continue

            link=urljoin(url,link_elem.get("href"))

            titulo=link_elem.text.strip()

            texto=(titulo+" "+a.text)

            preco=extrair_preco(texto)

            if preco==0 or preco>PRECO_MAX:

                continue

            if link in historico:

                continue

            historico.append(link)

            area=extrair_area(texto)

            preco_m2=preco/area if area else 0

            yield_anual=yield_estimada(preco)

            score=calcular_score(preco_m2,yield_anual)

            # estimativa distancia centro braga
            dist=2000
            tempo=tempo_pe(dist)

            mensagem=f"""
🏠 IMÓVEL DETECTADO

{titulo}

Preço: {preco} €

Área: {area} m²

€/m²: {round(preco_m2,1)}

Distância universidade: {int(dist)} m

Tempo a pé: {tempo} min

Yield: {round(yield_anual,2)} %

Score investimento: {score}/10

{link}
"""

            telegram(mensagem)

            novos.append(link)

            top.append((score,titulo,link))

    except Exception as e:

        print("Erro:",e)


# =========================
# FACEBOOK MARKETPLACE
# =========================

try:

    r=requests.get(FACEBOOK_URL,headers=HEADERS)

    soup=BeautifulSoup(r.text,"html.parser")

    posts=soup.select("a")

    for p in posts[:20]:

        titulo=p.text

        link="https://facebook.com"+p.get("href","")

        if "apartamento" in titulo.lower():

            telegram(f"""
📱 Facebook Marketplace

{titulo}

{link}
""")

except:

    pass


# =========================
# HISTORICO
# =========================

with open(HISTORICO_FILE,"w") as f:

    json.dump(historico,f)


# =========================
# TOP
# =========================

top.sort(reverse=True)

msg="🏆 TOP OPORTUNIDADES\n\n"

for i,(score,titulo,link) in enumerate(top[:10]):

    msg+=f"{i+1}. {titulo}\nScore {score}\n{link}\n\n"

telegram(msg)


telegram(f"""
📊 RELATÓRIO

Novos imóveis: {len(novos)}

Hora: {datetime.now()}
""")
