import requests
from bs4 import BeautifulSoup

url = "https://www.idealista.pt/comprar-casas/braga/"

headers = {"User-Agent": "Mozilla/5.0"}

page = requests.get(url, headers=headers)

soup = BeautifulSoup(page.text, "html.parser")

ads = soup.find_all("article")

for ad in ads[:20]:

    text = ad.get_text(" ", strip=True)

    price = None
    size = None

    for part in text.split():

        if "€" in part:
            try:
                price = int(part.replace("€", "").replace(".", ""))
            except:
                pass

        if "m²" in part:
            try:
                size = int(part.replace("m²", ""))
            except:
                pass

    if price and size:

        price_m2 = price / size

        if price_m2 < 1200:
            print("🔥 OPORTUNIDADE")

        print(price, "€", size, "m2 →", round(price_m2, 1), "€/m2")
