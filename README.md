# Shows SP

Agenda de shows em São Paulo com frontend estático no GitHub Pages e geração automatizada de `events.json`.

## Estrutura

- `index.html` → frontend estático
- `events.json` → agenda consolidada usada pelo site
- `seeds.json` → fallback e seed agrupado por casa
- `scripts/update_events.py` → pipeline principal de atualização

## O que foi refatorado

- O projeto deixou de depender de um único bloco `STATIC_EVENTS` gigante.
- A atualização agora usa arquitetura por fonte.
- O padrão do Picles foi generalizado para qualquer casa com endpoint direto compatível.
- Porta e Picles usam consulta direta via Shotgun quando disponível.
- As demais casas permanecem organizadas em `seeds.json`, prontas para ganhar coletores dedicados.

## Rodar localmente

```bash
python3 scripts/update_events.py
python3 -m http.server
```

## Próximos coletores sugeridos

- Casa de Francisca
- Cine Joia
- Bona / Eventim
- Porta Maldita / Sympla
- SESC

## Deploy

Publique o conteúdo na raiz de um repositório GitHub Pages.
