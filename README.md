# Pack 3 • Prévisions & Accompagnement — Demo Repo

&#x20;&#x20;

> Prototype interactif destiné à démontrer le **Pack 3** : modélisation financière tri‑scénario (SaaS B2B), interface Streamlit et export Excel/CSV.
>
> 📅 *Mis à jour : 4 août 2025*

---

## Sommaire

1. [Fonctionnalités](#fonctionnalités)
2. [Architecture du projet](#architecture)
3. [Installation rapide](#installation)
4. [Usage](#usage)
5. [Tests](#tests)
6. [Déploiement Docker](#docker)
7. [Roadmap](#roadmap)
8. [Contribuer](#contribuer)
9. [Licence](#licence)

---



## 1. Fonctionnalités ⭐

- **Moteur de prévision** 3 états (P&L, BS, CF) sur 12‑60 mois.
- **Trois scénarios** pré‑paramétrés (Base, Pessimiste, Ambitieux) + sliders pour custom.
- **KPIs clés** : ARR M12, runway, EBITDA M1.
- **Graphiques Plotly** : Cash, Revenue, EBITDA.
- **Export** CSV & Excel (meta incluse).
- **Tests Pytest** (100 % lignes moteur).



## 2. Architecture du projet 🏗

```
├── app/
│   └── main.py         # Interface Streamlit
├── model/
│   ├── __init__.py
│   └── forecast.py     # simulate(), Scenario
├── tests/
│   └── test_forecast.py
├── requirements.txt    # Dépendances runtime/dev
├── Dockerfile          # Image prod‑ready
└── README.md           # Ce fichier
```



## 3. Installation rapide ⚡

```bash
# 1. Clone
git clone https://github.com/your‑org/offre‑pack‑3.git
cd offre‑pack‑3

# 2. Environnement Python 3.12
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Dépendances
pip install -r requirements.txt
```



## 4. Usage 🖥️

```bash
streamlit run app/main.py
# Ouvre http://localhost:8501
```

1. Choisissez un scénario dans la sidebar ou ajustez les sliders.
2. Consultez les KPIs & graphiques.
3. Téléchargez le CSV ou l’Excel généré.



## 5. Lancer les tests 🧪

```bash
pytest -q   # doit afficher 4 passed
```



## 6. Build & run Docker 🐳

```bash
docker build -t pack3-demo .
docker run -p 8501:8501 pack3-demo
# Streamlit dispo sur http://localhost:8501
```



## 7. Roadmap 🛣️

La feuille de route ci‑dessous décrit les prochaines évolutions prévues pour transformer cette démo en véritable produit Pack 3.  *(☐ = à faire / ✔️ = terminé)*

| ⚑  | Lot                 | Tâches détaillées                                                                                     | Charge | Statut |
| -- | ------------------- | ----------------------------------------------------------------------------------------------------- | ------ | ------ |
| 🔵 | **UX**              | • Dark mode avec `st.theme`• Logo/charte client (config YAML)• I18N FR/EN via `session_state['lang']` | 0.5 j  | ☐      |
| 🔵 | **Analyse**         | • Tornado chart (sensibilité EBITDA)• Table « What‑If » ±5 % drivers                                  | 0.5 j  | ☐      |
| 🟡 | **API**             | • FastAPI `/simulate` (JSON ↔ DataFrame)• Doc OpenAPI + tests d’intégration                           | 1 j    | ☐      |
| 🟡 | **Données réelles** | • Connexion BigQuery (Pack 2)• Comparatif *budget vs actual* dans Streamlit                           | 1 j    | ☐      |
| 🟢 | **CI/CD**           | • Docker (<300 MB)• Pipeline Render.com auto‑deploy• Badge *Live Demo*                                | 0.5 j  | ✔️     |
| 🟢 | **Sécurité**        | • Basic Auth Render• Dependabot + `pip‑audit`                                                         | 0.25 j | ✔️     |

*Charge restante estimée : ****≈ 3 jours****.*



## 8. Contribuer 🤝. Contribuer 🤝

1. Ouvrez une *issue* pour discuter d’une feature ou d’un bug.
2. Fork → branche `feature/x` → PR.
3. La CI doit passer (`pytest`).



## 9. Licence 📑

MIT © 2025 — Feel free to fork, adapt and credit.

