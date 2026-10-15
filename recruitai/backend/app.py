"""
RecruitAI - Backend API (Flask)
=================================
Run with:  python app.py
Serves the REST API on http://localhost:5000 and the frontend (static files)
from ../frontend so the whole platform runs from a single command.
"""

import os
import sqlite3
import csv
import io
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, jsonify, g, send_from_directory

try:
    from flask_cors import CORS
    HAS_CORS = True
except ImportError:
    HAS_CORS = False  # fine for this project: frontend is served BY this same Flask app,
                       # so no cross-origin requests happen. Install flask-cors only if you
                       # split the frontend onto its own dev server/port.

import ai_matcher
import resume_parser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "database", "recruitai.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "..", "database", "schema.sql")
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
UPLOADS_DIR = os.path.join(BASE_DIR, "..", "database", "resumes")
os.makedirs(UPLOADS_DIR, exist_ok=True)
PHOTOS_DIR = os.path.join(BASE_DIR, "..", "database", "photos")
os.makedirs(PHOTOS_DIR, exist_ok=True)
ALLOWED_PHOTO_EXT = {".jpg", ".jpeg", ".png", ".webp"}

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
if HAS_CORS:
    CORS(app)


# --------------------------- DB HELPERS ---------------------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    fresh = not os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()

    # Seed a default admin account on first run so the Admin role
    # (from the original architecture) has someone to log in as.
    admin_exists = conn.execute("SELECT id FROM users WHERE role = 'admin'").fetchone()
    if not admin_exists:
        conn.execute(
            "INSERT INTO users (full_name, email, password_hash, role) VALUES (?, ?, ?, 'admin')",
            ("Platform Admin", "admin@recruitai.local", generate_password_hash("admin123")),
        )
        conn.commit()

    conn.close()
    return fresh


def hash_password(pw: str) -> str:
    return generate_password_hash(pw)


def verify_password(pw: str, pw_hash: str) -> bool:
    return check_password_hash(pw_hash, pw)


def row_to_dict(row):
    return dict(row) if row else None


def get_or_create_skill(db, name):
    name = name.strip()
    row = db.execute("SELECT id FROM skills WHERE name = ?", (name,)).fetchone()
    if row:
        return row["id"]
    cur = db.execute("INSERT INTO skills (name) VALUES (?)", (name,))
    db.commit()
    return cur.lastrowid


# --------------------------- STATIC / FRONTEND ---------------------------

@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    full = os.path.join(FRONTEND_DIR, path)
    if os.path.exists(full):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")


# --------------------------- AUTH ---------------------------

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(force=True)
    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO users (full_name, email, password_hash, role, company_name) VALUES (?, ?, ?, ?, ?)",
            (data["full_name"], data["email"], hash_password(data["password"]),
             data["role"], data.get("company_name")),
        )
        db.commit()
        user_id = cur.lastrowid
        if data["role"] == "candidate":
            db.execute("INSERT INTO candidates (user_id) VALUES (?)", (user_id,))
            db.commit()
        return jsonify({"id": user_id, "message": "Account created"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already registered"}), 409


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE email = ?", (data["email"],)).fetchone()
    if not row or not verify_password(data["password"], row["password_hash"]):
        return jsonify({"error": "Invalid credentials"}), 401
    user = row_to_dict(row)
    user.pop("password_hash")
    if user["role"] == "candidate":
        cand = db.execute("SELECT id FROM candidates WHERE user_id = ?", (user["id"],)).fetchone()
        user["candidate_id"] = cand["id"] if cand else None
    return jsonify(user)


# --------------------------- JOBS ---------------------------

@app.route("/api/jobs", methods=["GET"])
def list_jobs():
    db = get_db()
    rows = db.execute(
        "SELECT j.*, u.full_name AS recruiter_name, u.company_name "
        "FROM jobs j JOIN users u ON u.id = j.recruiter_id "
        "WHERE j.status = 'open' AND (j.application_deadline IS NULL OR j.application_deadline >= date('now')) "
        "ORDER BY j.created_at DESC"
    ).fetchall()
    jobs = []
    for row in rows:
        job = row_to_dict(row)
        skills = db.execute(
            "SELECT s.name FROM job_skills js JOIN skills s ON s.id = js.skill_id WHERE js.job_id = ?",
            (job["id"],),
        ).fetchall()
        job["skills"] = [s["name"] for s in skills]
        langs = db.execute(
            "SELECT language, level FROM job_languages WHERE job_id = ?", (job["id"],)
        ).fetchall()
        job["languages"] = [{"name": r["language"], "level": r["level"]} for r in langs]
        jobs.append(job)
    return jsonify(jobs)


@app.route("/api/recruiters/<int:recruiter_id>/jobs", methods=["GET"])
def list_recruiter_jobs(recruiter_id):
    """All of a recruiter's own postings, including closed/expired ones,
    unlike /api/jobs which only shows what's currently open to candidates."""
    db = get_db()
    rows = db.execute(
        "SELECT j.*, u.full_name AS recruiter_name, u.company_name "
        "FROM jobs j JOIN users u ON u.id = j.recruiter_id "
        "WHERE j.recruiter_id = ? ORDER BY j.created_at DESC",
        (recruiter_id,),
    ).fetchall()
    jobs = []
    for row in rows:
        job = row_to_dict(row)
        skills = db.execute(
            "SELECT s.name FROM job_skills js JOIN skills s ON s.id = js.skill_id WHERE js.job_id = ?",
            (job["id"],),
        ).fetchall()
        job["skills"] = [s["name"] for s in skills]
        langs = db.execute(
            "SELECT language, level FROM job_languages WHERE job_id = ?", (job["id"],)
        ).fetchall()
        job["languages"] = [{"name": r["language"], "level": r["level"]} for r in langs]
        jobs.append(job)
    return jsonify(jobs)


@app.route("/api/jobs", methods=["POST"])
def create_job():
    data = request.get_json(force=True)
    db = get_db()
    cur = db.execute(
        "INSERT INTO jobs (recruiter_id, title, description, requirements, location, "
        "employment_type, min_experience, status, subject, teaching_level, contract_type, "
        "region, application_deadline) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, 'open', ?, ?, ?, ?, ?)",
        (data["recruiter_id"], data["title"], data["description"], data["requirements"],
         data.get("location", ""), data.get("employment_type", "full-time"),
         data.get("min_experience", 0),
         data.get("subject", ""), data.get("teaching_level", ""),
         data.get("contract_type", "contractuel"),
         data.get("region", ""), data.get("application_deadline") or None),
    )
    job_id = cur.lastrowid
    required = set(s.lower() for s in data.get("required_skills", []))
    for skill_name in data.get("skills", []):
        skill_id = get_or_create_skill(db, skill_name)
        db.execute(
            "INSERT OR IGNORE INTO job_skills (job_id, skill_id, is_required) VALUES (?, ?, ?)",
            (job_id, skill_id, 1 if skill_name.lower() in required else 0),
        )
    for lang in data.get("languages", []):
        db.execute(
            "INSERT OR IGNORE INTO job_languages (job_id, language, level) VALUES (?, ?, ?)",
            (job_id, lang["name"], lang.get("level", "conversational")),
        )
    db.commit()
    return jsonify({"id": job_id, "message": "Job posted"}), 201


@app.route("/api/jobs/<int:job_id>/candidates", methods=["GET"])
def ranked_candidates_for_job(job_id):
    """The core 'intelligent recruitment' endpoint: ranks every applicant
    (or, if ?pool=all, every candidate in the DB) against this job."""
    db = get_db()
    job_row = db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if not job_row:
        return jsonify({"error": "Job not found"}), 404
    job = row_to_dict(job_row)

    job_skills = db.execute(
        "SELECT s.name, js.is_required FROM job_skills js JOIN skills s ON s.id = js.skill_id WHERE js.job_id = ?",
        (job_id,),
    ).fetchall()
    job["skills"] = [r["name"] for r in job_skills]
    job["required_skills"] = [r["name"] for r in job_skills if r["is_required"]]
    job_langs = db.execute(
        "SELECT language, level FROM job_languages WHERE job_id = ?", (job_id,)
    ).fetchall()
    job["languages"] = [{"name": r["language"], "level": r["level"]} for r in job_langs]

    pool = request.args.get("pool", "applied")  # 'applied' or 'all'
    if pool == "all":
        cand_rows = db.execute(
            "SELECT c.*, u.full_name, u.email FROM candidates c JOIN users u ON u.id = c.user_id"
        ).fetchall()
    else:
        cand_rows = db.execute(
            "SELECT c.*, u.full_name, u.email, a.id AS application_id, a.status AS application_status "
            "FROM applications a "
            "JOIN candidates c ON c.id = a.candidate_id "
            "JOIN users u ON u.id = c.user_id WHERE a.job_id = ?",
            (job_id,),
        ).fetchall()

    candidates = []
    for row in cand_rows:
        c = row_to_dict(row)
        skills = db.execute(
            "SELECT s.name FROM candidate_skills cs JOIN skills s ON s.id = cs.skill_id WHERE cs.candidate_id = ?",
            (c["id"],),
        ).fetchall()
        c["skills"] = [s["name"] for s in skills]
        langs = db.execute(
            "SELECT language, level FROM candidate_languages WHERE candidate_id = ?", (c["id"],)
        ).fetchall()
        c["languages"] = [{"name": r["language"], "level": r["level"]} for r in langs]
        candidates.append(c)

    ranked = ai_matcher.rank_candidates(job, candidates)

    # persist scores if these are real applications
    if pool == "applied":
        for r in ranked:
            db.execute(
                "UPDATE applications SET match_score=?, skill_overlap=?, text_similarity=?, language_match=?, ai_summary=? "
                "WHERE job_id=? AND candidate_id=?",
                (r["match_score"], r["skill_overlap"], r["text_similarity"], r["language_match"], r["ai_summary"],
                 job_id, r["id"]),
            )
        db.commit()

    return jsonify(ranked)


@app.route("/api/jobs/<int:job_id>/candidates/export.csv", methods=["GET"])
def export_ranked_candidates_csv(job_id):
    """Lets a recruiter hand a printed/emailed ranked list to a hiring
    committee, matches what ranked_candidates_for_job returns."""
    resp = ranked_candidates_for_job(job_id)
    if isinstance(resp, tuple):
        return resp  # propagate a 404 etc.
    ranked = resp.get_json()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Nom", "Email", "Score", "Competences", "Experience",
        "Langues", "Matiere", "Statut", "Resume du score",
    ])
    for c in ranked:
        writer.writerow([
            c.get("full_name", ""),
            c.get("email", ""),
            c.get("match_score", ""),
            ", ".join(c.get("skills", [])),
            c.get("experience_years", ""),
            ", ".join(f"{l['name']} ({l['level']})" for l in c.get("languages", [])),
            c.get("subject", ""),
            c.get("application_status", ""),
            c.get("ai_summary", ""),
        ])
    csv_data = output.getvalue()
    return app.response_class(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=candidats_offre_{job_id}.csv"},
    )


# --------------------------- CANDIDATES ---------------------------

@app.route("/api/candidates/<int:user_id>/profile", methods=["GET"])
def get_candidate_profile(user_id):
    db = get_db()
    cand = db.execute("SELECT * FROM candidates WHERE user_id = ?", (user_id,)).fetchone()
    if not cand:
        return jsonify({"error": "Candidate not found"}), 404
    profile = row_to_dict(cand)
    skills = db.execute(
        "SELECT s.name FROM candidate_skills cs JOIN skills s ON s.id = cs.skill_id WHERE cs.candidate_id = ?",
        (cand["id"],),
    ).fetchall()
    profile["skills"] = [s["name"] for s in skills]
    langs = db.execute(
        "SELECT language, level FROM candidate_languages WHERE candidate_id = ?", (cand["id"],)
    ).fetchall()
    profile["languages"] = [{"name": r["language"], "level": r["level"]} for r in langs]
    return jsonify(profile)


@app.route("/api/candidates/<int:user_id>/profile", methods=["PUT"])
def update_candidate_profile(user_id):
    data = request.get_json(force=True)
    db = get_db()
    cand = db.execute("SELECT * FROM candidates WHERE user_id = ?", (user_id,)).fetchone()
    if not cand:
        return jsonify({"error": "Candidate not found"}), 404
    candidate_id = cand["id"]

    # Merge with existing values instead of overwriting, so saving one field
    # (e.g. skills) never silently wipes another (e.g. an uploaded resume).
    db.execute(
        "UPDATE candidates SET headline=?, resume_text=?, experience_years=?, education_level=?, "
        "location=?, remote_ok=?, subject=?, teaching_level=?, passed_concours=? WHERE id=?",
        (
            data.get("headline", cand["headline"]),
            data.get("resume_text", cand["resume_text"]),
            data.get("experience_years", cand["experience_years"]),
            data.get("education_level", cand["education_level"]),
            data.get("location", cand["location"]),
            1 if data.get("remote_ok", cand["remote_ok"]) else 0,
            data.get("subject", cand["subject"]),
            data.get("teaching_level", cand["teaching_level"]),
            1 if data.get("passed_concours", cand["passed_concours"]) else 0,
            candidate_id,
        ),
    )

    if "skills" in data:
        db.execute("DELETE FROM candidate_skills WHERE candidate_id = ?", (candidate_id,))
        for skill_name in data["skills"]:
            skill_id = get_or_create_skill(db, skill_name)
            db.execute(
                "INSERT OR IGNORE INTO candidate_skills (candidate_id, skill_id) VALUES (?, ?)",
                (candidate_id, skill_id),
            )
    if "languages" in data:
        db.execute("DELETE FROM candidate_languages WHERE candidate_id = ?", (candidate_id,))
        for lang in data["languages"]:
            db.execute(
                "INSERT OR IGNORE INTO candidate_languages (candidate_id, language, level) VALUES (?, ?, ?)",
                (candidate_id, lang["name"], lang.get("level", "conversational")),
            )
    db.commit()
    return jsonify({"message": "Profile updated"})


@app.route("/photos/<filename>")
def serve_photo(filename):
    return send_from_directory(PHOTOS_DIR, filename)


@app.route("/api/candidates/<int:user_id>/photo", methods=["POST"])
def upload_photo(user_id):
    if "photo" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["photo"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_PHOTO_EXT:
        return jsonify({"error": "Please upload a JPG, PNG, or WEBP image"}), 400

    db = get_db()
    cand = db.execute("SELECT id FROM candidates WHERE user_id = ?", (user_id,)).fetchone()
    if not cand:
        return jsonify({"error": "Candidate not found"}), 404

    filename = f"candidate_{cand['id']}{ext}"
    file.save(os.path.join(PHOTOS_DIR, filename))
    db.execute("UPDATE candidates SET profile_picture = ? WHERE id = ?", (filename, cand["id"]))
    db.commit()
    return jsonify({"message": "Photo uploaded", "photo_url": f"/photos/{filename}"})


@app.route("/api/candidates/<int:user_id>/resume", methods=["POST"])
def upload_resume(user_id):
    """Accepts a PDF/DOCX/TXT resume file, extracts its text, and saves it
    straight onto the candidate's profile so it feeds the AI matcher."""
    if "resume" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    if not resume_parser.is_allowed_resume_file(file.filename):
        return jsonify({"error": "Please upload a PDF, DOCX, or TXT file"}), 400

    db = get_db()
    cand = db.execute("SELECT id FROM candidates WHERE user_id = ?", (user_id,)).fetchone()
    if not cand:
        return jsonify({"error": "Candidate not found"}), 404

    ext = os.path.splitext(file.filename)[1].lower()
    saved_path = os.path.join(UPLOADS_DIR, f"candidate_{cand['id']}{ext}")
    file.save(saved_path)

    try:
        extracted_text = resume_parser.extract_text_from_resume(saved_path)
    except (ValueError, RuntimeError) as e:
        return jsonify({"error": str(e)}), 400

    if not extracted_text.strip():
        return jsonify({"error": "Couldn't read any text from that file. Try a different format or paste your resume text manually."}), 400

    db.execute(
        "UPDATE candidates SET resume_text = ? WHERE id = ?",
        (extracted_text, cand["id"]),
    )
    db.commit()
    return jsonify({"message": "Resume uploaded and processed", "resume_text": extracted_text})


@app.route("/api/apply", methods=["POST"])
def apply_to_job():
    data = request.get_json(force=True)
    db = get_db()

    # Enforce a complete profile before allowing an application, so the AI
    # matcher always has something real to score.
    cand = db.execute(
        "SELECT * FROM candidates WHERE id = ?", (data["candidate_id"],)
    ).fetchone()
    if not cand:
        return jsonify({"error": "Candidate not found"}), 404
    if not cand["resume_text"] or not cand["resume_text"].strip():
        return jsonify({"error": "Please complete your profile (resume and skills) before applying"}), 400

    skill_count = db.execute(
        "SELECT COUNT(*) AS n FROM candidate_skills WHERE candidate_id = ?", (data["candidate_id"],)
    ).fetchone()["n"]
    if skill_count == 0:
        return jsonify({"error": "Please add at least one skill to your profile before applying"}), 400

    # Teacher-recruitment gate: subject is disqualifying, not just a scoring
    # nudge, so it's enforced here rather than only affecting the AI score.
    job = db.execute("SELECT * FROM jobs WHERE id = ?", (data["job_id"],)).fetchone()
    if not job:
        return jsonify({"error": "Job not found"}), 404

    if job["subject"] and cand["subject"] and job["subject"].strip().lower() != cand["subject"].strip().lower():
        return jsonify({
            "error": f"This position is for {job['subject']}, your declared subject is {cand['subject']}. "
                     f"Update your profile's subject if this is a mistake."
        }), 400

    try:
        db.execute(
            "INSERT INTO applications (job_id, candidate_id) VALUES (?, ?)",
            (data["job_id"], data["candidate_id"]),
        )
        db.commit()

        # Notify the recruiter who owns this job that a new application came in.
        info = db.execute(
            "SELECT j.recruiter_id, j.title, u.full_name FROM jobs j "
            "JOIN candidates c ON c.id = ? JOIN users u ON u.id = c.user_id "
            "WHERE j.id = ?",
            (data["candidate_id"], data["job_id"]),
        ).fetchone()
        if info:
            create_notification(
                db, info["recruiter_id"],
                f"{info['full_name']} applied to \"{info['title']}\".",
                "dashboard.html",
            )

        return jsonify({"message": "Application submitted"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Already applied to this job"}), 409


@app.route("/api/candidates/<int:user_id>/applications", methods=["GET"])
def candidate_applications(user_id):
    db = get_db()
    cand = db.execute("SELECT id FROM candidates WHERE user_id = ?", (user_id,)).fetchone()
    if not cand:
        return jsonify([])
    rows = db.execute(
        "SELECT a.*, j.title, j.location FROM applications a JOIN jobs j ON j.id = a.job_id "
        "WHERE a.candidate_id = ? ORDER BY a.applied_at DESC",
        (cand["id"],),
    ).fetchall()
    return jsonify([row_to_dict(r) for r in rows])


def create_notification(db, user_id, message, link=None):
    db.execute(
        "INSERT INTO notifications (user_id, message, link) VALUES (?, ?, ?)",
        (user_id, message, link),
    )
    db.commit()


@app.route("/api/notifications/<int:user_id>", methods=["GET"])
def list_notifications(user_id):
    db = get_db()
    rows = db.execute(
        "SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 30",
        (user_id,),
    ).fetchall()
    unread = db.execute(
        "SELECT COUNT(*) AS n FROM notifications WHERE user_id = ? AND is_read = 0", (user_id,)
    ).fetchone()["n"]
    return jsonify({"notifications": [row_to_dict(r) for r in rows], "unread_count": unread})


@app.route("/api/notifications/<int:notification_id>/read", methods=["PATCH"])
def mark_notification_read(notification_id):
    db = get_db()
    db.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notification_id,))
    db.commit()
    return jsonify({"message": "Marked as read"})


@app.route("/api/notifications/<int:user_id>/read-all", methods=["PATCH"])
def mark_all_notifications_read(user_id):
    db = get_db()
    db.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
    db.commit()
    return jsonify({"message": "All marked as read"})


@app.route("/api/applications/<int:application_id>/status", methods=["PATCH"])
def update_application_status(application_id):
    """Moves a candidate through the hiring pipeline: applied, shortlisted,
    interview, hired, rejected."""
    data = request.get_json(force=True)
    new_status = data.get("status")
    valid = {"applied", "shortlisted", "interview", "rejected", "hired"}
    if new_status not in valid:
        return jsonify({"error": f"Status must be one of: {', '.join(sorted(valid))}"}), 400
    db = get_db()
    row = db.execute("SELECT id FROM applications WHERE id = ?", (application_id,)).fetchone()
    if not row:
        return jsonify({"error": "Application not found"}), 404
    db.execute("UPDATE applications SET status = ? WHERE id = ?", (new_status, application_id))
    db.commit()

    # Notify the candidate their status just moved.
    info = db.execute(
        "SELECT u.id AS user_id, j.title FROM applications a "
        "JOIN candidates c ON c.id = a.candidate_id JOIN users u ON u.id = c.user_id "
        "JOIN jobs j ON j.id = a.job_id WHERE a.id = ?",
        (application_id,),
    ).fetchone()
    if info:
        create_notification(
            db, info["user_id"],
            f"Your application for \"{info['title']}\" is now: {new_status}.",
            "candidate.html",
        )

    return jsonify({"message": "Status updated", "status": new_status})


# --------------------------- SAVED JOBS ---------------------------

@app.route("/api/saved-jobs", methods=["POST"])
def save_job():
    data = request.get_json(force=True)
    db = get_db()
    try:
        db.execute(
            "INSERT INTO saved_jobs (candidate_id, job_id) VALUES (?, ?)",
            (data["candidate_id"], data["job_id"]),
        )
        db.commit()
        return jsonify({"message": "Job saved"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Already saved"}), 409


@app.route("/api/saved-jobs", methods=["DELETE"])
def unsave_job():
    data = request.get_json(force=True)
    db = get_db()
    db.execute(
        "DELETE FROM saved_jobs WHERE candidate_id = ? AND job_id = ?",
        (data["candidate_id"], data["job_id"]),
    )
    db.commit()
    return jsonify({"message": "Job unsaved"})


@app.route("/api/candidates/<int:candidate_id>/saved-jobs", methods=["GET"])
def list_saved_jobs(candidate_id):
    db = get_db()
    rows = db.execute(
        "SELECT j.*, u.company_name FROM saved_jobs sj "
        "JOIN jobs j ON j.id = sj.job_id JOIN users u ON u.id = j.recruiter_id "
        "WHERE sj.candidate_id = ? ORDER BY sj.saved_at DESC",
        (candidate_id,),
    ).fetchall()
    jobs = []
    for row in rows:
        job = row_to_dict(row)
        skills = db.execute(
            "SELECT s.name FROM job_skills js JOIN skills s ON s.id = js.skill_id WHERE js.job_id = ?",
            (job["id"],),
        ).fetchall()
        job["skills"] = [s["name"] for s in skills]
        jobs.append(job)
    return jsonify(jobs)


# --------------------------- ADMIN ---------------------------

@app.route("/api/admin/overview", methods=["GET"])
def admin_overview():
    db = get_db()
    stats = {
        "total_recruiters": db.execute("SELECT COUNT(*) AS n FROM users WHERE role='recruiter'").fetchone()["n"],
        "total_candidates": db.execute("SELECT COUNT(*) AS n FROM users WHERE role='candidate'").fetchone()["n"],
        "total_jobs": db.execute("SELECT COUNT(*) AS n FROM jobs").fetchone()["n"],
        "open_jobs": db.execute("SELECT COUNT(*) AS n FROM jobs WHERE status='open'").fetchone()["n"],
        "total_applications": db.execute("SELECT COUNT(*) AS n FROM applications").fetchone()["n"],
    }
    jobs = db.execute(
        "SELECT j.id, j.title, j.status, u.full_name AS recruiter_name, u.company_name, "
        "(SELECT COUNT(*) FROM applications a WHERE a.job_id = j.id) AS application_count "
        "FROM jobs j JOIN users u ON u.id = j.recruiter_id ORDER BY j.created_at DESC"
    ).fetchall()
    users = db.execute(
        "SELECT id, full_name, email, role, company_name, created_at FROM users ORDER BY created_at DESC"
    ).fetchall()
    return jsonify({
        "stats": stats,
        "jobs": [row_to_dict(r) for r in jobs],
        "users": [row_to_dict(r) for r in users],
    })


@app.route("/api/admin/jobs/<int:job_id>", methods=["DELETE"])
def admin_delete_job(job_id):
    db = get_db()
    db.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    db.commit()
    return jsonify({"message": "Job removed"})


@app.route("/api/admin/users/<int:target_user_id>", methods=["DELETE"])
def admin_delete_user(target_user_id):
    db = get_db()
    row = db.execute("SELECT role FROM users WHERE id = ?", (target_user_id,)).fetchone()
    if row and row["role"] == "admin":
        return jsonify({"error": "Cannot remove an admin account"}), 400
    db.execute("DELETE FROM users WHERE id = ?", (target_user_id,))
    db.commit()
    return jsonify({"message": "User removed"})


# --------------------------- ENTRYPOINT ---------------------------

if __name__ == "__main__":
    was_fresh = init_db()
    if was_fresh:
        print("✔ Fresh database initialized at", DB_PATH)
    print("✔ RecruitAI backend running: http://localhost:5000")
    app.run(debug=True, port=5000)
