# Documentation technique — Pack 3 « Prévisions & Accompagnement »

> **Version 2.0 — 4 août 2025**\
> (remplace intégralement la v1.0)

---

## Table des matières

1. [Architecture du dépôt](#architecture)
2. [Flux d’exécution détaillé](#flux)
3. [Spécification du moteur ](#moteur)[`forecast`](#moteur)
4. [Interface Streamlit : structure & états](#streamlit)
5. [Tests & intégration continue](#tests)
6. [Build, packaging & déploiement](#deploy)
7. [Sécurité, conformité & RGPD](#security)
8. [Roadmap d’extensions](#roadmap)
9. [Glossaire](#glossaire)

---



## 1. Architecture du dépôt

```
📦 offre-pack-3/
├── app/                     # Front Streamlit
│   └── main.py             # page unique (SPA)
├── model/                   # Moteur métier
│   ├── __init__.py
│   └── forecast.py         # simulate(), Scenario
├── tests/                  
│   └── test_forecast.py    # 4 tests Pytest
├── requirements.txt        # runtime + dev deps
├── .pre-commit-config.yaml # lint & format
├── .github/workflows/ci.yml# GitHub Actions (CI)
└── Dockerfile              # image prêt prod
```

### Découplage logique

- **Presentation layer** : `Streamlit` (widgets, charts, export).
- **Business logic** : `model.forecast` (sans I/O → testable).
- **Persistence** : in‑memory (CSV/Excel en buffer) → facile à brancher sur BDD ou S3 plus tard.

### Matrice des environnements

| Contexte       | Python                     | Navigateur cible    | Notes            |
| -------------- | -------------------------- | ------------------- | ---------------- |
| Dev local      |  3.12 venv                 | Chrome 125+         | `localhost:8501` |
| CI GitHub      |  3.12 actions/setup-python | —                   | Lint + tests     |
| Docker         |  python:3.12‑slim          | —                   | Expose `PORT`    |
| Cloud (Render) |  Docker image              | Edge/Chrome/Firefox | Autodeployment   |

---



## 2. Flux d’exécution détaillé

```
╭──────── Streamlit UI (main.py) ────────╮
│ 1. User sets sliders & selects scenario │
│  ↓                                     │
│ 2. run_simulation()  (cached)          │
╰──────────────┬──────────────────────────╯
               │ DataFrame (monthly rows)
               ▼
╭──────────────── forecast.py ───────────╮
│ simulate(start, months, mrr0, ...)     │
│  • vectorised NumPy maths              │
│  • returns df + attrs metadata         │
╰─────────────────────────────────────────╯
               ▼
╭──────── KPIs & Charts (Plotly) ────────╮
│ 3. Metrics tiles + line charts         │
╰─────────────────────────────────────────╯
               ▼
╭──────── Export module ────────────────╮
│ 4. Writes CSV (StringIO) & XLSX (BytesIO) │
╰─────────────────────────────────────────╯
```

*Temps de calcul* : < 1 ms pour 60 mois (machine dev M1).

---



## 3. Spécification du moteur `model.forecast`

### 3.1 Dataclass `Scenario`

```python
@dataclass(slots=True, frozen=True)
class Scenario:
    name: str           # Identifiant logique
    growth: float       # Decimal (ex : 0.05)
    churn: float        # Decimal (0‑1)
    cogs_pct: float     # % CA en COGS
    opex_rnd: float     # € / mois
    opex_sm: float
    opex_ga: float
```

### 3.2 Fonction `simulate()`

```python
simulate(start_date: datetime,
         months: int,
         mrr0: float,
         initial_cash: float,
         scenario: Scenario) -> pd.DataFrame
```

| Colonne           | Type      | Description                |
| ----------------- | --------- | -------------------------- |
| `month`           | int       | 1..N                       |
| `date`            | Timestamp | 1ᵉʳ du mois                |
| `mrr` / `revenue` | float     | CA mensuel (≈ MRR)         |
| `cogs`            | float     | Cost of Goods Sold         |
| `gross_profit`    | float     | Revenue − COGS             |
| `opex_*`          | float     | Opex fixes                 |
| `ebitda`          | float     | GP − Opex                  |
| `operating_cf`    | float     | Simplifié = EBITDA         |
| `cash_balance`    | float     | Cumulé avec `initial_cash` |

*Complexité* : O(N) — une passe vectorisée.

### 3.3 Extension points

- **Working capital** : ajouter ΔBFR avant cash.
- **CAPEX & amortissements** : nouveaux flux + impacts EBITDA.
- **Financement** : lignes dette, equity, intérêts.

---



## 4. Interface Streamlit

| Composant | ID / code              | Description                                                      |
| --------- | ---------------------- | ---------------------------------------------------------------- |
| Sidebar   | `st.sidebar.*`         | Sliders : growth, churn, COGS, opex.Inputs : MRR₀, cash₀, durée. |
| KPI tiles | `st.metric()`          | ARR M12, runway, EBITDA M1.                                      |
| Charts    | `plotly.express.line`  | `cash_balance`, `revenue`, `ebitda`.                             |
| Expander  | `st.dataframe()`       | Aperçu DataFrame.                                                |
| Download  | `st.download_button()` | CSV + XLSX.                                                      |

### États Streamlit

- **cache\_data** pour memoize `simulate()` -> évite recalcul si mêmes inputs.
- **session\_state** future : langue, dark/light mode.

---



## 5. Tests & intégration continue

### 5.1 Pytest

Quatre tests unitaires (100 % lignes couvertes pour `simulate()`). Ajouter prochainement :

- Tests de régression performance (< 5 ms pour 120 mois).
- Tests E2E Streamlit (Playwright).

### 5.2 GitHub Actions (extrait)

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.12'}
      - run: pip install -r requirements.txt
      - run: pytest -q
```

---



## 6. Build, packaging & déploiement

### 6.1 Dockerfile (extrait)

```Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
ENV PORT=8501
EXPOSE 8501
CMD ["streamlit", "run", "app/main.py", "--server.port", "${PORT}"]
```

### 6.2 Render.com (IaC YAML)

```yaml
services:
  - type: web
    name: pack3-demo
    env: docker
    plan: free
    autoDeploy: true
    dockerCommand: ""
```

### 6.3 Monitoring & logs

- Streamlit logs : stdout/stderr → Console Render.
- Healthcheck : `/healthz` route (à ajouter).

---



## 7. Sécurité, conformité & RGPD

| Aspect           | Mesure                                                                       |
| ---------------- | ---------------------------------------------------------------------------- |
| Données perso    | Le jeu de données démo est **fictif** → pas de données personnelles.         |
| Authentification | à activer via service d’hébergement (Basic Auth Render) si partage prospect. |
| Chiffrement      | TLS automatique (Render), aucune donnée persistée côté serveur.              |
| Dépendances      | SCA via Dependabot + `pip-audit` dans CI.                                    |

---



## 8. Roadmap d’extensions

1. **Tornado chart** interactif pour sensibilité (Plotly `go.Bar` orientation ='h').
2. **Upload réel vs budget** : merge DataFrame Pack 2 (actuals) avec prévision.
3. **API FastAPI** : `/simulate` → JSON pour intégration tierce.
4. **Internationalisation** : `st.session_state['lang']` + i18n JSON.
5. **RBAC** : Streamlit Auth0 component pour accès multi‑rôles.

---



## 9. Glossaire

| Terme             | Définition                                                           |
| ----------------- | -------------------------------------------------------------------- |
| **MRR**           | Monthly Recurring Revenue – revenus récurrents facturés chaque mois. |
| **ARR**           | Annual Recurring Revenue – MRR × 12.                                 |
| **COGS**          | Cost of Goods Sold – coûts directs de production/service.            |
| **Opex**          | Operating Expenses – dépenses d’exploitation hors COGS.              |
| **EBITDA**        | Earnings Before Interest, Taxes, Depreciation & Amortisation.        |
| **Runway**        | Durée avant épuisement de la trésorerie (mois).                      |
| **Scenario**      | Jeu d’hypothèses (growth, churn, coûts) pour la simulation.          |
| **Tornado chart** | Diagramme horizontal triant les variables par impact sur un KPI.     |
| **SaaS B2B**      | Software as a Service vendu à des entreprises.                       |
| **Streamlit**     | Framework Python pour apps web data‑driven.                          |
| **CDATA**         | Cached Data (Streamlit `@st.cache_data`).                            |

---

*Fin du document*

