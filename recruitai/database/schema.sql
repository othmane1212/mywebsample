-- =========================================================
-- RecruitAI - Intelligent Recruitment Platform
-- Database Schema (SQLite / adaptable to MySQL & PostgreSQL)
-- =========================================================

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------
-- USERS  (both recruiters and candidates authenticate here)
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name       TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    role            TEXT NOT NULL CHECK (role IN ('recruiter', 'candidate', 'admin')),
    company_name    TEXT,                          -- only used when role = recruiter
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------
-- CANDIDATE PROFILES
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS candidates (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER NOT NULL UNIQUE,
    headline         TEXT,                          -- e.g. "Backend Engineer, 5y"
    resume_text      TEXT,                          -- raw parsed resume text (used by AI matcher)
    experience_years REAL DEFAULT 0,
    education_level  TEXT,                          -- e.g. "Bachelor", "Master", "PhD"
    location         TEXT,
    remote_ok        BOOLEAN DEFAULT 0,
    profile_picture  TEXT,                          -- filename of uploaded photo, served from /photos/<file>
    subject          TEXT,                          -- matiere enseignee (e.g. "Mathematiques")
    teaching_level   TEXT,                          -- Primaire, College, Lycee
    passed_concours  BOOLEAN DEFAULT 0,              -- concours national de recrutement
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- SKILLS (normalized, many-to-many with jobs & candidates)
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS skills (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS candidate_skills (
    candidate_id  INTEGER NOT NULL,
    skill_id      INTEGER NOT NULL,
    proficiency   TEXT CHECK (proficiency IN ('beginner','intermediate','advanced','expert')) DEFAULT 'intermediate',
    PRIMARY KEY (candidate_id, skill_id),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- JOBS
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS jobs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    recruiter_id    INTEGER NOT NULL,
    title           TEXT NOT NULL,
    description     TEXT NOT NULL,
    requirements    TEXT NOT NULL,                 -- free text, fed into AI matcher
    location        TEXT,
    employment_type TEXT CHECK (employment_type IN ('full-time','part-time','contract','internship')) DEFAULT 'full-time',
    min_experience  REAL DEFAULT 0,
    status          TEXT CHECK (status IN ('open','closed','draft')) DEFAULT 'open',
    subject             TEXT,                       -- matiere enseignee requise
    teaching_level      TEXT,                        -- Primaire, College, Lycee
    contract_type       TEXT CHECK (contract_type IN ('titulaire','contractuel')) DEFAULT 'contractuel',
    region              TEXT,                        -- region administrative marocaine
    application_deadline DATE,                        -- date limite de candidature
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recruiter_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS job_skills (
    job_id       INTEGER NOT NULL,
    skill_id     INTEGER NOT NULL,
    is_required  BOOLEAN DEFAULT 1,                -- required vs "nice to have"
    PRIMARY KEY (job_id, skill_id),
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- APPLICATIONS  (candidate <-> job, scored by the AI engine)
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS applications (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id           INTEGER NOT NULL,
    candidate_id     INTEGER NOT NULL,
    match_score      REAL DEFAULT 0,                -- 0-100, produced by ai_matcher.py
    skill_overlap    REAL DEFAULT 0,                -- 0-100
    text_similarity  REAL DEFAULT 0,                -- 0-100 (TF-IDF cosine, resume wording vs job text)
    language_match   REAL DEFAULT 0,                -- 0-100 (spoken languages vs job's required languages)
    ai_summary       TEXT,                          -- short AI-generated explanation of the score
    status           TEXT CHECK (status IN ('applied','shortlisted','interview','rejected','hired')) DEFAULT 'applied',
    applied_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (job_id, candidate_id),
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- Helpful indexes for the matching engine & dashboards
-- ---------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_applications_job     ON applications(job_id);
CREATE INDEX IF NOT EXISTS idx_applications_score    ON applications(match_score DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_status           ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_candidate_skills      ON candidate_skills(skill_id);

-- ---------------------------------------------------------
-- SAVED JOBS (candidates bookmarking a job without applying)
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS saved_jobs (
    candidate_id  INTEGER NOT NULL,
    job_id        INTEGER NOT NULL,
    saved_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (candidate_id, job_id),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- NOTIFICATIONS (in-app, per user)
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS notifications (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    message     TEXT NOT NULL,
    link        TEXT,                              -- which page to open, e.g. candidate.html
    is_read     BOOLEAN DEFAULT 0,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, is_read);

-- ---------------------------------------------------------
-- LANGUAGES (spoken by candidates, needed for jobs)
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS candidate_languages (
    candidate_id  INTEGER NOT NULL,
    language      TEXT NOT NULL,
    level         TEXT CHECK (level IN ('basic','conversational','fluent','native')) DEFAULT 'conversational',
    PRIMARY KEY (candidate_id, language),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS job_languages (
    job_id        INTEGER NOT NULL,
    language      TEXT NOT NULL,
    level         TEXT CHECK (level IN ('basic','conversational','fluent','native')) DEFAULT 'conversational',
    PRIMARY KEY (job_id, language),
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- Seed data (a couple of skills so the demo isn't empty)
-- ---------------------------------------------------------
INSERT OR IGNORE INTO skills (name) VALUES
 ('Pédagogie'), ('Gestion de classe'), ('Préparation de cours'),
 ('Évaluation des élèves'), ('Mathématiques'), ('Français'),
 ('Physique-Chimie'), ('Sciences de la Vie et de la Terre'),
 ('Communication'), ('Travail en équipe'), ('Numérique éducatif'), ('Arabe');
