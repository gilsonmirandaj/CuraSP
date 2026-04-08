from __future__ import annotations
import requests
from bs4 import BeautifulSoup
from fallback.static_events import FALLBACK_BY_SOURCE
from .common import normalize_event, infer_genre, url_abs

URL = 'https://acasadefrancisca.art.br/programacao'
ALT_URL = 'https://casadefrancisca.art.br/novo/programacao'


def fetch_events():
    try:
        res = requests.get(URL, timeout=20, headers={'User-Agent': 'Mozilla/5.0'})
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        cards = soup.select('article')
        events = []
        for card in cards:
            title_tag = card.find(['h1','h2','h3','h4'])
            title = title_tag.get_text(' ', strip=True) if title_tag else ''
            link_tag = card.find('a', href=True)
            link = url_abs(URL, link_tag['href']) if link_tag else ALT_URL
            text = ' '.join(card.stripped_strings)
            if title:
                events.append(normalize_event(
                    name=title[:160], detail='', date='', time='', iso='', venue='Casa de Francisca',
                    v='francisca', genre=infer_genre(text), price='', url=link
                ))
        if events:
            return events
    except Exception:
        pass
    return FALLBACK_BY_SOURCE.get('francisca', [])
