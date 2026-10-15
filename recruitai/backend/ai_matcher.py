"""
RecruitAI - AI Matching Engine
================================
Scores a candidate against a job using:
  1. TF-IDF + cosine similarity between resume text and job description/requirements
     (semantic-ish keyword matching, runs 100% locally, no API key needed)
  2. Structured skill overlap (candidate_skills vs job_skills)
  3. Experience-level fit
  4. A lightweight, template-based "AI summary" explaining the score
     (drop-in point to swap for a real LLM call, see call_llm_explainer() below)

This is intentionally dependency-light (scikit-learn + numpy only) so it can be
demoed / graded without needing external API keys or network access.
"""

import re
import os
import json
from math import sqrt
from collections import Counter

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


STOPWORDS = set("""
a an the and or of to in for with on at by is are was were be been being
this that these those it its as from into over under about your you we our
""".split())


def _tokenize(text: str):
    text = (text or "").lower()
    words = re.findall(r"[a-z0-9\+\#\.]+", text)
    return [w for w in words if w not in STOPWORDS and len(w) > 1]


def _fallback_similarity(text_a: str, text_b: str) -> float:
    """Pure-python cosine similarity fallback if sklearn isn't installed."""
    a, b = Counter(_tokenize(text_a)), Counter(_tokenize(text_b))
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    dot = sum(a[w] * b[w] for w in common)
    norm_a = sqrt(sum(v * v for v in a.values()))
    norm_b = sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def text_similarity_score(resume_text: str, job_text: str) -> float:
    """Returns 0-100 similarity between resume and job description/requirements."""
    if not resume_text or not job_text:
        return 0.0

    if SKLEARN_AVAILABLE:
        try:
            vectorizer = TfidfVectorizer(stop_words="english")
            tfidf = vectorizer.fit_transform([resume_text, job_text])
            sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        except ValueError:
            sim = _fallback_similarity(resume_text, job_text)
    else:
        sim = _fallback_similarity(resume_text, job_text)

    return round(float(sim) * 100, 1)


def skill_overlap_score(candidate_skills: list, job_skills: list, required_skills: list = None):
    """
    candidate_skills / job_skills: list[str] (case-insensitive)
    required_skills: subset of job_skills that are mandatory -> weighted higher
    Returns (score_0_100, matched_skills, missing_required_skills)
    """
    cand_set = {s.lower().strip() for s in candidate_skills}
    job_set = {s.lower().strip() for s in job_skills}
    required_set = {s.lower().strip() for s in (required_skills or job_skills)}

    if not job_set:
        return 0.0, [], []

    matched = cand_set & job_set
    missing_required = required_set - cand_set

    # Weight required skills 2x, nice-to-have 1x
    nice_to_have = job_set - required_set
    max_points = len(required_set) * 2 + len(nice_to_have)
    earned_points = (
        len(matched & required_set) * 2 + len(matched & nice_to_have)
    )
    score = (earned_points / max_points * 100) if max_points else 0.0

    return round(score, 1), sorted(matched), sorted(missing_required)


def experience_fit_score(candidate_years: float, min_required_years: float) -> float:
    """0-100 score: full marks if candidate meets/exceeds requirement,
    tapering off penalty if under-qualified, slight taper if wildly over-qualified."""
    if min_required_years <= 0:
        return 100.0
    ratio = candidate_years / min_required_years
    if ratio >= 1:
        # meets requirement; cap bonus, gentle penalty for extreme overqualification (>3x)
        return 100.0 if ratio <= 3 else max(80.0, 100 - (ratio - 3) * 5)
    return round(max(0.0, ratio * 100), 1)


LANGUAGE_LEVEL_RANK = {"basic": 1, "conversational": 2, "fluent": 3, "native": 4}


def language_match_score(candidate_languages: list, job_languages: list):
    """
    candidate_languages / job_languages: list[{"name": str, "level": str}]
    job_languages is what the job requires. If the job has no language
    requirements, this returns a neutral 100 so it never penalizes a job
    that simply didn't ask for any.
    Returns (score_0_100, matched_labels, missing_labels).
    """
    if not job_languages:
        return 100.0, [], []

    cand_map = {
        l["name"].strip().lower(): LANGUAGE_LEVEL_RANK.get(l.get("level", "conversational"), 2)
        for l in candidate_languages
    }

    matched, missing = [], []
    points = 0.0
    for jl in job_languages:
        name = jl["name"].strip()
        needed_rank = LANGUAGE_LEVEL_RANK.get(jl.get("level", "conversational"), 2)
        cand_rank = cand_map.get(name.lower())
        if cand_rank is None:
            missing.append(name)
        elif cand_rank >= needed_rank:
            points += 1
            matched.append(name)
        else:
            # speaks it, just below the level the job asked for -> partial credit
            points += 0.5
            matched.append(f"{name} (below required level)")

    score = round(points / len(job_languages) * 100, 1)
    return score, matched, missing


def compute_match(resume_text, job_description, job_requirements,
                   candidate_skills, job_skills, required_skills,
                   candidate_years, min_required_years,
                   candidate_languages=None, job_languages=None,
                   weights=None):
    """
    Master scoring function combining all signals.
    weights: dict with keys 'text', 'skills', 'experience', 'language' summing to 1.0
    Returns a dict ready to store in `applications` table + display in UI.
    """
    weights = weights or {"text": 0.30, "skills": 0.30, "experience": 0.15, "language": 0.25}

    job_text = f"{job_description}\n{job_requirements}"
    t_score = text_similarity_score(resume_text, job_text)
    s_score, matched, missing = skill_overlap_score(candidate_skills, job_skills, required_skills)
    e_score = experience_fit_score(candidate_years, min_required_years)
    l_score, matched_langs, missing_langs = language_match_score(
        candidate_languages or [], job_languages or []
    )

    final_score = round(
        t_score * weights["text"]
        + s_score * weights["skills"]
        + e_score * weights["experience"]
        + l_score * weights["language"],
        1
    )

    summary = generate_ai_summary(final_score, t_score, s_score, e_score, matched, missing, missing_langs)

    return {
        "match_score": final_score,
        "text_similarity": t_score,
        "skill_overlap": s_score,
        "experience_fit": e_score,
        "language_match": l_score,
        "matched_skills": matched,
        "missing_required_skills": missing,
        "matched_languages": matched_langs,
        "missing_languages": missing_langs,
        "ai_summary": summary,
    }


def generate_ai_summary(final_score, t_score, s_score, e_score, matched, missing, missing_langs=None):
    """
    Template-based natural-language explanation of the score.
    --> Swap this function's body for `call_llm_explainer(...)` below to use
        a real LLM for richer, more nuanced explanations at demo/production time.
    """
    if final_score >= 80:
        verdict = "Excellent match"
    elif final_score >= 60:
        verdict = "Strong match"
    elif final_score >= 40:
        verdict = "Moderate match"
    else:
        verdict = "Weak match"

    parts = [f"{verdict} ({final_score}/100)."]

    if matched:
        shown = ", ".join(matched[:5])
        parts.append(f"Matches on: {shown}.")
    if missing:
        shown = ", ".join(missing[:5])
        parts.append(f"Missing required skills: {shown}.")
    if missing_langs:
        shown = ", ".join(missing_langs[:5])
        parts.append(f"Missing required language(s): {shown}.")
    if e_score < 60:
        parts.append("Experience level is below the role's stated requirement.")
    if t_score < 30:
        parts.append("Resume wording overlaps little with the job description, worth a manual review.")

    return " ".join(parts)


def rank_candidates(job, candidates):
    """
    job: dict with description, requirements, skills(list), required_skills(list),
         min_experience, languages(list of {"name","level"})
    candidates: list of dicts with resume_text, skills(list), experience_years,
         languages(list of {"name","level"})
    Returns candidates sorted by match_score desc, each annotated with scoring detail.
    """
    results = []
    for c in candidates:
        scored = compute_match(
            resume_text=c.get("resume_text", ""),
            job_description=job.get("description", ""),
            job_requirements=job.get("requirements", ""),
            candidate_skills=c.get("skills", []),
            job_skills=job.get("skills", []),
            required_skills=job.get("required_skills", []),
            candidate_years=c.get("experience_years", 0),
            min_required_years=job.get("min_experience", 0),
            candidate_languages=c.get("languages", []),
            job_languages=job.get("languages", []),
        )
        results.append({**c, **scored})
    return sorted(results, key=lambda r: r["match_score"], reverse=True)


# ---------------------------------------------------------------------------
# OPTIONAL: real LLM-powered explanation (used if ANTHROPIC_API_KEY is set)
# Wire this in instead of generate_ai_summary() for a richer demo moment.
# ---------------------------------------------------------------------------
def call_llm_explainer(resume_text, job_description, matched, missing):
    """
    Calls the Anthropic API to generate a nuanced, recruiter-friendly explanation.
    Falls back silently to the template summary if no API key is configured.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None  # caller should fall back to generate_ai_summary()

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        prompt = (
            "You are a recruitment assistant. In 2 short sentences, explain to a "
            "recruiter why this candidate is or isn't a good fit.\n\n"
            f"JOB DESCRIPTION:\n{job_description[:1500]}\n\n"
            f"RESUME:\n{resume_text[:1500]}\n\n"
            f"Matched skills: {', '.join(matched)}\n"
            f"Missing required skills: {', '.join(missing)}"
        )
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text.strip()
    except Exception:
        return None


if __name__ == "__main__":
    # quick manual smoke test
    demo_job = {
        "description": "We need a backend engineer to build APIs and manage our SQL database.",
        "requirements": "3+ years Python, SQL, Flask, REST API design.",
        "skills": ["Python", "SQL", "Flask", "REST"],
        "required_skills": ["Python", "SQL"],
        "min_experience": 3,
    }
    demo_candidates = [
        {"name": "Amina", "resume_text": "5 years building Python Flask APIs with SQL databases.",
         "skills": ["Python", "SQL", "Flask"], "experience_years": 5},
        {"name": "Youssef", "resume_text": "Frontend developer skilled in React and CSS animations.",
         "skills": ["React", "CSS", "JavaScript"], "experience_years": 2},
    ]
    for r in rank_candidates(demo_job, demo_candidates):
        print(json.dumps({k: r[k] for k in ("name", "match_score", "ai_summary")}, indent=2))
