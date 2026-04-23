import json
import os
from datetime import datetime, timezone

from scrapers.balaclava import get_balaclava_events
from scrapers.bona import get_bona_events
from scrapers.casa_francisca import get_casa_francisca_events
from scrapers.casa_rockambole import get_casa_rockambole_events
from scrapers.picles_shotgun import get_picles_events

STATIC_EVENTS = [
    {
        "name": "Zé Ibarra",
        "detail": "",
        "date": "Qui 23/04",
        "time": "19h",
        "iso": "2026-04-23",
        "venue": "Cine Joia",
        "v": "cine",
        "genre": "MPB",
        "price": "",
        "url": "https://www.songkick.com/concerts/43094750",
    },
    {
        "name": "Show part. Djonga",
        "detail": "Show autoral",
        "date": "Qui 23/04",
        "time": "21h",
        "iso": "2026-04-23",
        "venue": "SESC SP",
        "v": "sesc",
        "genre": "Hip-hop",
        "price": "",
        "url": "https://www.sescsp.org.br/?s=Djonga",
    },
    {
        "name": "Mari Jasca",
        "detail": "Show solo Disparada",
        "date": "Sex 24/04",
        "time": "20h",
        "iso": "2026-04-24",
        "venue": "SESC 14 Bis",
        "v": "sesc",
        "genre": "MPB",
        "price": "R$60",
        "url": "https://www.sescsp.org.br/?s=Mari+Jasca",
    },
    {
        "name": "Maglore",
        "detail": "",
        "date": "Sex 24/04",
        "time": "21h",
        "iso": "2026-04-24",
        "venue": "Cine Joia",
        "v": "cine",
        "genre": "Indie Rock",
        "price": "",
        "url": "https://shotgun.live/en/events/maglorenocinejoia",
    },
    {
        "name": "Show part. Djonga",
        "detail": "",
        "date": "Sex 24/04",
        "time": "21h",
        "iso": "2026-04-24",
        "venue": "SESC SP",
        "v": "sesc",
        "genre": "Hip-hop",
        "price": "",
        "url": "https://www.sescsp.org.br/?s=Djonga",
    },
    {
        "name": "Catto",
        "detail": "Caminhos Selvagens + tributo Gal",
        "date": "Sab 25/04",
        "time": "20h",
        "iso": "2026-04-25",
        "venue": "SESC 14 Bis",
        "v": "sesc",
        "genre": "MPB",
        "price": "R$60",
        "url": "https://www.sescsp.org.br/programacao/",
    },
    {
        "name": "Tributo Legião Urbana",
        "detail": "",
        "date": "Sab 25/04",
        "time": "21h",
        "iso": "2026-04-25",
        "venue": "SESC SP",
        "v": "sesc",
        "genre": "Rock",
        "price": "",
        "url": "https://www.sescsp.org.br/programacao/",
    },
    {
        "name": "Bastos e Leila Pinheiro",
        "detail": "",
        "date": "Sab 25/04",
        "time": "",
        "iso": "2026-04-25",
        "venue": "SESC SP",
        "v": "sesc",
        "genre": "MPB",
        "price": "",
        "url": "https://www.sescsp.org.br/programacao/",
    },
    {
        "name": "Sarah Leandro",
        "detail": "Forró de Bodocó",
        "date": "Dom 26/04",
        "time": "16h",
        "iso": "2026-04-26",
        "venue": "SESC Bom Retiro",
        "v": "sesc",
        "genre": "Forró",
        "price": "Grátis",
        "url": "https://www.sescsp.org.br/?s=Sarah+Leandro",
    },
    {
        "name": "The 5.6.7.8's",
        "detail": "",
        "date": "Dom 26/04",
        "time": "",
        "iso": "2026-04-26",
        "venue": "Cine Joia",
        "v": "cine",
        "genre": "Rock",
        "price": "",
        "url": "https://www.cinejoia.com.br/agenda/",
    },
    {
        "name": "Samba do Comerciário",
        "detail": "",
        "date": "Ter 28/04",
        "time": "",
        "iso": "2026-04-28",
        "venue": "SESC SP",
        "v": "sesc",
        "genre": "Samba",
        "price": "Grátis",
        "url": "https://www.sescsp.org.br/programacao/",
    },
    {
        "name": "Alma Djem",
        "detail": "Acústico – Reggae, MPB, Soul",
        "date": "Qui 30/04",
        "time": "21h",
        "iso": "2026-04-30",
        "venue": "SESC SP",
        "v": "sesc",
        "genre": "Reggae",
        "price": "R$60",
        "url": "https://www.sescsp.org.br/?s=Alma+Djem",
    },
    {
        "name": "Varukers",
        "detail": "",
        "date": "Sex 08/05",
        "time": "",
        "iso": "2026-05-08",
        "venue": "Cine Joia",
        "v": "cine",
        "genre": "Punk",
        "price": "",
        "url": "https://shotgun.live/pt-br/events/thevarukersnocinejoia",
    },
    {
        "name": "Leisure",
        "detail": "",
        "date": "Qua 13/05",
        "time": "21h",
        "iso": "2026-05-13",
        "venue": "Cine Joia",
        "v": "cine",
        "genre": "Funk/Soul",
        "price": "",
        "url": "https://www.songkick.com/concerts/43038806",
    },
    {
        "name": "Superchunk",
        "detail": "Balaclava apresenta",
        "date": "Dom 31/05",
        "time": "19h",
        "iso": "2026-05-31",
        "venue": "Cine Joia",
        "v": "cine",
        "genre": "Indie Rock",
        "price": "",
        "url": "https://ingresse.com/superchunk-sp",
    },
    {
        "name": "Shame",
        "detail": "Balaclava apresenta",
        "date": "Sab 20/06",
        "time": "19h",
        "iso": "2026-06-20",
        "venue": "Cine Joia",
        "v": "cine",
        "genre": "Post-punk",
        "price": "",
        "url": "https://ingresse.com/shame-sp",
    },
]


def sort_key(e: dict):
    iso = e.get('iso') or '9999-12-31'
    time = e.get('time') or '99h99'
    return (iso, time)


def dedupe(events: list) -> list:
    seen, out = set(), []
    for e in events:
        key = (e.get('name', '').lower().strip(), e.get('iso', ''), e.get('v', ''))
        if key not in seen:
            seen.add(key)
            out.append(e)
    return out


def run():
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    print(f'[run] hoje = {today}')

    scrapers = [
        ('balaclava',  get_balaclava_events),
        ('bona',       get_bona_events),
        ('francisca',  get_casa_francisca_events),
        ('rockambole', get_casa_rockambole_events),
        ('picles',     get_picles_events),
    ]

    dynamic: list = []
    for name, fn in scrapers:
        try:
            results = fn()
            print(f'[run] {name}: {len(results)} evento(s)')
            dynamic.extend(results)
        except Exception as ex:
            print(f'[run] {name} erro: {ex}')

    # Static events starting from today
    static_future = [e for e in STATIC_EVENTS if (e.get('iso') or '') >= today]

    all_events = dedupe(sorted(static_future + dynamic, key=sort_key))
    print(f'[run] total após dedupe: {len(all_events)} eventos')

    payload = {
        'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'events': all_events,
    }

    out_path = os.path.join(os.path.dirname(__file__), 'events.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f'[run] events.json gravado em {out_path}')


if __name__ == '__main__':
    run()
