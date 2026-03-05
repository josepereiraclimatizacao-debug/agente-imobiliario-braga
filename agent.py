import requests
from bs4 import BeautifulSoup

url = "https://www.idealista.pt/comprar-casas/braga/"

page = requests.get(url)

soup = BeautifulSoup(page.text, "html.parser")

anuncios = soup.find_all("article")

for anuncio in anuncios[:10]:
    texto = anuncio.get_text()
    print(texto)
