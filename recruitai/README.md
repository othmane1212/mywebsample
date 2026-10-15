# RecruitAI, Plateforme de Recrutement Intelligente

Un prototype complet : base de données SQL, frontend HTML/CSS/JS, backend
Python/Flask, et un moteur de matching IA local, conçu pour être démontré
de bout en bout.

## Architecture

```
┌──────────────────────┐      HTTP/JSON      ┌───────────────────────┐
│   Frontend             │  ───────────────▶  │   Backend (Flask)      │
│   HTML / CSS / JS       │  ◀───────────────  │   app.py                │
│   (servi par Flask)     │                    │                         │
└──────────────────────┘                    │  ┌───────────────────┐  │
                                              │  │ ai_matcher.py      │  │
                                              │  │ TF-IDF + score de  │  │
                                              │  │ compétences        │  │
                                              │  └───────────────────┘  │
                                              │  ┌───────────────────┐  │
                                              │  │ resume_parser.py   │  │
                                              │  │ PDF/DOCX/TXT →texte│  │
                                              │  └───────────────────┘  │
                                              └──────────┬──────────────┘
                                                          │ SQL
                                                 ┌────────▼────────┐
                                                 │  Base SQLite       │
                                                 │  schema.sql         │
                                                 └────────────────────┘
```

## Ce qui rend la plateforme "intelligente"

`backend/ai_matcher.py` évalue chaque candidat par rapport à chaque offre
en utilisant trois signaux, combinés en un seul score explicable :

1. **Similarité textuelle** : vectorisation TF-IDF + similarité cosinus
   entre le texte du CV et la description/les exigences du poste (via
   scikit-learn, avec une solution de repli sans dépendance si sklearn
   n'est pas installé).
2. **Recoupement des compétences** : comparaison structurée des
   compétences du candidat avec celles requises par le poste, les
   compétences obligatoires pesant deux fois plus que les compétences
   "appréciées".
3. **Adéquation de l'expérience** : années d'expérience comparées au
   minimum requis par le poste, avec des pénalités progressives en cas de
   sous-qualification ou de surqualification extrême.

Ces trois signaux sont combinés en un score unique de 0 à 100, accompagné
d'un `ai_summary` en langage clair expliquant *pourquoi* ("Correspond sur :
python, sql. Compétences requises manquantes : docker.").

Les langues (parlées par les candidats, requises pour les postes) sont
saisies et affichées partout dans la plateforme, mais ne sont pas encore
intégrées dans la formule du score, il s'agit d'un choix de périmètre
délibéré, pas d'un oubli, voir les Limites ci-dessous.

**Pour passer à un vrai LLM** (par exemple pour des explications plus
riches), `ai_matcher.py` contient déjà une fonction `call_llm_explainer()`
qui appelle l'API Anthropic si `ANTHROPIC_API_KEY` est définie, il suffit
de la substituer à `generate_ai_summary()` dans `compute_match()`.

## Lancer le projet

```bash
cd backend
pip install flask scikit-learn PyPDF2 python-docx

python app.py
```

Puis ouvrir **http://localhost:5000**, Flask sert à la fois le frontend et
l'API depuis la même origine.

La base SQLite est créée automatiquement dans `database/recruitai.db` au
premier lancement, avec une liste de compétences de départ et un compte
administrateur intégré.

## Script de démonstration

1. **S'inscrire comme recruteur** → publier une offre (titre, description,
   exigences, compétences avec obligatoires/appréciées distinguées, et les
   langues nécessaires le cas échéant).
2. **S'inscrire comme candidat** (onglet privé/navigation privée) →
   téléverser un CV (PDF/DOCX/TXT) ou coller le texte du CV, ajouter les
   compétences et les langues, enregistrer le profil (la candidature est
   bloquée jusqu'à ce qu'un CV et au moins une compétence soient
   enregistrés) → postuler à l'offre.
3. Retour sur le tableau de bord recruteur → le candidat affiche un
   **score de matching IA en direct** avec une répartition
   compétences/expérience/langue et une explication en langage clair.
   Faire avancer le candidat dans le pipeline de recrutement (Candidature
   → Présélectionné → Entretien → Embauché/Refusé), le candidat est
   notifié automatiquement.
4. Vérifier l'**icône de notification** sur l'un des deux tableaux de
   bord, les recruteurs sont notifiés des nouvelles candidatures, les
   candidats sont notifiés des changements de statut.
5. Se connecter avec le compte administrateur intégré
   (`admin@recruitai.local` / `admin123`) pour voir la vue d'ensemble de
   la plateforme : tous les utilisateurs, toutes les offres, avec la
   possibilité de supprimer l'un ou l'autre.

## Project structure

```
recruitai/
├── backend/
│   ├── app.py              Flask REST API + static file serving
│   ├── ai_matcher.py        AI matching engine (TF-IDF, skills, experience)
│   └── resume_parser.py     Extracts text from uploaded PDF/DOCX/TXT resumes
├── database/
│   └── schema.sql           Full SQL schema (users, jobs, candidates, skills,
│                             languages, applications, notifications, saved jobs)
├── frontend/
│   ├── index.html           Landing page
│   ├── about.html           WIFM + the AI's role, explained
│   ├── login.html / register.html
│   ├── dashboard.html       Recruiter: post jobs, AI-ranked applicants, pipeline
│   ├── candidate.html       Candidate: profile, browse/save/apply, track status
│   ├── admin.html           Platform-wide oversight (users, jobs)
│   ├── settings.html        Account info
│   ├── css/style.css
│   └── js/api.js            Shared API client, notifications, help modal
└── README.md
```

## Limites honnêtes (à mentionner si vous présentez ce projet)

- Les mots de passe sont correctement hachés avec `werkzeug.security`
  (et non un simple SHA-256 brut), mais il n'y a toujours pas de véritable
  système de jetons de session, le frontend fait simplement confiance à
  ce qui est stocké dans `localStorage`. Convient pour une démonstration,
  pas pour de la production.
- Le téléversement de CV prend en charge le PDF, le DOCX et le TXT. Les
  PDF scannés (images uniquement) n'extrairont aucun texte, car il n'y a
  pas d'étape d'OCR.
- Le matching par TF-IDF se fait au niveau des mots-clés/expressions, pas
  une compréhension sémantique profonde. Passer à des embeddings de
  phrases (`sentence-transformers`) améliorerait la qualité du matching au
  prix d'une dépendance plus lourde.
- Les langues sont enregistrées et affichées, mais pas encore prises en
  compte dans le score : un candidat auquel manque une langue requise
  n'est actuellement pas pénalisé dans `match_score`. Ce choix a été fait
  délibérément pour éviter de déstabiliser la formule de scoring juste
  avant une échéance, ce n'est pas une fonctionnalité manquante par
  oubli.
- Une base SQLite mono-serveur convient pour une démonstration ; un
  déploiement réel passerait à PostgreSQL et ajouterait une véritable
  couche d'authentification (JWT), conformément à l'architecture
  d'origine dont ce projet est issu.
