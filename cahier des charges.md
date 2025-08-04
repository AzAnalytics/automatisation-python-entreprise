# Cahier des charges — Pack 3 « Prévisions & Accompagnement »

> **Version 1.0 — 4 août 2025**

---

## 1. Contexte et objectifs
- **Contexte** : Les prospects ont besoin d’anticiper leur trésorerie et de convaincre leurs investisseurs. Le Pack 3 fournit un outil de prévision financier + un accompagnement régulier.
- **Objectifs** :
  1. Fournir une maquette fonctionnelle pour démontrer la valeur du Pack 3.
  2. Mettre en avant l’expertise modélisation + support mensuel.
  3. Créer une base réutilisable/vendable dès qu’un prospect signe.

## 2. Portée fonctionnelle
| Domaine                | Fonctionnalités livrées                                                                                 | Hors scope / option            |
|------------------------|----------------------------------------------------------------------------------------------------------|--------------------------------|
| **Modélisation**       | MRR → CA → P&L 3 états, cash-flow, runway, 3 scénarios (Base/Pessimiste/Ambitieux)                       | Gestion de dettes/capex (option) |
| **Paramétrage**        | Sliders & inputs pour modifier hypothèses (growth, churn, COGS, Opex, MRR₀, cash₀, durée)               | I18N multidevise (option)      |
| **Visualisation**      | KPIs (ARR M12, runway, EBITDA), graphiques interactifs, tableau détaillé                                | Tornado chart (option)         |
| **Export**             | CSV + Excel (métadonnées)                                                                                | PDF auto / deck PPT (option)   |
| **Accompagnement**     | Manuel utilisateur (PDF 5p) + vidéo 3 min + plan de suivi mensuel fictif                                | Support Slack temps‑réel       |
| **Déploiement**        | Exécution locale Streamlit, Dockerfile prêt pour Render.com                                             | Hébergement SaaS prod          |

## 3. Livrables
1. **Prototype interactif** (Streamlit) avec 3 scénarios + exports.
2. **Fichier Excel démonstration** généré depuis l’interface.
3. **Documentation utilisateur** (PDF) & **documentation technique** (séparée).
4. **Cahier des charges** (ce document).

## 4. Planning prévisionnel
| Phase                     | Tâches clés                               | Durée | Délai (J) |
|---------------------------|-------------------------------------------|-------|-----------|
| Analyse & cadrage         | Validation périmètre + KPI               | 0,5j  | J+0,5     |
| Dév. moteur & tests       | `forecast.py` + Pytest                   | 1j    | J+1,5     |
| Dév. interface Streamlit  | UI, KPIs, charts, exports                | 1j    | J+2,5     |
| Documentation & QA        | Docs, vidéo, revue code                  | 0,5j  | J+3       |

## 5. Critères d’acceptation
- Tous les tests Pytest passent en CI GitHub Actions.
- KPI “ARR M12” ≈ 600 k€ dans scénario Base (hypothèses par défaut).
- Export Excel téléchargeable ≤ 2 s.
- Docker image < 300 MB et démarre en ≤ 10 s.

## 6. Gouvernance & rôles
| Rôle              | Responsabilités                         |
|-------------------|-----------------------------------------|
| Chef de projet    | Suivi planning, validation livrables    |
| Dev principal     | Code moteur, UI, tests                  |
| Designer (option) | UI/UX, charte graphique                 |
| Relecteur finance | Vérif logique prévisionnelle            |

## 7. Risques & mitigations
| Risque                 | Impact | Mitigation                              |
|------------------------|--------|-----------------------------------------|
| Mauvaise adoption UI   | Moyen  | Tests utilisateurs + ajustements sliders|
| Dépendances non gelées | Faible | `requirements.txt` + Dependabot        |
| Métriques incohérentes | Haut   | Validation CFO interne + tests calcul   |

## 8. Budget indicatif
| Poste       | Jours | TJM (€) | Total (€)      |
|-------------|-------|---------|----------------|
| Développement & tests | 2   | 600     | 1200           |
| Documentation         | 0,5 | 600     | 300            |
| Gestion de projet     | 0,5 | 600     | 300            |
| **Total**             | **3** |         | **1 800 € HT** |

---

*Fin du cahier des charges*

