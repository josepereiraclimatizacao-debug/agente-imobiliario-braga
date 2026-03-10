import requests
from bs4 import BeautifulSoup
import json
import os
import re
import math
from datetime import datetime
from urllib.parse import urljoin

# =========================
# TELEGRAM
# =========================

TOKEN = "8748185653:AAG5nXSBrbay_34zVtd7dUJFblvDy7XsaNc"
CHAT_ID = "8248415390"

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
# CONFIG INVESTIMENTO
# =========================

PRECO_MAX = 300000
PRECO_MEDIO_M2 = 2000
RENDA_ESTUDANTE = 450

JURO = 0.04
ANOS = 30

TIPOLOGIAS = ["t0","t1","t2","t3","apartamento"]

# coordenadas Universidade Minho Gualtar
UNI_LAT = 41.561
UNI_LON = -8.397

# =========================
# SITES
# =========================

URLS = [
"https://www.imovirtual.com/comprar/apartamento/braga/",
"https://www.idealista.pt/comprar-casas/braga/"
]

HEADERS = {
"User-Agent": "Mozilla/5.0"
}

# =========================
# HISTORICO
# =========================

HISTORICO_FILE = "historico.json"

if os.path.exists(HISTORICO_FILE):

    with open(HISTORICO_FILE,"r") as f:
        historico=json.load(f)

else:
    historico=[]

historico = historico[-5000:]

# =========================
# FUNÇÕES
# =========================

def extrair_preco(anuncio):

    seletores = [
        ".price",
        ".item-price",
        ".offer-price",
        ".listing-price"
    ]

    for s in seletores:

        p = anuncio.select_one(s)

        if p:

            texto = p.text

            texto = texto.replace("€","").replace(".","").strip()

            numeros = re.findall(r"\d+",texto)

            if numeros:

                return int(numeros[0])

    texto = anuncio.text.replace(".","")

    numeros = re.findall(r"\d{4,7}",texto)

    if numeros:

        return int(numeros[0])

    return 0


def extrair_area(texto):

    m = re.search(r"(\d+)\s*m",texto.lower())

    if m:

        return int(m.group(1))

    return 0


def yield_estimada(preco):

    if preco == 0:
        return 0

    return (RENDA_ESTUDANTE*12)/preco*100


def calcular_credito(preco):

    entrada = preco*0.1
    emprestimo = preco-entrada

    meses = ANOS*12
    taxa = JURO/12

    prestacao = emprestimo*taxa/(1-(1+taxa)**-meses)

    return round(prestacao)


def calcular_score(preco_m2,yield_anual):

    score = 0

    if preco_m2 < PRECO_MEDIO_M2:
        score += 2

    if preco_m2 < PRECO_MEDIO_M2*0.8:
        score += 3

    if yield_anual > 5:
        score += 2

    if yield_anual > 7:
        score += 3

    return score


# distância aproximada até universidade
def distancia_universidade():

    # média centro Braga → universidade
    return 2500

# =========================
# START
# =========================

print("AGENTE IMOBILIARIO V9.1")

telegram("🤖 Scanner imobiliário Braga iniciado")

novos=[]
top=[]

# =========================
# SCRAPING
# =========================

for url in URLS:

    try:

        r=requests.get(url,headers=HEADERS,timeout=20)

        if r.status_code!=200:
            continue

        soup=BeautifulSoup(r.text,"html.parser")

        anuncios=soup.select("article,.item,.offer-item")

        for a in anuncios[:200]:

            link_elem=a.select_one("a")

            if not link_elem:
                continue

            link=urljoin(url,link_elem.get("href"))

            titulo=link_elem.text.strip()

            texto=(titulo+" "+a.text).lower()

            if not any(t in texto for t in TIPOLOGIAS):
                continue

            preco=extrair_preco(a)

            if preco>PRECO_MAX:
                continue

            if link in historico:
                continue

            historico.append(link)

            area=extrair_area(a.text)

            preco_m2=preco/area if area else 0

            yield_anual=yield_estimada(preco)

            prestacao=calcular_credito(preco)

            cashflow=RENDA_ESTUDANTE-prestacao

            score=calcular_score(preco_m2,yield_anual)

            distancia=distancia_universidade()

            mensagem=f"""
🏠 IMÓVEL DETECTADO

{titulo}

Preço: {preco}€

Área: {area} m²

€/m²: {round(preco_m2,1)}

Distância Universidade: {distancia} m

Yield: {round(yield_anual,1)}%

Prestação crédito: {prestacao}€

Cashflow: {cashflow}€

Score investimento: {score}/10

{link}
"""

            telegram(mensagem)

            top.append((score,titulo,link))

            novos.append(link)

    except Exception as e:

        print("Erro:",e)

# =========================
# GUARDAR HISTORICO
# =========================

with open(HISTORICO_FILE,"w") as f:

    json.dump(historico,f)

# =========================
# TOP INVESTIMENTOS
# =========================

top.sort(reverse=True)

top10=top[:10]

if top10:

    msg="🏆 TOP OPORTUNIDADES DO DIA\n\n"

    i=1

    for score,titulo,link in top10:

        msg+=f"{i}. {titulo}\nScore {score}\n{link}\n\n"

        i+=1

    telegram(msg)

# =========================
# RELATÓRIO
# =========================

telegram(f"""
📊 RELATÓRIO AGENTE

Novos imóveis: {len(novos)}

Hora: {datetime.now()}
""")

print("Fim execução")
