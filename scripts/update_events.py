#!/usr/bin/env python3
"""
Fetches live events from Shotgun API for Picles
and merges with the static seed data.
Writes events.json which index.html reads at runtime.

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
  # FRANCISCA
  {"name":"Nicolas Krassik e Pablo Moura","detail":"Forro franco-brasileiro","date":"Ter 07/4","time":"21h30","iso":"2026-04-07","venue":"Francisca Salao","v":"francisca","genre":"Forro","price":"","url":"https://bileto.sympla.com.br/event/117603"},
  {"name":"Romulo Froes","detail":"Lancamento Boneca Russa","date":"Qua 08/4","time":"21h30","iso":"2026-04-08","venue":"Francisca Salao","v":"francisca","genre":"MPB","price":"","url":"https://bileto.sympla.com.br/event/117567"},
  {"name":"Pagode da 27","detail":"","date":"Qua 08/4","time":"21h30","iso":"2026-04-08","venue":"Francisca Porao","v":"francisca","genre":"Samba","price":"Gratis","url":"https://casadefrancisca.art.br/novo/programacao"},
  {"name":"Aurea Martins e Cristovao Bastos","detail":"Feat. Renato Braz","date":"Qui 09/4","time":"21h30","iso":"2026-04-09","venue":"Francisca Salao","v":"francisca","genre":"MPB/Samba","price":"","url":"https://bileto.sympla.com.br/event/117570"},
  {"name":"Horoya 10 Anos","detail":"Afrobeat / jazz","date":"Sex 10/4","time":"22h","iso":"2026-04-10","venue":"Francisca Porao","v":"francisca","genre":"Afrobeat","price":"","url":"https://casadefrancisca.art.br/novo/programacao"},
  {"name":"Pagode da Dona Ivone","detail":"","date":"Sab 11/4","time":"17h","iso":"2026-04-11","venue":"Francisca Porao","v":"francisca","genre":"Samba","price":"R$26","url":"https://casadefrancisca.art.br/novo/programacao"},
  {"name":"Joao Camarero","detail":"Feat. Tigana Santana","date":"Sab 11/4","time":"22h","iso":"2026-04-11","venue":"Francisca Salao","v":"francisca","genre":"MPB","price":"","url":"https://bileto.sympla.com.br/event/117313"},
  {"name":"Roda Delas","detail":"Canta compositoras do samba","date":"Dom 12/4","time":"17h","iso":"2026-04-12","venue":"Francisca Porao","v":"francisca","genre":"Samba","price":"Gratis","url":"https://casadefrancisca.art.br/novo/programacao"},
  {"name":"Bruna Lucchesi","detail":"BANDOLEIRA","date":"Ter 14/4","time":"21h30","iso":"2026-04-14","venue":"Francisca Porao","v":"francisca","genre":"MPB/Indie","price":"","url":"https://bileto.sympla.com.br/event/117603"},
  {"name":"Andre Mehmari","detail":"2a Mostra de Piano","date":"Qua 15/4","time":"21h30","iso":"2026-04-15","venue":"Francisca Salao","v":"francisca","genre":"Classical","price":"","url":"https://bileto.sympla.com.br/event/117567"},
  {"name":"Bela Ciavatta","detail":"Feito o Sol","date":"Qui 16/4","time":"21h30","iso":"2026-04-16","venue":"Francisca Salao","v":"francisca","genre":"Afro-Bras.","price":"","url":"https://casadefrancisca.art.br/novo/programacao"},
  {"name":"Cida Moreira","detail":"A Musica de Angela Ro Ro","date":"Qui 16/4","time":"21h30","iso":"2026-04-16","venue":"Francisca Sala B","v":"francisca","genre":"MPB","price":"","url":"https://casadefrancisca.art.br/novo/programacao"},
  {"name":"Toninho Ferragutti e Nailor Proveta","detail":"Espelho do Som","date":"Sex 17/4","time":"22h","iso":"2026-04-17","venue":"Francisca Sala B","v":"francisca","genre":"Choro","price":"","url":"https://casadefrancisca.art.br/novo/programacao"},
  {"name":"Anais Sylla","detail":"Feat. Xenia Franca","date":"Qua 22/4","time":"21h30","iso":"2026-04-22","venue":"Francisca Salao","v":"francisca","genre":"Afro/MPB","price":"","url":"https://casadefrancisca.art.br/novo/programacao"},
  {"name":"Banda Gloria","detail":"Canta Chico Buarque","date":"Qui 23/4","time":"21h30","iso":"2026-04-23","venue":"Francisca Salao","v":"francisca","genre":"MPB/Samba","price":"","url":"https://casadefrancisca.art.br/novo/programacao"},
  {"name":"Blubell","detail":"Vaudeville","date":"Qui 23/4","time":"21h30","iso":"2026-04-23","venue":"Francisca Sala B","v":"francisca","genre":"MPB/Pop","price":"","url":"https://casadefrancisca.art.br/novo/programacao"},
  {"name":"Nega Duda","detail":"Samba de Roda","date":"Qui 23/4","time":"21h30","iso":"2026-04-23","venue":"Francisca Porao","v":"francisca","genre":"Samba","price":"Gratis","url":"https://casadefrancisca.art.br/novo/programacao"},
  {"name":"Explode Coracao 10 Anos","detail":"Tributo Maria Bethania","date":"Sex 24/4","time":"22h","iso":"2026-04-24","venue":"Francisca Salao","v":"francisca","genre":"Samba/MPB","price":"","url":"https://casadefrancisca.art.br/novo/programacao"},
  {"name":"Rodrigo Ogi e nILL","detail":"Manual Para Nao Desaparecer","date":"Sex 24/4","time":"22h","iso":"2026-04-24","venue":"Francisca Porao","v":"francisca","genre":"Rap","price":"","url":"https://casadefrancisca.art.br/novo/programacao"},
  {"name":"Samba do Aguida","detail":"","date":"Sab 25/4","time":"17h","iso":"2026-04-25","venue":"Francisca Porao","v":"francisca","genre":"Samba","price":"R$26","url":"https://casadefrancisca.art.br/novo/programacao"},
  {"name":"Jucara Marcal, Suzana Salles e Kiko Dinucci","detail":"Cantam Itamar","date":"Qua 29/4","time":"21h30","iso":"2026-04-29","venue":"Francisca Porao","v":"francisca","genre":"MPB","price":"","url":"https://casadefrancisca.art.br/novo/programacao"},
  # MALDITA
  {"name":"Jambu + Verdan","detail":"Indie rock, lancamento de disco","date":"Qui 02/4","time":"20h","iso":"2026-04-02","venue":"Porta Maldita","v":"maldita","genre":"Indie Rock","price":"R$35-50","url":"https://www.sympla.com.br/evento/a-porta-maldita-jambu-verdan/3341880"},
  {"name":"Felipe Tavora + Jalt + Cha Preto","detail":"Indie rock","date":"Sex 04/4","time":"20h","iso":"2026-04-04","venue":"Porta Maldita","v":"maldita","genre":"Indie Rock","price":"R$25-30","url":"https://www.sympla.com.br/evento/a-porta-maldita/3341881"},
  {"name":"ANOMALIA","detail":"AKA AFK, RUA 06, OKIE + mais","date":"Sab 11/4","time":"20h","iso":"2026-04-11","venue":"Porta Maldita","v":"maldita","genre":"Grime/Trap","price":"R$20","url":"https://www.sympla.com.br/evento/a-porta-maldita-anomalia/2859672"},
  {"name":"Bebe Feio + CRAS + Joker + BIG","detail":"","date":"Dom 12/4","time":"20h","iso":"2026-04-12","venue":"Porta Maldita","v":"maldita","genre":"Indie/Rock","price":"R$25","url":"https://www.sympla.com.br/evento/lgc/2869392"},
  {"name":"Animais + Surto Coletivo + All Star Dogs","detail":"Rock alternativo","date":"Sex 17/4","time":"20h","iso":"2026-04-17","venue":"Porta Maldita","v":"maldita","genre":"Rock","price":"R$25-30","url":"https://www.sympla.com.br/evento/a-porta-maldita/3369392"},
  # PORTA
  {"name":"Ryosuke Kiyasu + Aun Helden","detail":"Experimental","date":"Seg 30/3","time":"18h","iso":"2026-03-30","venue":"Porta, Pinheiros","v":"porta","genre":"Experimental","price":"R$40-50","url":"https://shotgun.live/pt-br/events/ryosuke-kiyasu-aun-helden"},
  {"name":"Pista Quente 0800 Club","detail":"Electronic","date":"2026","time":"","iso":"","venue":"Porta, Pinheiros","v":"porta","genre":"Eletronica","price":"Gratis","url":"https://shotgun.live/en/venues/p-o-r-t-a"},
  # ROCKAMBOLE
  {"name":"No Hope Fest","detail":"Experimental / noise - Test, Deafkids, Sturle Dagsland e mais","date":"Sex 03/4","time":"18h","iso":"2026-04-03","venue":"Casa Rockambole","v":"rockambole","genre":"Experimental","price":"R$30-60","url":"https://meaple.com.br/selorockambole/no-hope-fest"},
  # BONA
  {"name":"Jesse Harris","detail":"If You Believed In Me","date":"Ter 07/4","time":"20h","iso":"2026-04-07","venue":"Bona Casa de Musica","v":"bona","genre":"Folk/Jazz","price":"R$60","url":"https://www.eventim.com.br/artist/bona-casa-musica/jesse-harris/"},
  {"name":"Guilherme Neves","detail":"Samba Timido - feat. Cristovao Bastos, Renato Braz","date":"Qua 08/4","time":"21h","iso":"2026-04-08","venue":"Bona Casa de Musica","v":"bona","genre":"Samba/MPB","price":"R$60","url":"https://www.eventim.com.br/artist/bona-casa-musica/guilherme-neves-samba-timido/"},
  {"name":"Lan Lanh convida Chico Chico","detail":"","date":"Qui 09/4","time":"20h","iso":"2026-04-09","venue":"Bona Casa de Musica","v":"bona","genre":"MPB","price":"R$60","url":"https://www.eventim.com.br/artist/bona-casa-musica/lan-lanh-convida-chico-chico/"},
  {"name":"Salvador Sobral","detail":"Jazz / cantor-compositor portugues","date":"Sex 10/4","time":"20h","iso":"2026-04-10","venue":"Bona Casa de Musica","v":"bona","genre":"Jazz/MPB","price":"R$60","url":"https://www.eventim.com.br/artist/bona-casa-musica/salvador-sobral/"},
  {"name":"M.O.T.","detail":"Manga, Osvaldo e Tchernev (ex-Mutantes)","date":"Dom 12/4","time":"20h","iso":"2026-04-12","venue":"Bona Casa de Musica","v":"bona","genre":"Rock/MPB","price":"R$60","url":"https://www.eventim.com.br/artist/m-o-t-/"},
  {"name":"Marcelo Paiva e Luiza Villa","detail":"Anatomia de Bob Dylan","date":"Qua 15/4","time":"20h","iso":"2026-04-15","venue":"Bona Casa de Musica","v":"bona","genre":"Folk/MPB","price":"R$60","url":"https://www.eventim.com.br/artist/luiza-villa/"},
  {"name":"Xangai","detail":"Cultura sertaneja","date":"2026","time":"","iso":"","venue":"Bona Casa de Musica","v":"bona","genre":"MPB","price":"R$60","url":"https://www.eventim.com.br/artist/bona-casa-musica/"},
]

DAYS_PT = ["Dom","Seg","Ter","Qua","Qui","Sex","Sab"]

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
            day_str = DAYS_PT[dt_local.weekday() % 7 - 6 % 7] if True else ""
            # weekday(): Mon=0..Sun=6 → our DAYS_PT: Dom=0,Seg=1..Sab=6
            wd = (dt_local.weekday() + 1) % 7  # Mon=1..Sun=0 → shift to Dom=0
            day_str = DAYS_PT[wd]
            date_str = f"{day_str} {dt_local.day:02d}/{dt_local.month:02d}"
            time_str = f"{dt_local.hour:02d}h{dt_local.minute:02d}" if dt_local.minute else f"{dt_local.hour:02d}h"
            iso_str  = dt_local.strftime("%Y-%m-%d")
            slug = e.get("slug", "")
            result.append({
                "name":   e.get("name", ""),
                "detail": "",
                "date":   date_str,
                "time":   time_str,
                "iso":    iso_str,
                "venue":  "Picles Cardeal",
                "v":      "picles",
                "genre":  infer_genre(e.get("name", "")),
                "price":  "",
                "url":    f"https://shotgun.live/events/{slug}" if slug else "https://shotgun.live/en/venues/picles",
            })
        print(f"[picles] fetched {len(result)} events from Shotgun")
        return result
    except Exception as ex:
        print(f"[picles] fetch failed: {ex} — using fallback")
        return None

PICLES_FALLBACK = [
    {"name":"Vivendo do Ocio","detail":"+ Murilo Muraah + DJ Breno Oliveira","date":"Qui 09/4","time":"20h","iso":"2026-04-09","venue":"Picles Cardeal","v":"picles","genre":"Indie Rock","price":"R$40","url":"https://shotgun.live/en/venues/picles"},
    {"name":"The Mockers","detail":"","date":"Sex 10/4","time":"20h","iso":"2026-04-10","venue":"Picles Cardeal","v":"picles","genre":"Rock","price":"","url":"https://www.songkick.com/concerts/43132498"},
    {"name":"X.i.s. + DJ Erick Jay","detail":"","date":"Qui 16/4","time":"20h","iso":"2026-04-16","venue":"Picles Cardeal","v":"picles","genre":"Hip-hop","price":"","url":"https://shotgun.live/en/venues/picles"},
    {"name":"CACO + Juia","detail":"","date":"Sex 17/4","time":"20h","iso":"2026-04-17","venue":"Picles Cardeal","v":"picles","genre":"Indie","price":"","url":"https://shotgun.live/en/venues/picles"},
    {"name":"Caravaggio","detail":"","date":"Seg 20/4","time":"20h","iso":"2026-04-20","venue":"Picles Cardeal","v":"picles","genre":"Rock","price":"","url":"https://shotgun.live/en/venues/picles"},
]

def main():
    picles = fetch_picles()
    if not picles:
        picles = PICLES_FALLBACK

    all_events = STATIC_EVENTS + picles

    # Deduplicate by name+iso+venue
    seen = set()
    deduped = []
    for e in all_events:
        key = f"{e['name'].lower()}|{e.get('iso','')}|{e['v']}"
        if key not in seen:
            seen.add(key)
            deduped.append(e)

    # Sort by iso date
    def sort_key(e):
        return e.get("iso") or "9999"

    deduped.sort(key=sort_key)

    output = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "events": deduped,
    }

    out_path = os.path.join(os.path.dirname(__file__), "..", "data", "events.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"[done] {len(deduped)} events written to events.json")

if __name__ == "__main__":
    main()
