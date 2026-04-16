from scrapers.picles_shotgun import get_picles_events
from scrapers.casa_francisca import get_casa_francisca_events
from scrapers.casa_rockambole import get_casa_rockambole_events
from scrapers.balaclava import get_balaclava_events
from scrapers.bona import get_bona_events
import json
from datetime import datetime, timezone

STATIC_EVENTS = [
  {
    "name": "No Hope Fest",
    "detail": "Experimental / noise - Test, Deafkids, Sturle Dagsland e mais",
    "date": "Sex 03/4",
    "time": "18h",
    "iso": "2026-04-03",
    "venue": "Casa Rockambole",
    "v": "rockambole",
    "genre": "Experimental",
    "price": "R$30-60",
    "url": "https://meaple.com.br/rockambole/no-hope-fest"
  },
  {
    "name": "Mac DeMarco",
    "detail": "",
    "date": "Sab 04/4",
    "time": "21h",
    "iso": "2026-04-04",
    "venue": "Audio SP",
    "v": "balaclava",
    "genre": "Indie/Pop",
    "price": "",
    "url": "https://www.ingresse.com/macdemarco-sp2/"
  },
  {
    "name": "Mac DeMarco",
    "detail": "Data extra",
    "date": "Dom 05/4",
    "time": "19h",
    "iso": "2026-04-05",
    "venue": "Audio SP",
    "v": "balaclava",
    "genre": "Indie/Pop",
    "price": "",
    "url": "https://www.ingresse.com/macdemarco-sp2/"
  },
  {
    "name": "Jesse Harris",
    "detail": "If You Believed In Me",
    "date": "Ter 07/4",
    "time": "20h",
    "iso": "2026-04-07",
    "venue": "Bona Casa de Musica",
    "v": "bona",
    "genre": "Folk/Jazz",
    "price": "R$60",
    "url": "https://www.eventim.com.br/artist/bona-casa-musica/jesse-harris/"
  },
  {
    "name": "Public Image Ltd.",
    "detail": "Com The Gulps",
    "date": "Qua 08/4",
    "time": "19h",
    "iso": "2026-04-08",
    "venue": "Cine Joia",
    "v": "cine",
    "genre": "Post-punk",
    "price": "",
    "url": "https://fastix.com.br/events/public-image-ltd-em-sao-paulo"
  },
  {
    "name": "Caique Tostes",
    "detail": "Performance poetica e saude mental",
    "date": "Qui 09/4",
    "time": "19h",
    "iso": "2026-04-09",
    "venue": "SESC Ipiranga",
    "v": "sesc",
    "genre": "MPB",
    "price": "Gratis",
    "url": "https://www.sescsp.org.br/programacao/"
  },
  {
    "name": "Negritude Jr.",
    "detail": "Show",
    "date": "Sex 10/4",
    "time": "20h30",
    "iso": "2026-04-10",
    "venue": "SESC SP",
    "v": "sesc",
    "genre": "Pagode",
    "price": "",
    "url": "https://www.sescsp.org.br/programacao/"
  },
  {
    "name": "Negritude Jr.",
    "detail": "Show",
    "date": "Sab 11/4",
    "time": "20h30",
    "iso": "2026-04-11",
    "venue": "SESC SP",
    "v": "sesc",
    "genre": "Pagode",
    "price": "",
    "url": "https://www.sescsp.org.br/programacao/"
  },
  {
    "name": "Oriente",
    "detail": "",
    "date": "Sab 11/4",
    "time": "20h",
    "iso": "2026-04-11",
    "venue": "Cine Joia",
    "v": "cine",
    "genre": "Hip-hop",
    "price": "",
    "url": "https://www.songkick.com/concerts/43045390"
  },
  {
    "name": "Mirim e Victor Xama",
    "detail": "",
    "date": "Dom 12/4",
    "time": "",
    "iso": "2026-04-12",
    "venue": "SESC SP",
    "v": "sesc",
    "genre": "Rap",
    "price": "",
    "url": "https://www.sescsp.org.br/programacao/"
  },
  {
    "name": "Anna Tsuchiya",
    "detail": "",
    "date": "Ter 14/4",
    "time": "",
    "iso": "2026-04-14",
    "venue": "Cine Joia",
    "v": "cine",
    "genre": "Rock/Pop",
    "price": "",
    "url": "https://www.songkick.com/concerts/43013462"
  },
  {
    "name": "Mad Professor",
    "detail": "Com Liquidus Ambiento",
    "date": "Qui 16/4",
    "time": "19h",
    "iso": "2026-04-16",
    "venue": "Cine Joia",
    "v": "cine",
    "genre": "Reggae",
    "price": "",
    "url": "https://www.songkick.com/concerts/43083456"
  },
  {
    "name": "Cachorro Grande",
    "detail": "",
    "date": "Sex 17/4",
    "time": "20h",
    "iso": "2026-04-17",
    "venue": "Cine Joia",
    "v": "cine",
    "genre": "Rock",
    "price": "",
    "url": "https://www.songkick.com/concerts/43045390"
  },
  {
    "name": "DJ Nelson Maca",
    "detail": "Samba rock, MPB, soul",
    "date": "Sab 18/4",
    "time": "15h",
    "iso": "2026-04-18",
    "venue": "Nazare Paulista",
    "v": "sesc",
    "genre": "Samba",
    "price": "Gratis",
    "url": "https://www.sescsp.org.br/programacao/"
  },
  {
    "name": "Midnight Til Morning",
    "detail": "",
    "date": "Sab 18/4",
    "time": "19h",
    "iso": "2026-04-18",
    "venue": "Cine Joia",
    "v": "cine",
    "genre": "Pop",
    "price": "",
    "url": "https://www.songkick.com/concerts/42936819"
  },
  {
    "name": "Comadres",
    "detail": "Forro pe de serra, baiao",
    "date": "Dom 19/4",
    "time": "15h",
    "iso": "2026-04-19",
    "venue": "Bom Jesus dos Perdoes",
    "v": "sesc",
    "genre": "Forro",
    "price": "Gratis",
    "url": "https://www.sescsp.org.br/programacao/"
  },
  {
    "name": "Show part. Djonga",
    "detail": "Show autoral",
    "date": "Qui 23/4",
    "time": "21h",
    "iso": "2026-04-23",
    "venue": "SESC SP",
    "v": "sesc",
    "genre": "Hip-hop",
    "price": "",
    "url": "https://www.sescsp.org.br/?s=Djonga"
  },
  {
    "name": "Ze Ibarra",
    "detail": "",
    "date": "Qui 23/4",
    "time": "19h",
    "iso": "2026-04-23",
    "venue": "Cine Joia",
    "v": "cine",
    "genre": "MPB",
    "price": "",
    "url": "https://www.songkick.com/concerts/43094750"
  },
  {
    "name": "Show part. Djonga",
    "detail": "",
    "date": "Sex 24/4",
    "time": "21h",
    "iso": "2026-04-24",
    "venue": "SESC SP",
    "v": "sesc",
    "genre": "Hip-hop",
    "price": "",
    "url": "https://www.sescsp.org.br/?s=Djonga"
  },
  {
    "name": "Mari Jasca",
    "detail": "Show solo Disparada",
    "date": "Sex 24/4",
    "time": "20h",
    "iso": "2026-04-24",
    "venue": "SESC 14 Bis",
    "v": "sesc",
    "genre": "MPB",
    "price": "R$60",
    "url": "https://www.sescsp.org.br/?s=Mari+Jasca"
  },
  {
    "name": "Maglore",
    "detail": "",
    "date": "Sex 24/4",
    "time": "21h",
    "iso": "2026-04-24",
    "venue": "Cine Joia",
    "v": "cine",
    "genre": "Indie Rock",
    "price": "",
    "url": "https://shotgun.live/en/events/maglorenocinejoia"
  },
  {
    "name": "Catto",
    "detail": "Caminhos Selvagens + tributo Gal",
    "date": "Sab 25/4",
    "time": "20h",
    "iso": "2026-04-25",
    "venue": "SESC 14 Bis",
    "v": "sesc",
    "genre": "MPB",
    "price": "R$60",
    "url": "https://www.sescsp.org.br/programacao/"
  },
  {
    "name": "Tributo Legiao Urbana",
    "detail": "",
    "date": "Sab 25/4",
    "time": "21h",
    "iso": "2026-04-25",
    "venue": "SESC SP",
    "v": "sesc",
    "genre": "Rock",
    "price": "",
    "url": "https://www.sescsp.org.br/programacao/"
  },
  {
    "name": "Bastos e Leila Pinheiro",
    "detail": "",
    "date": "Sab 25/4",
    "time": "",
    "iso": "2026-04-25",
    "venue": "SESC SP",
    "v": "sesc",
    "genre": "MPB",
    "price": "",
    "url": "https://www.sescsp.org.br/programacao/"
  },
  {
    "name": "Sarah Leandro",
    "detail": "Forro de Bodoco",
    "date": "Dom 26/4",
    "time": "16h",
    "iso": "2026-04-26",
    "venue": "SESC Bom Retiro",
    "v": "sesc",
    "genre": "Forro",
    "price": "Gratis",
    "url": "https://www.sescsp.org.br/?s=Sarah+Leandro"
  },
  {
    "name": "The 5.6.7.8s",
    "detail": "",
    "date": "Sab 26/4",
    "time": "",
    "iso": "2026-04-26",
    "venue": "Cine Joia",
    "v": "cine",
    "genre": "Rock",
    "price": "",
    "url": "https://www.cinejoia.com.br/agenda/"
  },
  {
    "name": "Samba do Comerciario",
    "detail": "",
    "date": "Ter 28/4",
    "time": "",
    "iso": "2026-04-28",
    "venue": "SESC SP",
    "v": "sesc",
    "genre": "Samba",
    "price": "Gratis",
    "url": "https://www.sescsp.org.br/programacao/"
  },
  {
    "name": "Alma Djem",
    "detail": "Acustico - Reggae, MPB, Soul",
    "date": "Qui 30/4",
    "time": "21h",
    "iso": "2026-04-30",
    "venue": "SESC SP",
    "v": "sesc",
    "genre": "Reggae",
    "price": "R$60",
    "url": "https://www.sescsp.org.br/?s=Alma+Djem"
  },
  {
    "name": "Varukers",
    "detail": "",
    "date": "Sex 08/5",
    "time": "",
    "iso": "2026-05-08",
    "venue": "Cine Joia",
    "v": "cine",
    "genre": "Punk",
    "price": "",
    "url": "https://shotgun.live/pt-br/events/thevarukersnocinejoia"
  },
  {
    "name": "Leisure",
    "detail": "",
    "date": "Qua 13/5",
    "time": "21h",
    "iso": "2026-05-13",
    "venue": "Cine Joia",
    "v": "cine",
    "genre": "Funk/Soul",
    "price": "",
    "url": "https://www.songkick.com/concerts/43038806"
  },
  {
    "name": "Superchunk",
    "detail": "Balaclava apresenta",
    "date": "Dom 31/5",
    "time": "19h",
    "iso": "2026-05-31",
    "venue": "Cine Joia",
    "v": "cine",
    "genre": "Indie Rock",
    "price": "",
    "url": "https://ingresse.com/superchunk-sp"
  },
  {
    "name": "Shame",
    "detail": "Balaclava apresenta",
    "date": "Sab 20/6",
    "time": "19h",
    "iso": "2026-06-20",
    "venue": "Cine Joia",
    "v": "cine",
    "genre": "Post-punk",
    "price": "",
    "url": "https://ingresse.com/shame-sp"
  }
]


def dedupe(events):
    seen = set()
    out = []
    for e in events:
        key = f"{(e.get('name') or '').strip().lower()}|{e.get('iso') or ''}|{e.get('v') or ''}"
        if key in seen:
            continue
        seen.add(key)
        out.append(e)
    return out


def sort_key(e):
    return (e.get('iso') or '9999-99-99', e.get('time') or '99:99', e.get('name') or '')


def run():
    events = []
    events += STATIC_EVENTS
    try:
        events += get_picles_events()
    except Exception as ex:
        print(f'Falha ao coletar Picles: {ex}')
    try:
        events += get_casa_francisca_events()
    except Exception as ex:
        print(f'Falha ao coletar Casa de Francisca: {ex}')
    try:
        events += get_casa_rockambole_events()
    except Exception as ex:
        print(f'Falha ao coletar Casa Rockambole: {ex}')
    try:
        events += get_balaclava_events()
    except Exception as ex:
        print(f'Falha ao coletar Balaclava: {ex}')
    try:
        events += get_bona_events()
    except Exception as ex:
        print(f'Falha ao coletar Bona Casa de Música: {ex}')

    events = dedupe(events)
    events.sort(key=sort_key)

    payload = {
        'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'events': events,
    }

    with open('events.json', 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"{len(events)} eventos coletados")

if __name__ == '__main__':
    run()
