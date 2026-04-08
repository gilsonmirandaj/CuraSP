# Shows SP

Agenda de shows em São Paulo — projeto refatorado em pastas.

## Estrutura

```
shows-sp-refatorado/
├── index.html
├── data/
│   └── events.json
└── scripts/
    └── update_events.py
```

## O que mudou

- `events.json` foi movido para `data/events.json`.
- `update_events.py` foi movido para `scripts/update_events.py`.
- O script foi ajustado para gravar a saída em `data/events.json`.
- A correção do link da Casa Rockambole já está aplicada.

## Rodar localmente

```bash
python3 scripts/update_events.py
python3 -m http.server
```

## Observação

Se o `index.html` atual estiver fazendo `fetch("events.json")`, troque para `fetch("data/events.json")`.


## Ajustes aplicados

- Links da Casa de Francisca padronizados para a página oficial da casa na Sympla e para a página de programação oficial.


## Casa de Francisca

O script foi preparado para normalizar os eventos da Casa de Francisca a partir da página oficial na Sympla:

- Base oficial: `https://site.bileto.sympla.com.br/casadefrancisca/`
- Eventos da Francisca passam por normalização automática de URL.
- Links antigos de `bileto.sympla.com.br/event/...` e de programação genérica são substituídos pela base oficial da casa.

Se você quiser a etapa seguinte, dá para evoluir esse normalizador para um scraper que descubra e consulte cada evento individualmente a partir da página oficial.

- Eventos da Casa de Francisca restaurados no `events.json` do pacote e com links padronizados.


## Coletor da Francisca

O projeto agora possui um coletor dedicado da Casa de Francisca no script:

- `fetch_francisca_from_seed()` concentra o tratamento da casa.
- A normalização das URLs da Francisca fica centralizada.
- Os eventos da Francisca deixam de depender do fluxo genérico dos demais seeds.

Isso facilita a próxima etapa de trocar o seed por captura direta dos eventos individuais da Sympla.

- Casa de Francisca agora tem fallback visível apontando para a página oficial da Sympla, evitando desaparecer da interface.


## Estrutura compatível com GitHub Pages

Esta versão mantém `index.html` e `events.json` na raiz para preservar o deploy que já funcionava no GitHub Pages, enquanto move a captura para módulos em `scrapers/` e mantém um ponto de entrada em `run.py`.

## Coleta de dados

- `scrapers/picles_shotgun.py`: consulta direta ao endpoint público do Shotgun para o Picles.
- `scrapers/casa_francisca.py`: consulta a página oficial da Casa de Francisca e cria eventos normalizados.
- `run.py`: consolida os scrapers com os eventos estáticos das outras casas e regrava `events.json` na raiz.
- `.github/workflows/update-events.yml`: mantém o commit de `events.json` na raiz, preservando o fluxo de deploy que já funcionava.
