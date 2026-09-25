import re
from collections import Counter


# ============================================================
# STEP 34 - RESUME IMPROVEMENT PLAN
# ============================================================

def generate_improvement_plan(
    missing_required,
    missing_preferred,
    missing_keywords,
    content_suggestions,
    resume_status,
    ats_score,
):
    high_priority = []
    medium_priority = []
    low_priority = []

    for skill in missing_required:
        high_priority.append(
            f"Required skill gap: {skill}. "
            "Only include or claim this skill if you genuinely have the relevant "
            "knowledge or experience."
        )

    if ats_score < 60:
        high_priority.append(
            "ATS keyword coverage is below 60%. Tailor the resume to the job "
            "description by naturally using relevant terminology that accurately "
            "reflects your experience."
        )

    if resume_status in ["Weak Match", "Moderate Match"]:
        high_priority.append(
            "The technical skill match is below 60%. Strengthen relevant skills "
            "before claiming them on the resume."
        )

    for skill in missing_preferred:
        medium_priority.append(
            f"Preferred skill gap: {skill}. Consider learning or demonstrating "
            "this skill if it is relevant to your career target."
        )

    for keyword in missing_keywords:
        medium_priority.append(
            f"Review missing ATS keyword: {keyword}. Include it naturally only "
            "where it accurately represents your experience."
        )

    for suggestion in content_suggestions:
        medium_priority.append(suggestion)

    low_priority.append(
        "If you have relevant certifications, consider adding them with the "
        "certification name and issuer."
    )

    total_gaps = (
        len(missing_required)
        + len(missing_preferred)
        + len(missing_keywords)
    )

    if high_priority:
        summary = (
            "Focus first on the high-priority skill and ATS gaps, then improve "
            "the remaining resume areas."
        )
    else:
        summary = (
            "The resume has good alignment. Continue improving keywords, "
            "achievements, and measurable results."
        )

    return {
        "high_priority": high_priority,
        "medium_priority": medium_priority,
        "low_priority": low_priority,
        "recommendation_summary": summary,
        "total_detected_gaps": total_gaps,
    }


# ============================================================
# STEP 35 - RESUME BULLET / ACTION VERB ANALYSIS
# ============================================================

ACTION_VERBS = {
    "developed",
    "designed",
    "built",
    "created",
    "implemented",
    "developed",
    "automated",
    "optimized",
    "improved",
    "analyzed",
    "tested",
    "deployed",
    "integrated",
    "configured",
    "managed",
    "maintained",
    "engineered",
    "programmed",
    "led",
    "solved",
    "created",
    "achieved",
}


def analyze_resume_bullets(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    bullet_lines = []

    for line in lines:
        if (
            line.startswith("•")
            or line.startswith("-")
            or line.startswith("*")
            or re.match(r"^\d+[\.\)]\s+", line)
        ):
            bullet_lines.append(line)

    action_verb_count = 0
    weak_bullet_count = 0

    action_verb_examples = []
    weak_bullet_examples = []

    for bullet in bullet_lines:
        cleaned = re.sub(
            r"^[•\-\*]\s*|\d+[\.\)]\s*",
            "",
            bullet,
        ).strip()

        first_word_match = re.match(r"([A-Za-z]+)", cleaned)

        if first_word_match:
            first_word = first_word_match.group(1).lower()
        else:
            first_word = ""

        if first_word in ACTION_VERBS:
            action_verb_count += 1

            if len(action_verb_examples) < 5:
                action_verb_examples.append(cleaned)
        else:
            weak_bullet_count += 1

            if len(weak_bullet_examples) < 5:
                weak_bullet_examples.append(cleaned)

    total_bullets = len(bullet_lines)

    if total_bullets == 0:
        status = "No bullet points detected"
    elif action_verb_count / total_bullets >= 0.6:
        status = "Strong Action Verb Usage"
    elif action_verb_count / total_bullets >= 0.3:
        status = "Moderate Action Verb Usage"
    else:
        status = "Needs Stronger Action Verbs"

    return {
        "total_bullets": total_bullets,
        "action_verb_bullets": action_verb_count,
        "weak_bullets": weak_bullet_count,
        "action_verb_percentage": round(
            (action_verb_count / total_bullets) * 100, 2
        )
        if total_bullets
        else 0,
        "status": status,
        "action_verb_examples": action_verb_examples,
        "weak_bullet_examples": weak_bullet_examples,
    }


# ============================================================
# STEP 36 - ACHIEVEMENT & QUANTIFICATION ANALYSIS
# ============================================================

def analyze_achievements(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    achievement_lines = []
    quantified_lines = []

    for line in lines:
        if len(line) < 15:
            continue

        number_patterns = [
            r"\b\d+(?:\.\d+)?%\b",
            r"\b\d+(?:\.\d+)?\s*(?:users|projects|students|customers|records|tasks)\b",
            r"\b\d+(?:\.\d+)?x\b",
            r"\b\d+(?:\.\d+)?\s*(?:seconds|minutes|hours|days|months)\b",
        ]

        has_quantification = any(
            re.search(pattern, line, re.IGNORECASE)
            for pattern in number_patterns
        )

        achievement_words = [
            "increased",
            "decreased",
            "improved",
            "reduced",
            "achieved",
            "saved",
            "generated",
            "optimized",
            "boosted",
            "completed",
            "delivered",
            "automated",
        ]

        has_achievement_word = any(
            word in line.lower()
            for word in achievement_words
        )

        if has_quantification:
            quantified_lines.append(line)

        if has_quantification and has_achievement_word:
            achievement_lines.append(line)

    total_lines = len(lines)

    if len(achievement_lines) >= 3:
        status = "Strong Quantified Achievements"
    elif len(achievement_lines) >= 1:
        status = "Some Quantified Achievements"
    else:
        status = "Limited Quantified Achievements"

    return {
        "quantified_lines": len(quantified_lines),
        "achievement_lines": len(achievement_lines),
        "total_resume_lines": total_lines,
        "achievement_status": status,
        "achievement_examples": achievement_lines[:5],
        "quantification_examples": quantified_lines[:5],
    }


# ============================================================
# STEP 37 - SECTION-WISE RESUME SCORING
# ============================================================

def calculate_section_scores(word_counts, resume_sections):
    scores = {}

    section_limits = {
        "summary": (30, 80),
        "education": (15, 100),
        "technical_skills": (10, 150),
        "projects": (40, 500),
        "experience": (30, 500),
        "certifications": (5, 150),
    }

    for section, (minimum, maximum) in section_limits.items():
        word_count = word_counts.get(section, 0)

        if word_count == 0:
            scores[section] = 0
        elif minimum <= word_count <= maximum:
            scores[section] = 100
        elif word_count < minimum:
            scores[section] = 60
        else:
            scores[section] = 80

    existing_scores = list(scores.values())

    overall_section_score = round(
        sum(existing_scores) / len(existing_scores), 2
    ) if existing_scores else 0

    return {
        "section_scores": scores,
        "overall_section_score": overall_section_score,
    }


# ============================================================
# STEP 38 - JOB ROLE / TITLE ALIGNMENT
# ============================================================

KNOWN_ROLES = [
    "software developer",
    "software engineer",
    "python developer",
    "java developer",
    "frontend developer",
    "backend developer",
    "full stack developer",
    "web developer",
    "data analyst",
    "data scientist",
    "machine learning engineer",
    "ai engineer",
    "devops engineer",
    "cloud engineer",
    "database administrator",
    "mobile app developer",
]


def extract_roles(text):
    text_lower = text.lower()

    detected_roles = []

    for role in KNOWN_ROLES:
        if role in text_lower:
            detected_roles.append(role)

    return detected_roles


def analyze_job_title_alignment(resume_text, job_text):
    resume_roles = extract_roles(resume_text)
    job_roles = extract_roles(job_text)

    matched_roles = [
        role for role in job_roles
        if role in resume_roles
    ]

    missing_roles = [
        role for role in job_roles
        if role not in resume_roles
    ]

    if not job_roles:
        status = "Job Role Not Detected"
    elif matched_roles:
        status = "Role Alignment Detected"
    else:
        status = "Role Alignment Needs Improvement"

    return {
        "resume_roles": resume_roles,
        "job_roles": job_roles,
        "matched_roles": matched_roles,
        "missing_roles": missing_roles,
        "alignment_status": status,
    }


# ============================================================
# STEP 39 - FINAL RESUME HEALTH REPORT
# ============================================================

def generate_resume_health_report(
    ats_score,
    content_score,
    section_score,
    weighted_match_percentage,
    bullet_analysis,
    achievement_analysis,
    job_alignment,
):
    health_score = round(
        (
            ats_score
            + content_score
            + section_score
            + weighted_match_percentage
        ) / 4,
        2,
    )

    health_score = max(0, min(100, health_score))

    if health_score >= 80:
        health_status = "Excellent Resume Health"
    elif health_score >= 65:
        health_status = "Good Resume Health"
    elif health_score >= 50:
        health_status = "Moderate Resume Health"
    else:
        health_status = "Needs Improvement"

    strengths = []
    weaknesses = []

    if ats_score >= 70:
        strengths.append("Good ATS keyword alignment")
    else:
        weaknesses.append("ATS keyword alignment needs improvement")

    if content_score >= 70:
        strengths.append("Good resume content coverage")
    else:
        weaknesses.append("Resume content coverage can be improved")

    if section_score >= 80:
        strengths.append("Strong resume section structure")
    else:
        weaknesses.append("Some resume sections need improvement")

    if weighted_match_percentage >= 70:
        strengths.append("Strong job skill match")
    else:
        weaknesses.append("Job skill match can be improved")

    if bullet_analysis.get("action_verb_percentage", 0) >= 60:
        strengths.append("Strong action verb usage")
    else:
        weaknesses.append("Use stronger action verbs in resume bullets")

    if achievement_analysis.get("achievement_lines", 0) > 0:
        strengths.append("Contains quantified achievements")
    else:
        weaknesses.append("Add more measurable achievements")

    if job_alignment.get("matched_roles"):
        strengths.append("Job role alignment detected")
    else:
        weaknesses.append("Improve job title alignment")

    return {
        "health_score": health_score,
        "health_status": health_status,
        "strengths": strengths,
        "weaknesses": weaknesses,
    }


# ============================================================
# STEP 40 - ANALYSIS SUMMARY
# ============================================================

def generate_analysis_summary(
    resume_status,
    ats_score,
    weighted_match_percentage,
    content_score,
    health_score,
):
    scores = {
        "ATS Score": ats_score,
        "Job Match": weighted_match_percentage,
        "Content Score": content_score,
        "Resume Health": health_score,
    }

    strongest_area = max(scores, key=scores.get)
    weakest_area = min(scores, key=scores.get)

    if health_score >= 80:
        overall_status = "Strong Resume"
    elif health_score >= 65:
        overall_status = "Good Resume"
    elif health_score >= 50:
        overall_status = "Moderate Resume"
    else:
        overall_status = "Needs Improvement"

    return {
        "overall_status": overall_status,
        "resume_status": resume_status,
        "scores": scores,
        "strongest_area": strongest_area,
        "weakest_area": weakest_area,
        "summary": (
            f"The resume currently has a {overall_status.lower()} profile. "
            f"The strongest area is {strongest_area}, while "
            f"{weakest_area} requires more attention."
        ),
    }