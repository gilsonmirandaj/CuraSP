#!/usr/bin/env python3
"""
Fetches live events from Shotgun API for Picles
and merges with the static seed data.
Writes data/events.json which index.html reads at runtime.

No API keys needed — Shotgun's public organization endpoint is unauthenticated.
Run by GitHub Actions weekly. Safe to run locally too.
"""

import json
import urllib.request
import urllib.error
from datetime import datetime, timezone
import os
import re

# ── STATIC SEED (all non-Picles events) ──────────────────────────
STATIC_EVENTS = [
# SESC
{"name":"Caique Tostes","detail":"Performance poetica e saude mental","date":"Qui 09/4","time":"19h","iso":"2026-04-09","venue":"SESC Ipiranga","v":"sesc","genre":"MPB","price":"Gratis","url":"https://www.sescsp.org.br/programacao/"},
{"name":"Negritude Jr.","detail":"Show","date":"Sex 10/4","time":"20h30","iso":"2026-04-10","venue":"SESC SP","v":"sesc","genre":"Pagode","price":"","url":"https://www.sescsp.org.br/programacao/"},
{"name":"Negritude Jr.","detail":"Show","date":"Sab 11/4","time":"20h30","iso":"2026-04-11","venue":"SESC SP","v":"sesc","genre":"Pagode","price":"","url":"https://www.sescsp.org.br/programacao/"},
{"name":"Mirim e Victor Xama","detail":"","date":"Dom 12/4","time":"","iso":"2026-04-12","venue":"SESC SP","v":"sesc","genre":"Rap","price":"","url":"https://www.sescsp.org.br/programacao/"},
{"name":"DJ Nelson Maca","detail":"Samba rock, MPB, soul","date":"Sab 18/4","time":"15h","iso":"2026-04-18","venue":"Nazare Paulista","v":"sesc","genre":"Samba","price":"Gratis","url":"https://www.sescsp.org.br/programacao/"},
{"name":"Comadres","detail":"Forro pe de serra, baiao","date":"Dom 19/4","time":"15h","iso":"2026-04-19","venue":"Bom Jesus dos Perdoes","v":"sesc","genre":"Forro","price":"Gratis","url":"https://www.sescsp.org.br/programacao/"},
{"name":"Show part. Djonga","detail":"Show autoral","date":"Qui 23/4","time":"21h","iso":"2026-04-23","venue":"SESC SP","v":"sesc","genre":"Hip-hop","price":"","url":"https://www.sescsp.org.br/?s=Djonga"},
{"name":"Show part. Djonga","detail":"","date":"Sex 24/4","time":"21h","iso":"2026-04-24","venue":"SESC SP","v":"sesc","genre":"Hip-hop","price":"","url":"https://www.sescsp.org.br/?s=Djonga"},
{"name":"Mari Jasca","detail":"Show solo Disparada","date":"Sex 24/4","time":"20h","iso":"2026-04-24","venue":"SESC 14 Bis","v":"sesc","genre":"MPB","price":"R$60","url":"https://www.sescsp.org.br/?s=Mari+Jasca"},
{"name":"Catto","detail":"Caminhos Selvagens + tributo Gal","date":"Sab 25/4","time":"20h","iso":"2026-04-25","venue":"SESC 14 Bis","v":"sesc","genre":"MPB","price":"R$60","url":"https://www.sescsp.org.br/programacao/"},
{"name":"Tributo Legiao Urbana","detail":"","date":"Sab 25/4","time":"21h","iso":"2026-04-25","venue":"SESC SP","v":"sesc","genre":"Rock","price":"","url":"https://www.sescsp.org.br/programacao/"},
{"name":"Bastos e Leila Pinheiro","detail":"","date":"Sab 25/4","time":"","iso":"2026-04-25","venue":"SESC SP","v":"sesc","genre":"MPB","price":"","url":"https://www.sescsp.org.br/programacao/"},
{"name":"Sarah Leandro","detail":"Forro de Bodoco","date":"Dom 26/4","time":"16h","iso":"2026-04-26","venue":"SESC Bom Retiro","v":"sesc","genre":"Forro","price":"Gratis","url":"https://www.sescsp.org.br/?s=Sarah+Leandro"},
{"name":"Samba do Comerciario","detail":"","date":"Ter 28/4","time":"","iso":"2026-04-28","venue":"SESC SP","v":"sesc","genre":"Samba","price":"Gratis","url":"https://www.sescsp.org.br/programacao/"},
{"name":"Alma Djem","detail":"Acustico - Reggae, MPB, Soul","date":"Qui 30/4","time":"21h","iso":"2026-04-30","venue":"SESC SP","v":"sesc","genre":"Reggae","price":"R$60","url":"https://www.sescsp.org.br/?s=Alma+Djem"},
# CINE JOIA
{"name":"Public Image Ltd.","detail":"Com The Gulps","date":"Qua 08/4","time":"19h","iso":"2026-04-08","venue":"Cine Joia","v":"cine","genre":"Post-punk","price":"","url":"https://fastix.com.br/events/public-image-ltd-em-sao-paulo"},
{"name":"Oriente","detail":"","date":"Sab 11/4","time":"20h","iso":"2026-04-11","venue":"Cine Joia","v":"cine","genre":"Hip-hop","price":"","url":"https://www.songkick.com/concerts/43045390"},
{"name":"Anna Tsuchiya","detail":"","date":"Ter 14/4","time":"","iso":"2026-04-14","venue":"Cine Joia","v":"cine","genre":"Rock/Pop","price":"","url":"https://www.songkick.com/concerts/43013462"},
{"name":"Mad Professor","detail":"Com Liquidus Ambiento","date":"Qui 16/4","time":"19h","iso":"2026-04-16","venue":"Cine Joia","v":"cine","genre":"Reggae","price":"","url":"https://www.songkick.com/concerts/43083456"},
{"name":"Cachorro Grande","detail":"","date":"Sex 17/4","time":"20h","iso":"2026-04-17","venue":"Cine Joia","v":"cine","genre":"Rock","price":"","url":"https://www.songkick.com/concerts/43045390"},
{"name":"Midnight Til Morning","detail":"","date":"Sab 18/4","time":"19h","iso":"2026-04-18","venue":"Cine Joia","v":"cine","genre":"Pop","price":"","url":"https://www.songkick.com/concerts/42936819"},
{"name":"Ze Ibarra","detail":"","date":"Qui 23/4","time":"19h","iso":"2026-04-23","venue":"Cine Joia","v":"cine","genre":"MPB","price":"","url":"https://www.songkick.com/concerts/43094750"},
{"name":"Maglore","detail":"","date":"Sex 24/4","time":"21h","iso":"2026-04-24","venue":"Cine Joia","v":"cine","genre":"Indie Rock","price":"","url":"https://shotgun.live/en/events/maglorenocinejoia"},
{"name":"The 5.6.7.8s","detail":"","date":"Sab 26/4","time":"","iso":"2026-04-26","venue":"Cine Joia","v":"cine","genre":"Rock","price":"","url":"https://www.cinejoia.com.br/agenda/"},
{"name":"Varukers","detail":"","date":"Sex 08/5","time":"","iso":"2026-05-08","venue":"Cine Joia","v":"cine","genre":"Punk","price":"","url":"https://shotgun.live/pt-br/events/thevarukersnocinejoia"},
{"name":"Leisure","detail":"","date":"Qua 13/5","time":"21h","iso":"2026-05-13","venue":"Cine Joia","v":"cine","genre":"Funk/Soul","price":"","url":"https://www.songkick.com/concerts/43038806"},
{"name":"Superchunk","detail":"Balaclava apresenta","date":"Dom 31/5","time":"19h","iso":"2026-05-31","venue":"Cine Joia","v":"cine","genre":"Indie Rock","price":"","url":"https://ingresse.com/superchunk-sp"},
{"name":"Shame","detail":"Balaclava apresenta","date":"Sab 20/6","time":"19h","iso":"2026-06-20","venue":"Cine Joia","v":"cine","genre":"Post-punk","price":"","url":"https://ingresse.com/shame-sp"},
# BALACLAVA
{"name":"Mac DeMarco","detail":"","date":"Sab 04/4","time":"21h","iso":"2026-04-04","venue":"Audio SP","v":"balaclava","genre":"Indie/Pop","price":"","url":"https://www.ingresse.com/macdemarco-sp2/"},
{"name":"Mac DeMarco","detail":"Data extra","date":"Dom 05/4","time":"19h","iso":"2026-04-05","venue":"Audio SP","v":"balaclava","genre":"Indie/Pop","price":"","url":"https://www.ingresse.com/macdemarco-sp2/"},
# ROCKAMBOLE
{"name":"No Hope Fest","detail":"Experimental / noise - Test, Deafkids, Sturle Dagsland e mais","date":"Sex 03/4","time":"18h","iso":"2026-04-03","venue":"Casa Rockambole","v":"rockambole","genre":"Experimental","price":"R$30-60","url":"https://meaple.com.br/rockambole/no-hope-fest"},
# BONA
{"name":"Jesse Harris","detail":"If You Believed In Me","date":"Ter 07/4","time":"20h","iso":"2026-04-07","venue":"Bona Casa de Musica","v":"bona","genre":"Folk/Jazz","price":"R$60","url":"https://www.eventim.com.br/artist/bona-casa-musica/jesse-harris/"},
]

DAYS_PT = ["Dom","Seg","Ter","Qua","Qui","Sex","Sab"]

FRANCISCA_BASE_URL = "https://site.bileto.sympla.com.br/casadefrancisca/"


def normalize_francisca_url(url, fallback=FRANCISCA_BASE_URL):
    if not url:
        return fallback
    url = url.strip()
    if "site.bileto.sympla.com.br/casadefrancisca" in url:
        return url
    if "casadefrancisca.art.br/novo/programacao" in url:
        return fallback
    if "bileto.sympla.com.br/event/" in url:
        return fallback
    return url


def normalize_static_event(event):
    event = dict(event)
    if event.get("v") == "francisca":
        event["url"] = normalize_francisca_url(event.get("url", ""))
    return event


def infer_genre(name):
    n = name.lower()
    if re.search(r'rock|punk|metal|grunge', n): return "Rock"
    if re.search(r'indie', n): return "Indie Rock"
    if re.search(r'jazz', n): return "Jazz"
    if re.search(r'samba|pagode', n): return "Samba"
    if re.search(r'mpb|folk|acustic', n): return "MPB"
    if re.search(r'hip.hop|rap', n): return "Hip-hop"
    if re.search(r'eletr|elet|\bdj\b|club', n): return "Eletronica"
    if re.search(r'forro|baiao', n): return "Forro"
    return "Indie Rock"

def fetch_picles():
    url = "https://shotgun.live/api/organizations/picles/events?language=pt-br"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        events = data.get("events", [])
        result = []
        for e in events:
            start = e.get("startDate", "")
            if not start:
                continue
            dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
            dt_local = dt.astimezone()
            wd = (dt_local.weekday() + 1) % 7
            day_str = DAYS_PT[wd]
            date_str = f"{day_str} {dt_local.day:02d}/{dt_local.month:02d}"
            time_str = f"{dt_local.hour:02d}h{dt_local.minute:02d}" if dt_local.minute else f"{dt_local.hour:02d}h"
            iso_str = dt_local.strftime("%Y-%m-%d")
            slug = e.get("slug", "")
            result.append({
                "name": e.get("name", ""),
                "detail": "",
                "date": date_str,
                "time": time_str,
                "iso": iso_str,
                "venue": "Picles Cardeal",
                "v": "picles",
                "genre": infer_genre(e.get("name", "")),
                "price": "",
                "url": f"https://shotgun.live/events/{slug}" if slug else "https://shotgun.live/en/venues/picles",
            })
        return result
    except Exception:
        return None

PICLES_FALLBACK = [
    {"name":"Vivendo do Ocio","detail":"+ Murilo Muraah + DJ Breno Oliveira","date":"Qui 09/4","time":"20h","iso":"2026-04-09","venue":"Picles Cardeal","v":"picles","genre":"Indie Rock","price":"R$40","url":"https://shotgun.live/en/venues/picles"},
]

def main():
    picles = fetch_picles() or PICLES_FALLBACK
    all_events = [normalize_static_event(e) for e in STATIC_EVENTS] + picles

    seen = set()
    deduped = []
    for e in all_events:
        key = f"{e['name'].lower()}|{e.get('iso','')}|{e['v']}"
        if key not in seen:
            seen.add(key)
            deduped.append(e)

    deduped.sort(key=lambda e: e.get("iso") or "9999")

    output = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "events": deduped,
    }

    out_path = os.path.join(os.path.dirname(__file__), "..", "data", "events.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
