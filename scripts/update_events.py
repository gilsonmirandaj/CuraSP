#!/usr/bin/env python3
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
import re

STATIC_EVENTS = [
  {
    "name": "Ryosuke Kiyasu + Aun Helden",
    "detail": "Experimental",
    "date": "Seg 30/3",
    "time": "18h",
    "iso": "2026-03-30",
    "venue": "Porta, Pinheiros",
    "v": "porta",
    "genre": "Experimental",
    "price": "R$40-50",
    "url": "https://shotgun.live/pt-br/events/ryosuke-kiyasu-aun-helden"
  },
  {
    "name": "Jambu + Verdan",
    "detail": "Indie rock, lancamento de disco",
    "date": "Qui 02/4",
    "time": "20h",
    "iso": "2026-04-02",
    "venue": "Porta Maldita",
    "v": "maldita",
    "genre": "Indie Rock",
    "price": "R$35-50",
    "url": "https://www.sympla.com.br/evento/a-porta-maldita-jambu-verdan/3341880"
  },
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
    "url": "https://meaple.com.br/selorockambole/no-hope-fest"
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
    "name": "Felipe Tavora + Jalt + Cha Preto",
    "detail": "Indie rock",
    "date": "Sex 04/4",
    "time": "20h",
    "iso": "2026-04-04",
    "venue": "Porta Maldita",
    "v": "maldita",
    "genre": "Indie Rock",
    "price": "R$25-30",
    "url": "https://www.sympla.com.br/evento/a-porta-maldita/3341881"
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
    "name": "Nicolas Krassik e Pablo Moura",
    "detail": "Forro franco-brasileiro",
    "date": "Ter 07/4",
    "time": "21h30",
    "iso": "2026-04-07",
    "venue": "Francisca Salao",
    "v": "francisca",
    "genre": "Forro",
    "price": "",
    "url": "https://bileto.sympla.com.br/event/117603"
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
    "name": "Romulo Froes",
    "detail": "Lancamento Boneca Russa",
    "date": "Qua 08/4",
    "time": "21h30",
    "iso": "2026-04-08",
    "venue": "Francisca Salao",
    "v": "francisca",
    "genre": "MPB",
    "price": "",
    "url": "https://bileto.sympla.com.br/event/117567"
  },
  {
    "name": "Pagode da 27",
    "detail": "",
    "date": "Qua 08/4",
    "time": "21h30",
    "iso": "2026-04-08",
    "venue": "Francisca Porao",
    "v": "francisca",
    "genre": "Samba",
    "price": "Gratis",
    "url": "https://casadefrancisca.art.br/novo/programacao"
  },
  {
    "name": "Guilherme Neves",
    "detail": "Samba Timido - feat. Cristovao Bastos, Renato Braz",
    "date": "Qua 08/4",
    "time": "21h",
    "iso": "2026-04-08",
    "venue": "Bona Casa de Musica",
    "v": "bona",
    "genre": "Samba/MPB",
    "price": "R$60",
    "url": "https://www.eventim.com.br/artist/bona-casa-musica/guilherme-neves-samba-timido/"
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
    "name": "Aurea Martins e Cristovao Bastos",
    "detail": "Feat. Renato Braz",
    "date": "Qui 09/4",
    "time": "21h30",
    "iso": "2026-04-09",
    "venue": "Francisca Salao",
    "v": "francisca",
    "genre": "MPB/Samba",
    "price": "",
    "url": "https://bileto.sympla.com.br/event/117570"
  },
  {
    "name": "Lan Lanh convida Chico Chico",
    "detail": "",
    "date": "Qui 09/4",
    "time": "20h",
    "iso": "2026-04-09",
    "venue": "Bona Casa de Musica",
    "v": "bona",
    "genre": "MPB",
    "price": "R$60",
    "url": "https://www.eventim.com.br/artist/bona-casa-musica/lan-lanh-convida-chico-chico/"
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
    "name": "Horoya 10 Anos",
    "detail": "Afrobeat / jazz",
    "date": "Sex 10/4",
    "time": "22h",
    "iso": "2026-04-10",
    "venue": "Francisca Porao",
    "v": "francisca",
    "genre": "Afrobeat",
    "price": "",
    "url": "https://casadefrancisca.art.br/novo/programacao"
  },
  {
    "name": "Salvador Sobral",
    "detail": "Jazz / cantor-compositor portugues",
    "date": "Sex 10/4",
    "time": "20h",
    "iso": "2026-04-10",
    "venue": "Bona Casa de Musica",
    "v": "bona",
    "genre": "Jazz/MPB",
    "price": "R$60",
    "url": "https://www.eventim.com.br/artist/bona-casa-musica/salvador-sobral/"
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
    "name": "Pagode da Dona Ivone",
    "detail": "",
    "date": "Sab 11/4",
    "time": "17h",
    "iso": "2026-04-11",
    "venue": "Francisca Porao",
    "v": "francisca",
    "genre": "Samba",
    "price": "R$26",
    "url": "https://casadefrancisca.art.br/novo/programacao"
  },
  {
    "name": "Joao Camarero",
    "detail": "Feat. Tigana Santana",
    "date": "Sab 11/4",
    "time": "22h",
    "iso": "2026-04-11",
    "venue": "Francisca Salao",
    "v": "francisca",
    "genre": "MPB",
    "price": "",
    "url": "https://bileto.sympla.com.br/event/117313"
  },
  {
    "name": "ANOMALIA",
    "detail": "AKA AFK, RUA 06, OKIE + mais",
    "date": "Sab 11/4",
    "time": "20h",
    "iso": "2026-04-11",
    "venue": "Porta Maldita",
    "v": "maldita",
    "genre": "Grime/Trap",
    "price": "R$20",
    "url": "https://www.sympla.com.br/evento/a-porta-maldita-anomalia/2859672"
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
    "name": "Roda Delas",
    "detail": "Canta compositoras do samba",
    "date": "Dom 12/4",
    "time": "17h",
    "iso": "2026-04-12",
    "venue": "Francisca Porao",
    "v": "francisca",
    "genre": "Samba",
    "price": "Gratis",
    "url": "https://casadefrancisca.art.br/novo/programacao"
  },
  {
    "name": "Bebe Feio + CRAS + Joker + BIG",
    "detail": "",
    "date": "Dom 12/4",
    "time": "20h",
    "iso": "2026-04-12",
    "venue": "Porta Maldita",
    "v": "maldita",
    "genre": "Indie/Rock",
    "price": "R$25",
    "url": "https://www.sympla.com.br/evento/lgc/2869392"
  },
  {
    "name": "M.O.T.",
    "detail": "Manga, Osvaldo e Tchernev (ex-Mutantes)",
    "date": "Dom 12/4",
    "time": "20h",
    "iso": "2026-04-12",
    "venue": "Bona Casa de Musica",
    "v": "bona",
    "genre": "Rock/MPB",
    "price": "R$60",
    "url": "https://www.eventim.com.br/artist/m-o-t-/"
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
    "name": "Bruna Lucchesi",
    "detail": "BANDOLEIRA",
    "date": "Ter 14/4",
    "time": "21h30",
    "iso": "2026-04-14",
    "venue": "Francisca Porao",
    "v": "francisca",
    "genre": "MPB/Indie",
    "price": "",
    "url": "https://bileto.sympla.com.br/event/117603"
  },
  {
    "name": "Andre Mehmari",
    "detail": "2a Mostra de Piano",
    "date": "Qua 15/4",
    "time": "21h30",
    "iso": "2026-04-15",
    "venue": "Francisca Salao",
    "v": "francisca",
    "genre": "Classical",
    "price": "",
    "url": "https://bileto.sympla.com.br/event/117567"
  },
  {
    "name": "Marcelo Paiva e Luiza Villa",
    "detail": "Anatomia de Bob Dylan",
    "date": "Qua 15/4",
    "time": "20h",
    "iso": "2026-04-15",
    "venue": "Bona Casa de Musica",
    "v": "bona",
    "genre": "Folk/MPB",
    "price": "R$60",
    "url": "https://www.eventim.com.br/artist/luiza-villa/"
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
    "name": "Bela Ciavatta",
    "detail": "Feito o Sol",
    "date": "Qui 16/4",
    "time": "21h30",
    "iso": "2026-04-16",
    "venue": "Francisca Salao",
    "v": "francisca",
    "genre": "Afro-Bras.",
    "price": "",
    "url": "https://casadefrancisca.art.br/novo/programacao"
  },
  {
    "name": "Cida Moreira",
    "detail": "A Musica de Angela Ro Ro",
    "date": "Qui 16/4",
    "time": "21h30",
    "iso": "2026-04-16",
    "venue": "Francisca Sala B",
    "v": "francisca",
    "genre": "MPB",
    "price": "",
    "url": "https://casadefrancisca.art.br/novo/programacao"
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
    "name": "Toninho Ferragutti e Nailor Proveta",
    "detail": "Espelho do Som",
    "date": "Sex 17/4",
    "time": "22h",
    "iso": "2026-04-17",
    "venue": "Francisca Sala B",
    "v": "francisca",
    "genre": "Choro",
    "price": "",
    "url": "https://casadefrancisca.art.br/novo/programacao"
  },
  {
    "name": "Animais + Surto Coletivo + All Star Dogs",
    "detail": "Rock alternativo",
    "date": "Sex 17/4",
    "time": "20h",
    "iso": "2026-04-17",
    "venue": "Porta Maldita",
    "v": "maldita",
    "genre": "Rock",
    "price": "R$25-30",
    "url": "https://www.sympla.com.br/evento/a-porta-maldita/3369392"
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
    "name": "Anais Sylla",
    "detail": "Feat. Xenia Franca",
    "date": "Qua 22/4",
    "time": "21h30",
    "iso": "2026-04-22",
    "venue": "Francisca Salao",
    "v": "francisca",
    "genre": "Afro/MPB",
    "price": "",
    "url": "https://casadefrancisca.art.br/novo/programacao"
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
    "name": "Banda Gloria",
    "detail": "Canta Chico Buarque",
    "date": "Qui 23/4",
    "time": "21h30",
    "iso": "2026-04-23",
    "venue": "Francisca Salao",
    "v": "francisca",
    "genre": "MPB/Samba",
    "price": "",
    "url": "https://casadefrancisca.art.br/novo/programacao"
  },
  {
    "name": "Blubell",
    "detail": "Vaudeville",
    "date": "Qui 23/4",
    "time": "21h30",
    "iso": "2026-04-23",
    "venue": "Francisca Sala B",
    "v": "francisca",
    "genre": "MPB/Pop",
    "price": "",
    "url": "https://casadefrancisca.art.br/novo/programacao"
  },
  {
    "name": "Nega Duda",
    "detail": "Samba de Roda",
    "date": "Qui 23/4",
    "time": "21h30",
    "iso": "2026-04-23",
    "venue": "Francisca Porao",
    "v": "francisca",
    "genre": "Samba",
    "price": "Gratis",
    "url": "https://casadefrancisca.art.br/novo/programacao"
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
    "name": "Explode Coracao 10 Anos",
    "detail": "Tributo Maria Bethania",
    "date": "Sex 24/4",
    "time": "22h",
    "iso": "2026-04-24",
    "venue": "Francisca Salao",
    "v": "francisca",
    "genre": "Samba/MPB",
    "price": "",
    "url": "https://casadefrancisca.art.br/novo/programacao"
  },
  {
    "name": "Rodrigo Ogi e nILL",
    "detail": "Manual Para Nao Desaparecer",
    "date": "Sex 24/4",
    "time": "22h",
    "iso": "2026-04-24",
    "venue": "Francisca Porao",
    "v": "francisca",
    "genre": "Rap",
    "price": "",
    "url": "https://casadefrancisca.art.br/novo/programacao"
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
    "name": "Samba do Aguida",
    "detail": "",
    "date": "Sab 25/4",
    "time": "17h",
    "iso": "2026-04-25",
    "venue": "Francisca Porao",
    "v": "francisca",
    "genre": "Samba",
    "price": "R$26",
    "url": "https://casadefrancisca.art.br/novo/programacao"
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
    "name": "Jucara Marcal, Suzana Salles e Kiko Dinucci",
    "detail": "Cantam Itamar",
    "date": "Qua 29/4",
    "time": "21h30",
    "iso": "2026-04-29",
    "venue": "Francisca Porao",
    "v": "francisca",
    "genre": "MPB",
    "price": "",
    "url": "https://casadefrancisca.art.br/novo/programacao"
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
  },
  {
    "name": "Pista Quente 0800 Club",
    "detail": "Electronic",
    "date": "2026",
    "time": "",
    "iso": "",
    "venue": "Porta, Pinheiros",
    "v": "porta",
    "genre": "Eletronica",
    "price": "Gratis",
    "url": "https://shotgun.live/en/venues/p-o-r-t-a"
  },
  {
    "name": "Xangai",
    "detail": "Cultura sertaneja",
    "date": "2026",
    "time": "",
    "iso": "",
    "venue": "Bona Casa de Musica",
    "v": "bona",
    "genre": "MPB",
    "price": "R$60",
    "url": "https://www.eventim.com.br/artist/bona-casa-musica/"
  }
]

PICLES_FALLBACK = [
  {"name":"Picles Cardeal","detail":"Fallback da venue","date":"2026","time":"","iso":"","venue":"Picles Cardeal","v":"picles","genre":"","price":"","url":"https://shotgun.live/en/venues/picles"}
]

DAYS_PT = ["Dom","Seg","Ter","Qua","Qui","Sex","Sab"]

def infer_genre(name: str) -> str:
    n = (name or '').lower()
    if re.search(r'rock|punk|metal|grunge', n): return 'Rock'
    if re.search(r'indie', n): return 'Indie Rock'
    if re.search(r'jazz', n): return 'Jazz'
    if re.search(r'samba|pagode', n): return 'Samba'
    if re.search(r'mpb|folk|acust', n): return 'MPB'
    if re.search(r'hip[ -]?hop|rap', n): return 'Hip-hop'
    if re.search(r'eletr|elet|\bdj\b|club|house|techno', n): return 'Eletrônica'
    if re.search(r'forr[oó]|baiao|baião', n): return 'Forró'
    return 'Indie Rock'

def weekday_pt(dt):
    return DAYS_PT[(dt.weekday() + 1) % 7]

def fetch_picles():
    url = 'https://shotgun.live/api/organizations/picles/events?language=pt-br'
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0','Accept':'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            payload = json.loads(r.read().decode('utf-8'))
        events = payload.get('events', []) if isinstance(payload, dict) else []
        out = []
        for e in events:
            start = e.get('startDate') or e.get('start_at') or ''
            if not start:
                continue
            try:
                dt = datetime.fromisoformat(start.replace('Z', '+00:00')).astimezone()
            except Exception:
                continue
            slug = e.get('slug', '')
            out.append({
                'name': e.get('name', '').strip(),
                'detail': '',
                'date': f"{weekday_pt(dt)} {dt.day:02d}/{dt.month:02d}",
                'time': f"{dt.hour:02d}h{dt.minute:02d}" if dt.minute else f"{dt.hour:02d}h",
                'iso': dt.strftime('%Y-%m-%d'),
                'venue': 'Picles Cardeal',
                'v': 'picles',
                'genre': infer_genre(e.get('name', '')),
                'price': '',
                'url': f"https://shotgun.live/events/{slug}" if slug else 'https://shotgun.live/en/venues/picles'
            })
        print(f'[picles] fetched {len(out)} events')
        return out
    except Exception as ex:
        print(f'[picles] fetch failed: {ex}')
        return None

def dedupe(events):
    seen = set()
    out = []
    for e in events:
        if not isinstance(e, dict):
            continue
        key = f"{(e.get('name') or '').strip().lower()}|{e.get('iso') or ''}|{e.get('v') or ''}"
        if key in seen:
            continue
        seen.add(key)
        out.append(e)
    return out

def sort_key(e):
    iso = e.get('iso') or '9999-99-99'
    return (iso, e.get('time') or '99:99', e.get('name') or '')

def main():
    picles = fetch_picles() or PICLES_FALLBACK
    all_events = dedupe(STATIC_EVENTS + picles)
    all_events.sort(key=sort_key)
    output = {
        'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'events': all_events,
    }
    out_path = Path(__file__).resolve().parent.parent / 'data' / 'events.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'[done] {len(all_events)} events written to {out_path}')

if __name__ == '__main__':
    main()
