from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity



def calculate_match_score(resume_skills: set, jd_skills: set) -> dict:
    """Calculate matched, missing, and extra skills."""
    resume_skills = {s.lower() for s in resume_skills}
    jd_skills = {s.lower() for s in jd_skills}

    matched = resume_skills & jd_skills
    missing = jd_skills - resume_skills
    extra = resume_skills - jd_skills

    score = (len(matched) / len(jd_skills) * 100) if jd_skills else 0

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "extra_skills": extra,
        "skill_match_score": round(score, 2),
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
    }


def calculate_text_similarity(resume_text: str, jd_text: str) -> float:
    """TF-IDF cosine similarity between resume and JD text."""
    if not resume_text.strip() or not jd_text.strip():
        return 0.0
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        vectors = vectorizer.fit_transform([resume_text, jd_text])
        score = cosine_similarity(vectors[0], vectors[1])[0][0]
        return round(float(score), 4)
    except Exception:
        return 0.0


def get_overall_score(resume_skills: set, jd_skills: set,
                      resume_text: str = "", jd_text: str = "") -> dict:
    """
    Combine skill match (70%) + text similarity (30%) into one score.
    resume_text and jd_text are optional — pass empty strings if not available.
    """
    skill_result = calculate_match_score(resume_skills, jd_skills)
    text_sim = calculate_text_similarity(resume_text, jd_text)

    skill_score = skill_result["skill_match_score"]
    overall = round(skill_score * 0.7 + text_sim * 100 * 0.3, 2)

    return {
        **skill_result,
        "text_similarity_score": text_sim,
        "overall_score": overall,
    }


def get_fit_level(score: float) -> str:
    """Return a human-readable fit label based on score."""
    if score >= 75:
        return "Strong Match 💚"
    elif score >= 50:
        return "Good Match 🟡"
    elif score >= 25:
        return "Partial Match 🟠"
    else:
        return "Low Match 🔴"


def get_recommendations(missing_skills: set, score: float) -> list:
    """Generate actionable recommendations based on missing skills and score."""
    recs = []

    if score >= 75:
        recs.append("Great fit! Tailor your resume summary to mirror the job description language.")
    elif score >= 50:
        recs.append("Good match. Highlight your most relevant projects prominently.")
    else:
        recs.append("Consider upskilling before applying — focus on the missing skills below.")

    if missing_skills:
        top_missing = sorted(missing_skills)[:5]
        recs.append(f"Learn these missing skills: {', '.join(top_missing)}.")
        recs.append("Add a 'Skills' section to your resume listing all technical tools explicitly.")

    if score < 50:
        recs.append("Take a free course on Coursera or Udemy to close skill gaps quickly.")

    recs.append("Quantify your achievements in bullet points (e.g. 'improved accuracy by 15%').")
    recs.append("Use keywords from the job description naturally throughout your resume.")

    return recs