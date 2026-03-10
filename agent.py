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

        requests.post(url,data={
        "chat_id":CHAT_ID,
        "text":msg
        },timeout=10)

    except:
        pass

# =========================
# CONFIG INVESTIMENTO
# =========================

PRECO_MAX=300000
RENDA_ESTUDANTE=450
PRECO_MEDIO_M2=2000

TIPOLOGIAS=["t0","t1","t2"]

ZONAS=[
"gualtar",
"universidade",
"campus",
"sao vitor",
"são vítor",
"braga"
]

PALAVRAS_OPORTUNIDADE=[
"remodelar",
"renovar",
"recuperar",
"obras",
"urgente",
"oportunidade"
]

PALAVRAS_PARTICULAR=[
"particular",
"sem imobiliaria",
"direto proprietario"
]

PALAVRAS_PREMERCADO=[
"heranca",
"banco",
"leilao"
]

# =========================
# SITES
# =========================

URLS=[
"https://www.imovirtual.com/comprar/apartamento/braga/",
"https://www.idealista.pt/comprar-casas/braga/"
]

HEADERS={
"User-Agent":
"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
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
# FUNÇÕES
# =========================

def extrair_preco(texto):

    texto=texto.replace(".","")

    numeros=re.findall(r"\d{4,6}",texto)

    if numeros:

        try:
            return int(numeros[0])
        except:
            return 0

    return 0


def extrair_area(texto):

    m=re.search(r"(\d+)\s*m",texto.lower())

    if m:

        try:
            return int(m.group(1))
        except:
            return 0

    return 0


def yield_estimada(preco):

    if preco==0:
        return 0

    return (RENDA_ESTUDANTE*12)/preco*100


def calcular_score(preco_m2,yield_anual):

    score=0

    if preco_m2<PRECO_MEDIO_M2*0.9:
        score+=2

    if preco_m2<PRECO_MEDIO_M2*0.7:
        score+=2

    if yield_anual>5:
        score+=2

    if yield_anual>7:
        score+=2

    return score

# =========================
# START
# =========================

print("AGENTE IMOBILIARIO V7")

telegram("🤖 Scanner imobiliário Braga iniciado")

novos=[]
total=0

# =========================
# SCRAPING
# =========================

for url in URLS:

    try:

        print("A analisar:",url)

        r=requests.get(url,headers=HEADERS,timeout=20)

        if r.status_code!=200:

            print("Falhou:",url)
            continue

        soup=BeautifulSoup(r.text,"html.parser")

        anuncios=soup.select("article,.item,.offer-item")

        print("Encontrados:",len(anuncios))

        for a in anuncios[:150]:

            link_elem=a.select_one("a")

            if not link_elem:
                continue

            link=urljoin(url,link_elem.get("href"))

            titulo=link_elem.text.strip()

            texto=titulo.lower()

            if not any(t in texto for t in TIPOLOGIAS):
                continue

            if not any(z in texto for z in ZONAS):
                continue

            preco=extrair_preco(a.text)

            if preco>PRECO_MAX:
                continue

            if link in historico:
                continue

            historico.append(link)

            area=extrair_area(a.text)

            preco_m2=preco/area if area else 0

            yield_anual=yield_estimada(preco)

            score=calcular_score(preco_m2,yield_anual)

            mensagem=f"""
🏠 IMÓVEL DETECTADO

{titulo}

Preço: {preco}€

Área: {area} m2

€/m2: {round(preco_m2,1)}

Yield: {round(yield_anual,1)}%

Score investimento: {score}/8

{link}
"""

            telegram(mensagem)

            if any(p in texto for p in PALAVRAS_OPORTUNIDADE):

                telegram(f"""
🚨 OPORTUNIDADE

{titulo}

Preço: {preco}€

{link}
""")

            if any(p in texto for p in PALAVRAS_PARTICULAR):

                telegram(f"""
👤 VENDA PARTICULAR

{titulo}

Preço: {preco}€

{link}
""")

            if any(p in texto for p in PALAVRAS_PREMERCADO):

                telegram(f"""
💰 NEGÓCIO PRÉ-MERCADO

{titulo}

Preço: {preco}€

{link}
""")

            novos.append(link)

            total+=1

    except Exception as e:

        print("Erro:",e)

# =========================
# GUARDAR HISTORICO
# =========================

with open(HISTORICO_FILE,"w") as f:

    json.dump(historico,f)

# =========================
# RELATÓRIO
# =========================

telegram(f"""
📊 RELATÓRIO AGENTE V7

Analisados: {total}

Novos: {len(novos)}

Hora: {datetime.now()}
""")

print("Fim execução")
