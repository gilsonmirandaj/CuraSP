import requests
from bs4 import BeautifulSoup

URL = "https://acasadefrancisca.art.br/programacao"

def get_casa_francisca_events():
    events = []

    res = requests.get(URL)
    soup = BeautifulSoup(res.text, "html.parser")

    cards = soup.select("article")

    for card in cards:
        try:
            title = card.get_text(strip=True)

            link_tag = card.find("a")
            link = link_tag["href"] if link_tag else URL

            events.append({
                "casa": "Casa de Francisca",
                "titulo": title,
                "link": link
            })
        except:
            pass

    return events
