# RecruitAI, Fiche de Préparation à la Présentation

Une page, ce que fait chaque fichier, et comment répondre aux questions
que vous allez probablement recevoir.

## Le pitch en 30 secondes

« RecruitAI est une plateforme de recrutement où chaque candidature est
notée automatiquement par rapport au poste, sur trois signaux : les
compétences, l'expérience, et la proximité entre le vocabulaire du CV et
la description du poste. Le recruteur voit ainsi une liste de candidats
classée avec une raison en langage clair, au lieu de lire chaque CV à la
main. »

## Ce que fait chaque fichier

**`backend/app.py`** — l'ensemble de l'API REST. Chaque clic dans le
navigateur appelle un de ces points d'accès : inscription/connexion,
publier une offre, lister les offres, postuler, mettre à jour le profil
d'un candidat, téléverser un CV/une photo, faire avancer quelqu'un dans le
pipeline de recrutement, notifications, supervision admin. Il sert aussi
les fichiers HTML/CSS/JS, donc un seul processus Python fait tourner toute
la plateforme.

**`backend/ai_matcher.py`** — le moteur de scoring. Prend un candidat et
une offre, renvoie un score de 0 à 100 plus une explication en langage
clair. Trois sous-scores sont combinés :
- **Similarité textuelle** : TF-IDF + similarité cosinus entre le texte du
  CV et la description du poste (c'est la partie "IA", c'est la même
  technique de base que les moteurs de recherche utilisent pour juger la
  pertinence d'un document par rapport à une requête).
- **Recoupement des compétences** : les compétences obligatoires comptent
  double, les compétences "appréciées" comptent une fois.
- **Adéquation de l'expérience** : compare les années d'expérience au
  minimum requis par le poste, en pénalisant à la fois la
  sous-qualification et la surqualification extrême.

**`backend/resume_parser.py`** — transforme un fichier PDF/DOCX/TXT
téléversé en texte brut, pour qu'il puisse être analysé par le moteur
ci-dessus.

**`database/schema.sql`** — les tables SQL : utilisateurs, offres,
candidats, compétences, langues, candidatures, notifications, offres
sauvegardées. Tout est normalisé, par exemple les compétences vivent dans
leur propre table et sont liées aux offres et aux candidats par ID, sans
duplication de texte.

**`frontend/*.html` + `css/style.css` + `js/api.js`** — l'interface. Du
HTML/CSS/JS pur, sans framework, qui communique avec le backend via des
appels `fetch()`. `api.js` regroupe la logique partagée (le client API,
les notifications, la fenêtre d'aide) pour éviter la duplication de code
sur chaque page.

## Questions probables, et comment y répondre

**« Est-ce vraiment de l'IA, ou juste des conditions if ? »**
« C'est une véritable technique d'apprentissage automatique : la
vectorisation TF-IDF avec similarité cosinus. Ce n'est pas un grand modèle
de langage, mais c'est du vrai NLP (traitement du langage naturel), la
même famille de technique utilisée dans le classement de pertinence des
moteurs de recherche. Je l'ai choisie délibérément parce qu'elle
fonctionne entièrement hors ligne sans clé API, ce qui compte pour un
prototype autonome. »

**« Comment rendriez-vous l'IA plus intelligente ? »**
« En remplaçant TF-IDF par des embeddings de phrases
(`sentence-transformers`), qui comprennent le sens, pas seulement le
recoupement de mots. Le code est déjà structuré pour que ce soit un
remplacement direct dans une seule fonction, `text_similarity_score()`
dans `ai_matcher.py`. »

**« Est-ce prêt pour la production ? »**
« Non, et je peux dire exactement pourquoi : SQLite au lieu de Postgres,
pas de vrais jetons de session (le frontend fait confiance à
localStorage), pas de limitation du taux de requêtes. Ce sont les
prochaines étapes logiques, pas des lacunes que je cache. »

**« Quelle a été la partie la plus difficile à résoudre ? »**
« Rendre le score explicable, pas juste un chiffre. Les recruteurs ne
font pas confiance à une boîte noire, donc chaque score est accompagné
des compétences qui correspondent, de celles qui manquent, et d'une
phrase claire expliquant le verdict. »

**« Pourquoi trois signaux séparés plutôt qu'un seul score ? »**
« Parce qu'ils peuvent être en désaccord : quelqu'un peut avoir des
compétences parfaites mais aucune expérience, ou un excellent vocabulaire
de CV mais lui manquer une compétence obligatoire. Les séparer, c'est ce
qui rend le score défendable au lieu d'être arbitraire. »

**« Les recruteurs et les candidats voient-ils la même chose ? »**
« Oui, la transparence était un objectif de conception, pas une
réflexion après coup. Le candidat voit la même répartition de score que
le recruteur voit pour sa candidature. »

**« Et le champ des langues, cela affecte-t-il le score ? »**
« Pas encore, délibérément. J'ai ajouté le modèle de données et
l'interface pour cela, mais intégrer ça dans la formule de scoring la
veille d'une échéance était un risque que j'ai choisi de ne pas prendre.
C'est une prochaine étape claire et prête à être faite. »

## Si une démonstration plante en direct

Restez calme, dites ce que vous vérifieriez : « Dans un environnement
réel, je vérifierais l'erreur exacte dans le terminal Flask, là c'est
probablement juste une session de navigateur périmée. » Puis soit
rafraîchissez, soit basculez sur une description orale du flux, vous
comprenez ce système, un accroc d'interface ne change pas ça.
