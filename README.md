# Shows SP

Agenda de shows em São Paulo — 9 casas independentes e culturais.

## Como subir no GitHub Pages

1. Crie um repositório **público** no GitHub chamado `shows-sp`
2. Suba todos os arquivos deste projeto para a branch `main`
3. Vá em **Settings → Pages → Source → Deploy from branch → main / root**
4. Acesse em `https://SEU_USUARIO.github.io/shows-sp/`

## Como funciona

```
index.html          → frontend estático, lê events.json
events.json         → dados dos eventos (gerado automaticamente)
scripts/update_events.py  → busca eventos novos do Shotgun + seed estático
.github/workflows/update.yml → roda toda segunda-feira às 8h UTC
```

O GitHub Actions roda o script semanalmente, busca a programação do Picles direto
da API do Shotgun, e faz commit do `events.json` atualizado no repositório.
O site lê esse arquivo estático — sem backend, sem chaves de API expostas.

## Rodar localmente

```bash
python3 scripts/update_events.py   # gera events.json
python3 -m http.server             # serve em localhost:8000
```

## Casas cobertas

| Casa | Fonte |
|------|-------|
| SESC | Seed manual (programação mensal) |
| Cine Joia | Seed + links Fastix/Shotgun/Songkick |
| Balaclava | Seed manual |
| Casa de Francisca | Seed manual |
| Porta Maldita | Seed manual (Sympla) |
| Porta Pinheiros | Seed manual (Shotgun) |
| Picles Cardeal | **API ao vivo do Shotgun** (atualiza toda segunda) |
| Casa Rockambole | Seed manual |
| Bona Casa de Música | Seed manual (Eventim) |

## Forçar atualização manual

No GitHub, vá em **Actions → Atualizar eventos → Run workflow**.


## Workflow

O workflow correto está em `.github/workflows/update-events.yml` e atualiza `data/events.json`.
