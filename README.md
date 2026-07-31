# SDG Data Insights Dashboard

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/AdnaKoss/sdg-data-insights-dashboard)
[![Python](https://img.shields.io/badge/python-3.12-blue)](backend/requirements.txt)
[![React](https://img.shields.io/badge/react-18-61DAFB)](frontend/package.json)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688)](backend/requirements.txt)

<!-- Live demo: dodati link nakon deploy-a, npr. **[Live demo](https://sdg-data-insights-dashboard.onrender.com)** -->

Full-stack aplikacija koja obrađuje World Bank Open Data indikatore (pristup
internetu, obrazovanje, siromaštvo, rodna ravnopravnost, BDP...) i nad njima
radi analizu — KMeans klasterovanje zemalja po "digitalnoj spremnosti", linearnu
trend/forecast projekciju po zemlji, i auto-generisan policy brief (PDF/Markdown)
— kroz FastAPI REST API i React/Recharts dashboard.

## Arhitektura

```
World Bank Open Data API
        │  (scripts/fetch_data.py, jednokratno)
        ▼
backend/data/raw/*.csv  ──►  FastAPI (backend/app) ──► React dashboard (frontend/)
                                   │
                                   ├── /api/indicators, /api/countries   (catalogue)
                                   ├── /api/data, /summary, /ranking,
                                   │   /improvers                        (stats)
                                   ├── /api/analysis/clusters, /trend    (ML)
                                   ├── /api/reports/policy-brief         (PDF/MD)
                                   └── /api/admin/refresh-data           (live re-pull)
```

Podaci se povlače jednom (`scripts/fetch_data.py`) i commituju kao CSV u
`backend/data/raw/`, tako da aplikacija radi odmah nakon kloniranja repoa bez
potrebe za pozivanjem eksternog API-ja. `/api/admin/refresh-data` po potrebi
povuče svježe podatke sa World Bank API-ja u memoriju (ne mijenja committovane
CSV-ove).

## Struktura

```
backend/
  app/
    main.py          FastAPI aplikacija, CORS, lifespan (učitava keš u app.state)
    config.py        Definicije indikatora, broj klastera, putanje
    deps.py          FastAPI dependencies (dataframe iz app.state)
    schemas.py        Pydantic modeli za request/response
    data/            World Bank API klijent + CSV keš
    analysis/        stats.py, trend.py, clustering.py (pandas/scikit-learn)
    reports/         policy_brief.py — narativ + matplotlib grafovi ugrađeni u PDF
    routers/         catalogue, data, analysis, reports, admin
  data/raw/          countries.csv, indicators.csv (committovan demo dataset)
  scripts/fetch_data.py   Jednokratno povlačenje podataka sa World Bank API-ja
  tests/             pytest testovi (analysis, API, report, worldbank client)
  run.py             `python run.py` pokreće API na :8000
frontend/
  src/
    components/      Header, FilterBar, KpiCards, RankingChart, ImproversChart,
                      TrendPanel, ClusterScatter, PolicyBriefPanel
    styles/
  vite.config.js      Proxy /api → localhost:8000 u dev modu
```

## Pokretanje

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

# Prvi put: povuci realne podatke sa World Bank API-ja u data/raw/
python scripts/fetch_data.py

python run.py
```

API je dostupan na `http://localhost:8000`, Swagger dokumentacija na
`http://localhost:8000/docs`.

### Frontend (dev)

```bash
cd frontend
npm install
npm run dev
```

Vite dev server proxy-uje `/api/*` pozive na `http://localhost:8000` (vidi
`vite.config.js`), pa backend mora biti pokrenut paralelno.

### Produkcija (jedan proces)

```bash
cd frontend && npm run build   # generiše frontend/dist
cd ../backend && python run.py
```

FastAPI servira `frontend/dist` na `/` pored `/api/*` ruta (vidi
`app.mount("/", StaticFiles(...))` u `app/main.py`), tako da je nakon builda
dovoljan samo backend proces.

## Testovi

```bash
cd backend
pytest
```

## Tehnologije

- **Backend:** FastAPI, pandas, scikit-learn (KMeans, PCA), matplotlib, fpdf2, pytest
- **Frontend:** React 18, Vite, Recharts
