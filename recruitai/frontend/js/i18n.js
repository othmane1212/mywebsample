/* RecruitAI — internationalisation (EN / FR) */

const TRANSLATIONS = {
  en: {
    // nav / shared
    "nav.how": "How it works",
    "nav.about": "About",
    "nav.flow": "The AI, step by step",
    "nav.login": "Log in",
    "nav.getStarted": "Get started",
    "nav.createAccount": "Create account",
    "nav.dashboard": "Go to dashboard",
    "common.signedInAs": "Signed in as",
    "common.logout": "Log out",
    "common.settings": "Settings",
    "common.loading": "Loading…",
    "common.save": "Save",
    "common.apply": "Apply",
    "common.applied": "Applied",
    "common.back": "Back to dashboard",

    // landing
    "landing.eyebrow": "Intelligent recruitment, not another inbox",
    "landing.h1a": "Stop reading resumes.",
    "landing.h1b": "Start meeting candidates.",
    "landing.lede": "You posted the job. Now you have 347 applications sitting in your inbox. RecruitAI reads them for you, compares each candidate with what the role actually needs, and puts the strongest matches at the top.",
    "landing.postJob": "Post a job",
    "landing.findRole": "Find a role",
    "landing.flowKicker": "From application to answer",
    "landing.flowTitle": "What actually happens the moment someone applies",
    "landing.flow1Title": "Application comes in",
    "landing.flow1Text": "Resume text, skills, experience, and languages, all saved to the candidate's profile.",
    "landing.flow2Title": "AI reads both sides",
    "landing.flow2Text": "Resume language is compared against the job description and requirements directly.",
    "landing.flow3Title": "Three signals combine",
    "landing.flow3Text": "Skills overlap, experience fit, and language similarity, weighted and merged into one score.",
    "landing.flow4Title": "Recruiter sees the why",
    "landing.flow4Text": "Ranked instantly, with a plain-language reason attached, not just a number.",
    "landing.ctaTitle": "Spend less time finding candidates. Spend more time talking to them.",
    "landing.startRecruiting": "Start recruiting",
    "landing.findNextRole": "Find your next role",

    // auth
    "auth.welcomeBack": "Welcome back",
    "auth.loginSub": "Log in to your RecruitAI account.",
    "auth.email": "Email",
    "auth.password": "Password",
    "auth.newHere": "New here?",
    "auth.createTitle": "Create your account",
    "auth.createSub": "Tell us which side of the table you're on.",
    "auth.hiring": "I'm hiring",
    "auth.jobHunting": "I'm job hunting",
    "auth.fullName": "Full name",
    "auth.companyName": "Company name",
    "auth.alreadyHave": "Already have an account?",

    // recruiter dashboard
    "rec.yourJobs": "Your jobs",
    "rec.yourJobsSub": "Every applicant is scored automatically the moment they apply.",
    "rec.postJob": "Post a job",
    "rec.postJobSub": "Mark the skills that are truly required, it changes how candidates are scored.",
    "rec.jobTitle": "Job title",
    "rec.location": "Location",
    "rec.minExp": "Minimum experience (years)",
    "rec.description": "Description",
    "rec.requirements": "Requirements",
    "rec.skills": "Skills (press Enter to add)",
    "rec.requiredSkills": "Which of those are required, not just nice-to-have? (press Enter to add)",
    "rec.languagesNeeded": "Languages needed",
    "rec.postJobBtn": "Post job",
    "rec.noJobs": "No jobs yet",
    "rec.noJobsText": "Post your first job and RecruitAI will start ranking candidates against it automatically.",
    "rec.noApplicants": "No applicants yet.",

    // candidate portal
    "cand.openRoles": "Open roles",
    "cand.openRolesSub": "Complete your profile first so RecruitAI can score how well you fit each role.",
    "cand.browseJobs": "Browse jobs",
    "cand.savedJobs": "Saved jobs",
    "cand.savedJobsSub": "Jobs you've bookmarked to come back to later.",
    "cand.yourProfile": "Your profile",
    "cand.yourProfileSub": "This is what the AI matcher reads, the more specific, the better your match scores.",
    "cand.yourApplications": "Your applications",
    "cand.yourApplicationsSub": "Track status and see your match score for each role you've applied to.",
    "cand.headline": "Headline",
    "cand.yearsExp": "Years of experience",
    "cand.education": "Education level",
    "cand.uploadResume": "Upload your resume (PDF, DOCX, or TXT)",
    "cand.resumeText": "Resume text",
    "cand.skills": "Skills (press Enter to add)",
    "cand.languages": "Languages you speak",
    "cand.saveProfile": "Save profile",
    "cand.uploadPhoto": "Upload profile picture",
    "cand.searchPlaceholder": "Search by title or location…",
    "cand.filterAll": "All",
    "cand.saveForLater": "Save for later",
    "cand.saved": "Saved",
    "cand.noSaved": "No saved jobs yet",
    "cand.noSavedText": "Bookmark a job from \"Browse jobs\" to see it here.",
    "cand.noApps": "No applications yet",
    "cand.noAppsText": "Browse open roles and apply, your match score appears here once RecruitAI scores it.",
    "cand.noMatching": "No matching roles",
    "cand.noMatchingText": "Try a different search or filter.",

    // admin
    "admin.overview": "Platform overview",
    "admin.overviewSub": "Global visibility across every recruiter and candidate on RecruitAI.",
    "admin.allJobs": "All jobs",
    "admin.allJobsSub": "Every job posted on the platform, across every recruiter.",
    "admin.allUsers": "All users",
    "admin.allUsersSub": "Every recruiter and candidate account on RecruitAI.",
    "admin.recruiters": "Recruiters",
    "admin.candidates": "Candidates",
    "admin.openJobs": "Open jobs",
    "admin.applications": "Applications",
    "admin.remove": "Remove",

    // settings
    "set.title": "Settings",
    "set.sub": "Your account and how the platform works.",
    "set.account": "Account",
    "set.name": "Name",
    "set.role": "Role",
    "set.language": "Language",
    "set.languageSub": "Choose the interface language. Applies everywhere, including the homepage.",
    "set.notifications": "Notifications",
    "set.notificationsText": "You'll get a notification whenever your application status changes (candidates) or someone applies to your job (recruiters). Check the bell icon on your dashboard.",

    // levels / statuses
    "level.basic": "Basic",
    "level.conversational": "Conversational",
    "level.fluent": "Fluent",
    "level.native": "Native",
    "status.applied": "applied",
    "status.shortlisted": "shortlisted",
    "status.interview": "interview",
    "status.hired": "hired",
    "status.rejected": "rejected",
    "notif.empty": "No notifications yet.",
    "help.title": "Quick help",
    "help.gotIt": "Got it",
  },

  fr: {
    // nav / shared
    "nav.how": "Comment ça marche",
    "nav.about": "À propos",
    "nav.flow": "L'IA, étape par étape",
    "nav.login": "Connexion",
    "nav.getStarted": "Commencer",
    "nav.createAccount": "Créer un compte",
    "nav.dashboard": "Tableau de bord",
    "common.signedInAs": "Connecté en tant que",
    "common.logout": "Déconnexion",
    "common.settings": "Paramètres",
    "common.loading": "Chargement…",
    "common.save": "Enregistrer",
    "common.apply": "Postuler",
    "common.applied": "Candidature envoyée",
    "common.back": "Retour au tableau de bord",

    // landing
    "landing.eyebrow": "Recrutement intelligent, pas une boîte mail de plus",
    "landing.h1a": "Arrêtez de lire des CV.",
    "landing.h1b": "Commencez à rencontrer des candidats.",
    "landing.lede": "Vous avez publié l'offre. Vous avez maintenant 347 candidatures dans votre boîte mail. RecruitAI les lit pour vous, compare chaque candidat aux besoins réels du poste, et place les meilleurs profils en haut de la liste.",
    "landing.postJob": "Publier une offre",
    "landing.findRole": "Trouver un poste",
    "landing.flowKicker": "De la candidature à la réponse",
    "landing.flowTitle": "Ce qui se passe réellement au moment où quelqu'un postule",
    "landing.flow1Title": "La candidature arrive",
    "landing.flow1Text": "Texte du CV, compétences, expérience et langues, tout est enregistré dans le profil du candidat.",
    "landing.flow2Title": "L'IA lit les deux côtés",
    "landing.flow2Text": "Le vocabulaire du CV est comparé directement à la description et aux exigences du poste.",
    "landing.flow3Title": "Trois signaux se combinent",
    "landing.flow3Text": "Recoupement des compétences, adéquation de l'expérience et similarité du vocabulaire, pondérés en un seul score.",
    "landing.flow4Title": "Le recruteur voit le pourquoi",
    "landing.flow4Text": "Classement instantané, avec une explication en langage clair, pas seulement un chiffre.",
    "landing.ctaTitle": "Passez moins de temps à chercher des candidats. Passez plus de temps à leur parler.",
    "landing.startRecruiting": "Commencer à recruter",
    "landing.findNextRole": "Trouver votre prochain poste",

    // auth
    "auth.welcomeBack": "Bon retour",
    "auth.loginSub": "Connectez-vous à votre compte RecruitAI.",
    "auth.email": "E-mail",
    "auth.password": "Mot de passe",
    "auth.newHere": "Nouveau ici ?",
    "auth.createTitle": "Créez votre compte",
    "auth.createSub": "Dites-nous de quel côté de la table vous êtes.",
    "auth.hiring": "Je recrute",
    "auth.jobHunting": "Je cherche un emploi",
    "auth.fullName": "Nom complet",
    "auth.companyName": "Nom de l'entreprise",
    "auth.alreadyHave": "Vous avez déjà un compte ?",

    // recruiter dashboard
    "rec.yourJobs": "Vos offres",
    "rec.yourJobsSub": "Chaque candidat est noté automatiquement dès qu'il postule.",
    "rec.postJob": "Publier une offre",
    "rec.postJobSub": "Indiquez les compétences réellement obligatoires, cela change la façon dont les candidats sont notés.",
    "rec.jobTitle": "Intitulé du poste",
    "rec.location": "Lieu",
    "rec.minExp": "Expérience minimum (années)",
    "rec.description": "Description",
    "rec.requirements": "Exigences",
    "rec.skills": "Compétences (appuyez sur Entrée pour ajouter)",
    "rec.requiredSkills": "Lesquelles sont obligatoires, et non simplement appréciées ? (Entrée pour ajouter)",
    "rec.languagesNeeded": "Langues requises",
    "rec.postJobBtn": "Publier l'offre",
    "rec.noJobs": "Aucune offre pour l'instant",
    "rec.noJobsText": "Publiez votre première offre et RecruitAI commencera automatiquement à classer les candidats.",
    "rec.noApplicants": "Aucun candidat pour l'instant.",

    // candidate portal
    "cand.openRoles": "Postes ouverts",
    "cand.openRolesSub": "Complétez d'abord votre profil pour que RecruitAI puisse évaluer votre adéquation à chaque poste.",
    "cand.browseJobs": "Parcourir les offres",
    "cand.savedJobs": "Offres sauvegardées",
    "cand.savedJobsSub": "Les offres que vous avez mises de côté pour y revenir plus tard.",
    "cand.yourProfile": "Votre profil",
    "cand.yourProfileSub": "C'est ce que lit le moteur de matching, plus c'est précis, meilleurs seront vos scores.",
    "cand.yourApplications": "Vos candidatures",
    "cand.yourApplicationsSub": "Suivez le statut et consultez votre score pour chaque poste auquel vous avez postulé.",
    "cand.headline": "Titre professionnel",
    "cand.yearsExp": "Années d'expérience",
    "cand.education": "Niveau d'études",
    "cand.uploadResume": "Téléversez votre CV (PDF, DOCX ou TXT)",
    "cand.resumeText": "Texte du CV",
    "cand.skills": "Compétences (appuyez sur Entrée pour ajouter)",
    "cand.languages": "Langues que vous parlez",
    "cand.saveProfile": "Enregistrer le profil",
    "cand.uploadPhoto": "Téléverser une photo de profil",
    "cand.searchPlaceholder": "Rechercher par intitulé ou lieu…",
    "cand.filterAll": "Toutes",
    "cand.saveForLater": "Sauvegarder",
    "cand.saved": "Sauvegardée",
    "cand.noSaved": "Aucune offre sauvegardée",
    "cand.noSavedText": "Sauvegardez une offre depuis « Parcourir les offres » pour la retrouver ici.",
    "cand.noApps": "Aucune candidature pour l'instant",
    "cand.noAppsText": "Parcourez les postes ouverts et postulez, votre score apparaîtra ici une fois calculé.",
    "cand.noMatching": "Aucun poste correspondant",
    "cand.noMatchingText": "Essayez une autre recherche ou un autre filtre.",

    // admin
    "admin.overview": "Vue d'ensemble de la plateforme",
    "admin.overviewSub": "Visibilité globale sur tous les recruteurs et candidats de RecruitAI.",
    "admin.allJobs": "Toutes les offres",
    "admin.allJobsSub": "Toutes les offres publiées sur la plateforme, tous recruteurs confondus.",
    "admin.allUsers": "Tous les utilisateurs",
    "admin.allUsersSub": "Tous les comptes recruteurs et candidats de RecruitAI.",
    "admin.recruiters": "Recruteurs",
    "admin.candidates": "Candidats",
    "admin.openJobs": "Offres ouvertes",
    "admin.applications": "Candidatures",
    "admin.remove": "Supprimer",

    // settings
    "set.title": "Paramètres",
    "set.sub": "Votre compte et le fonctionnement de la plateforme.",
    "set.account": "Compte",
    "set.name": "Nom",
    "set.role": "Rôle",
    "set.language": "Langue",
    "set.languageSub": "Choisissez la langue de l'interface. S'applique partout, y compris la page d'accueil.",
    "set.notifications": "Notifications",
    "set.notificationsText": "Vous recevrez une notification dès que le statut de votre candidature change (candidats) ou que quelqu'un postule à votre offre (recruteurs). Consultez l'icône cloche sur votre tableau de bord.",

    // levels / statuses
    "level.basic": "Notions",
    "level.conversational": "Conversationnel",
    "level.fluent": "Courant",
    "level.native": "Langue maternelle",
    "status.applied": "candidature",
    "status.shortlisted": "présélectionné",
    "status.interview": "entretien",
    "status.hired": "embauché",
    "status.rejected": "refusé",
    "notif.empty": "Aucune notification pour l'instant.",
    "help.title": "Aide rapide",
    "help.gotIt": "Compris",
  },
};

const I18n = {
  get() {
    return localStorage.getItem("recruitai_lang") || "en";
  },
  set(lang) {
    localStorage.setItem("recruitai_lang", lang);
    document.documentElement.setAttribute("lang", lang);
    I18n.apply();
  },
  /** Translate a key; falls back to English, then to the key itself. */
  t(key) {
    const lang = I18n.get();
    return (TRANSLATIONS[lang] && TRANSLATIONS[lang][key])
      || TRANSLATIONS.en[key]
      || key;
  },
  /** Replace text/placeholders on every element carrying a data-i18n attribute. */
  apply() {
    document.querySelectorAll("[data-i18n]").forEach(el => {
      el.textContent = I18n.t(el.getAttribute("data-i18n"));
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
      el.placeholder = I18n.t(el.getAttribute("data-i18n-placeholder"));
    });
    document.documentElement.setAttribute("lang", I18n.get());
  },
};

document.addEventListener("DOMContentLoaded", () => I18n.apply());
