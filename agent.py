import requests
from bs4 import BeautifulSoup
import json
import os
import re
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
]

HEADERS = {
"User-Agent":
"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

HISTORICO_FILE = "historico.json"

TIPOLOGIAS = ["t0","t1","t2"]

ZONAS_UNIVERSIDADE = [
"gualtar",
"universidade",
"campus",
"são vítor",
"sao vitor",
"braga"
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
"particular",
"venda urgente"
]

# preço médio aproximado €/m2 braga
PRECO_MEDIO_M2 = 2000

# ============================
# TELEGRAM
# ============================

def enviar_telegram(msg):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    try:
        requests.post(url,data=data,timeout=10)
    except:
        pass

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

historico = historico[-5000:]

# ============================
# FUNÇÕES
# ============================

def extrair_preco(texto):

    numeros = re.findall(r'\d+', texto.replace(".",""))

    if numeros:
        try:
            return int(numeros[0])
        except:
            return 0

    return 0


def extrair_area(texto):

    match = re.search(r'(\d+)\s*m', texto.lower())

    if match:
        try:
            return int(match.group(1))
        except:
            return 0

    return 0

# ============================
# INICIO
# ============================

print("AGENTE IMOBILIARIO BRAGA V3")

enviar_telegram("🤖 Agente Braga V3 iniciado")

total = 0
novos = []
oportunidades = 0

# ============================
# SCRAPING
# ============================

for url in URLS:

    try:

        print("A analisar:",url)

        response = requests.get(url,headers=HEADERS,timeout=20)

        if response.status_code != 200:
            print("Erro acesso:",url)
            continue

        soup = BeautifulSoup(response.text,"html.parser")

        anuncios = soup.select("article, .item")

        print("Anuncios encontrados:",len(anuncios))

        for anuncio in anuncios[:120]:

            link_elem = anuncio.select_one("a")

            if not link_elem:
                continue

            link = link_elem.get("href")

            if not link:
                continue

            link = urljoin(url,link)

            titulo = link_elem.text.strip()

            if not titulo:
                titulo = "Apartamento Braga"

            texto = titulo.lower()

            # ============================
            # FILTRO TIPOLOGIA
            # ============================

            if not any(t in texto for t in TIPOLOGIAS):
                continue

            # ============================
            # FILTRO ZONA
            # ============================

            if not any(z in texto for z in ZONAS_UNIVERSIDADE):
                continue

            # ============================
            # PREÇO
            # ============================

            preco = extrair_preco(anuncio.text)

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

            # ============================
            # AREA
            # ============================

            area = extrair_area(anuncio.text)

            preco_m2 = 0

            if area > 0 and preco > 0:
                preco_m2 = preco / area

            # ============================
            # YIELD ESTUDANTES
            # ============================

            renda_estimada = 450

            yield_estimada = 0

            if preco > 0:
                yield_estimada = (renda_estimada * 12) / preco * 100

            # ============================
            # DETECÇÃO DESCONTO
            # ============================

            desconto = ""

            if preco_m2 > 0 and preco_m2 < PRECO_MEDIO_M2 * 0.6:
                desconto = "🔥 POSSÍVEL 40% ABAIXO DO MERCADO"

            # ============================
            # MENSAGEM
            # ============================

            mensagem = f"""
🏠 NOVO IMÓVEL

{titulo}

💰 Preço: {preco}€

📐 Área: {area} m2
💶 €/m2: {round(preco_m2,1)}

📈 Yield estimada: {round(yield_estimada,1)}%

{desconto}

{link}
"""

            enviar_telegram(mensagem)

            # ============================
            # OPORTUNIDADE
            # ============================

            if any(p in texto for p in PALAVRAS_OPORTUNIDADE):

                oportunidades += 1

                alerta = f"""
🚨 OPORTUNIDADE DETECTADA

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
💰 NEGÓCIO ANTES DO MERCADO

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
📊 RELATÓRIO AGENTE BRAGA V3

Analisados: {total}

Novos encontrados: {len(novos)}

Oportunidades: {oportunidades}

Hora: {datetime.now()}
"""

enviar_telegram(mensagem)

print("Fim execução")
