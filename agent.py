import requests
from bs4 import BeautifulSoup
import json
import os
import re
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
        requests.post(url,data={"chat_id":CHAT_ID,"text":msg},timeout=10)
    except:
        pass

# =========================
# CONFIG INVESTIMENTO
# =========================

PRECO_MAX = 150000
RENDA_ESTUDANTE = 450
PRECO_MEDIO_M2 = 2000

TIPOLOGIAS = ["t0","t1","t2","t3"]

# =========================
# SITES PESQUISA
# =========================

URLS = [

"https://www.imovirtual.com/comprar/apartamento/braga/",
"https://www.idealista.pt/comprar-casas/braga/",
"https://supercasa.pt/comprar-casas/braga/",
"https://casa.sapo.pt/comprar-apartamentos/braga/",
"https://www.olx.pt/imoveis/apartamentos-casas-a-venda/braga/"

]

HEADERS = {
"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
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

historico = historico[-5000:]

# =========================
# EXTRAIR PREÇO CORRETO
# =========================

def extrair_preco(anuncio):

    seletores = [
    ".price",
    ".item-price",
    ".offer-price",
    ".listing-price",
    ".price-tag",
    "[class*=price]"
    ]

    for s in seletores:

        p = anuncio.select_one(s)

        if p:

            texto=p.text

            texto=texto.replace("€","").replace(".","")

            numeros=re.findall(r"\d+",texto)

            if numeros:

                preco=int(numeros[0])

                if preco>10000 and preco<1000000:

                    return preco

    # fallback geral
    texto=anuncio.text.replace(".","")

    numeros=re.findall(r"\d{5,7}",texto)

    if numeros:

        preco=int(numeros[0])

        if preco>10000:
            return preco

    return 0


# =========================
# AREA
# =========================

def extrair_area(texto):

    m=re.search(r"(\d+)\s*m",texto.lower())

    if m:

        try:
            return int(m.group(1))
        except:
            return 0

    return 0


# =========================
# YIELD
# =========================

def yield_estimada(preco):

    if preco==0:
        return 0

    return round((RENDA_ESTUDANTE*12)/preco*100,2)


# =========================
# SCORE INVESTIMENTO
# =========================

def calcular_score(preco_m2,yield_anual):

    score=0

    if preco_m2 < PRECO_MEDIO_M2:
        score += 2

    if preco_m2 < PRECO_MEDIO_M2*0.8:
        score += 3

    if yield_anual > 5:
        score += 2

    if yield_anual > 7:
        score += 3

    return score


# =========================
# START
# =========================

print("AGENTE IMOBILIARIO V11")

telegram("🤖 Scanner imobiliário Braga iniciado")

novos=[]
top=[]

# =========================
# SCRAPING
# =========================

for url in URLS:

    try:

        print("A analisar:",url)

        r=requests.get(url,headers=HEADERS,timeout=20)

        if r.status_code!=200:

            print("Erro acesso:",url)

            continue

        soup=BeautifulSoup(r.text,"html.parser")

        anuncios=soup.select("article,.item,.offer-item,.listing")

        print("Anuncios encontrados:",len(anuncios))

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

            if preco==0 or preco>PRECO_MAX:
                continue

            if link in historico:
                continue

            historico.append(link)

            area=extrair_area(a.text)

            preco_m2 = preco/area if area else 0

            yield_anual=yield_estimada(preco)

            score=calcular_score(preco_m2,yield_anual)

            mensagem=f"""
🏠 IMÓVEL DETECTADO

{titulo}

Preço anúncio: {preco}€

Área: {area} m²

€/m²: {round(preco_m2,1)}

Yield estimada: {yield_anual}%

Score investimento: {score}/10

{link}
"""

            telegram(mensagem)

            novos.append(link)

            top.append((score,titulo,link))

    except Exception as e:

        print("Erro scraping:",e)

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
# RELATORIO
# =========================

telegram(f"""
📊 RELATÓRIO AGENTE

Novos imóveis encontrados: {len(novos)}

Hora: {datetime.now()}
""")

print("Fim execução")
