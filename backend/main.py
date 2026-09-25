from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import re
import fitz

from backend.advanced_analysis import (
    generate_improvement_plan,
    analyze_resume_bullets,
    analyze_achievements,
    calculate_section_scores,
    analyze_job_title_alignment,
    generate_resume_health_report,
    generate_analysis_summary,
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="AI Resume Analyzer",
    description="AI-powered Resume and Job Description Analyzer",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# SKILL DATABASE
# ============================================================

SKILL_DATABASE = [
    # Programming
    "python",
    "java",
    "javascript",
    "typescript",
    "c",
    "c++",
    "c#",

    # Web
    "html",
    "css",
    "bootstrap",
    "tailwind css",
    "react",
    "angular",
    "vue",
    "next.js",
    "node.js",
    "express",
    "fastapi",
    "flask",
    "django",
    "rest api",
    "graphql",

    # Database
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "oracle",
    "firebase",

    # Cloud / DevOps
    "aws",
    "azure",
    "google cloud",
    "docker",
    "kubernetes",
    "linux",

    # Tools
    "git",
    "github",
    "gitlab",

    # AI / ML
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "natural language processing",
    "nlp",
    "ml",
    "genai",
    "generative ai",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",

    # CS
    "problem solving",
    "data structures",
    "algorithms",
    "object-oriented programming",

    # Other
    "code review",
    "testing",
    "performance",
    "agile",
    "scrum",
    "communication",
    "teamwork",
]


# ============================================================
# SKILL ALIASES
# ============================================================

SKILL_ALIASES = {
    "py": "python",
    "python3": "python",

    "js": "javascript",
    "javascript.js": "javascript",

    "ts": "typescript",

    "reactjs": "react",
    "react.js": "react",

    "node": "node.js",
    "nodejs": "node.js",

    "fast api": "fastapi",

    "rest": "rest api",
    "restful api": "rest api",
    "rest apis": "rest api",

    "mongo": "mongodb",
    "mongo db": "mongodb",
    "mongodb database": "mongodb",

    "postgres": "postgresql",

    "amazon web services": "aws",
    "aws cloud": "aws",

    "object oriented programming": "object-oriented programming",
    "object-oriented programming": "object-oriented programming",
    "oops": "object-oriented programming",
    "oop": "object-oriented programming",

    "problem-solving": "problem solving",

    "ml": "machine learning",

    "ai": "artificial intelligence",

    "nlp": "natural language processing",

    "generative ai": "generative ai",

    "gen ai": "generative ai",
}


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "AI Resume Analyzer API is running",
        "version": "1.0.0",
        "docs": "/docs",
    }


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_pdf_text(file_bytes):
    try:
        document = fitz.open(
            stream=file_bytes,
            filetype="pdf",
        )

        pages = []

        for page in document:
            pages.append(page.get_text())

        document.close()

        return "\n".join(pages)

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to read PDF: {str(error)}",
        )


# ============================================================
# SECTION DETECTION
# ============================================================

SECTION_ALIASES = {
    "summary": [
        "summary",
        "professional summary",
        "profile",
        "objective",
        "career objective",
    ],

    "education": [
        "education",
        "academic background",
        "qualifications",
    ],

    "technical_skills": [
        "technical skills",
        "skills",
        "technical skill",
        "technical expertise",
        "technologies",
    ],

    "projects": [
        "projects",
        "academic projects",
        "personal projects",
        "project experience",
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "internship",
        "internships",
    ],

    "certifications": [
        "certifications",
        "certificates",
        "certification",
        "licenses",
    ],

    "additional_information": [
        "additional information",
        "additional",
        "achievements",
        "activities",
        "interests",
        "hobbies",
    ],
}


def detect_sections(text):

    text_lower = text.lower()

    result = {}

    for section, aliases in SECTION_ALIASES.items():

        result[section] = any(
            re.search(
                rf"(?<!\w){re.escape(alias)}(?!\w)",
                text_lower,
            )
            for alias in aliases
        )

    return result


# ============================================================
# WORD COUNT
# ============================================================

def calculate_word_count(text):

    return len(
        re.findall(
            r"\b\w+\b",
            text,
        )
    )


def calculate_section_word_counts(text):

    lines = text.splitlines()

    section_positions = []

    for index, line in enumerate(lines):

        normalized = line.strip().lower()

        for section, aliases in SECTION_ALIASES.items():

            if normalized in aliases:

                section_positions.append(
                    (index, section)
                )

                break

    word_counts = {
        "summary": 0,
        "education": 0,
        "technical_skills": 0,
        "projects": 0,
        "experience": 0,
        "certifications": 0,
        "additional_information": 0,
    }

    for position, (start_index, section) in enumerate(
        section_positions
    ):

        end_index = (
            section_positions[position + 1][0]
            if position + 1 < len(section_positions)
            else len(lines)
        )

        section_text = "\n".join(
            lines[start_index + 1:end_index]
        )

        word_counts[section] = calculate_word_count(
            section_text
        )

    return word_counts


# ============================================================
# SKILL NORMALIZATION
# ============================================================

def normalize_skill(skill):

    skill = skill.strip().lower()

    skill = re.sub(
        r"\s+",
        " ",
        skill,
    )

    return SKILL_ALIASES.get(
        skill,
        skill,
    )


# ============================================================
# SKILL SEARCH
# ============================================================

def skill_exists_in_text(skill, text):

    if not text:
        return False

    normalized_skill = normalize_skill(skill)

    aliases = [
        alias
        for alias, normalized in SKILL_ALIASES.items()
        if normalized == normalized_skill
    ]

    aliases.append(normalized_skill)

    text_lower = text.lower()

    for alias in aliases:

        pattern = (
            r"(?<![a-zA-Z0-9])"
            + re.escape(alias.lower())
            + r"(?![a-zA-Z0-9])"
        )

        if re.search(
            pattern,
            text_lower,
        ):
            return True

    return False


# ============================================================
# RESUME SKILL EXTRACTION
# ============================================================

def extract_skills(text):

    found_skills = []

    for skill in SKILL_DATABASE:

        if skill_exists_in_text(
            skill,
            text,
        ):

            normalized = normalize_skill(skill)

            if normalized not in found_skills:
                found_skills.append(normalized)

    return found_skills


# ============================================================
# JOB DESCRIPTION CLEANING
# ============================================================

def clean_job_description(text):

    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Convert bullets to spaces
    text = re.sub(
        r"[•●▪◦]",
        "\n",
        text,
    )

    # Normalize excessive spaces
    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# JOB SECTION EXTRACTION
# ============================================================

def extract_job_sections(job_text):

    job_text = clean_job_description(job_text)

    if not job_text:
        return {
            "required": "",
            "preferred": "",
        }

    text = job_text.lower()

    # --------------------------------------------------------
    # Preferred section
    # --------------------------------------------------------

    preferred_patterns = [
        r"\bpreferred\s+skills?\b",
        r"\bpreferred\b",
        r"\bdesired\s+skills?\b",
        r"\bdesired\b",
        r"\bnice\s+to\s+have\b",
        r"\bgood\s+to\s+have\b",
        r"\boptional\s+skills?\b",
        r"\bpreferred\s+qualifications?\b",
    ]

    preferred_match = None

    for pattern in preferred_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:
            preferred_match = match
            break

    if preferred_match:

        required_part = text[
            :preferred_match.start()
        ]

        preferred_part = text[
            preferred_match.end():
        ]

    else:

        required_part = text
        preferred_part = ""

    # --------------------------------------------------------
    # Stop preferred section at another major heading
    # --------------------------------------------------------

    if preferred_part:

        stop_patterns = [
            r"\bqualifications?\b",
            r"\beducation\b",
            r"\bexperience\b",
            r"\bresponsibilities\b",
            r"\babout\s+the\s+role\b",
            r"\babout\s+us\b",
        ]

        stop_positions = []

        for pattern in stop_patterns:

            match = re.search(
                pattern,
                preferred_part,
                re.IGNORECASE,
            )

            if match:
                stop_positions.append(
                    match.start()
                )

        if stop_positions:

            preferred_part = preferred_part[
                :min(stop_positions)
            ]

    # --------------------------------------------------------
    # Required section
    # --------------------------------------------------------

    required_patterns = [
        r"\brequired\s+skills?\b",
        r"\brequired\b",
        r"\brequirements?\b",
        r"\bmust\s+have\b",
        r"\bmandatory\s+skills?\b",
        r"\bqualifications?\b",
    ]

    required_match = None

    for pattern in required_patterns:

        match = re.search(
            pattern,
            required_part,
            re.IGNORECASE,
        )

        if match:
            required_match = match
            break

    if required_match:

        required_section = required_part[
            required_match.end():
        ]

    else:

        # If there is no explicit Required heading,
        # use the whole non-preferred part.
        required_section = required_part

    return {
        "required": required_section,
        "preferred": preferred_part,
    }


# ============================================================
# REQUIRED / PREFERRED SKILL EXTRACTION
# ============================================================

def extract_required_preferred_skills(job_text):

    job_text = clean_job_description(
        job_text
    )

    sections = extract_job_sections(
        job_text
    )

    required_text = sections["required"]
    preferred_text = sections["preferred"]

    required_skills = []
    preferred_skills = []

    # --------------------------------------------------------
    # Required skills
    # --------------------------------------------------------

    for skill in SKILL_DATABASE:

        if skill_exists_in_text(
            skill,
            required_text,
        ):

            normalized = normalize_skill(skill)

            if normalized not in required_skills:

                required_skills.append(
                    normalized
                )

    # --------------------------------------------------------
    # Preferred skills
    # --------------------------------------------------------

    for skill in SKILL_DATABASE:

        if skill_exists_in_text(
            skill,
            preferred_text,
        ):

            normalized = normalize_skill(skill)

            if normalized not in preferred_skills:

                preferred_skills.append(
                    normalized
                )

    # --------------------------------------------------------
    # If explicit required section wasn't found,
    # detect all technical skills from the complete JD.
    # --------------------------------------------------------

    if not required_skills and not preferred_skills:

        for skill in SKILL_DATABASE:

            if skill_exists_in_text(
                skill,
                job_text,
            ):

                normalized = normalize_skill(
                    skill
                )

                if normalized not in required_skills:

                    required_skills.append(
                        normalized
                    )

    # --------------------------------------------------------
    # If preferred skills were detected,
    # remove them from required.
    # --------------------------------------------------------

    preferred_skills = [
        skill
        for skill in preferred_skills
        if skill not in required_skills
    ]

    # --------------------------------------------------------
    # Safety fallback:
    # If only preferred skills exist, keep them.
    # --------------------------------------------------------

    return {
        "required": list(
            dict.fromkeys(
                required_skills
            )
        ),
        "preferred": list(
            dict.fromkeys(
                preferred_skills
            )
        ),
    }


# ============================================================
# JOB SKILL EXTRACTION
# ============================================================

def extract_job_skills(job_text):

    result = extract_required_preferred_skills(
        job_text
    )

    return list(
        dict.fromkeys(
            result["required"]
            + result["preferred"]
        )
    )


# ============================================================
# SKILL MATCHING
# ============================================================

def match_skills(
    resume_skills,
    required_skills,
    preferred_skills,
):

    resume_set = {
        normalize_skill(skill)
        for skill in resume_skills
    }

    required_skills = list(
        dict.fromkeys(
            normalize_skill(skill)
            for skill in required_skills
        )
    )

    preferred_skills = list(
        dict.fromkeys(
            normalize_skill(skill)
            for skill in preferred_skills
        )
    )

    matched_required = [
        skill
        for skill in required_skills
        if skill in resume_set
    ]

    missing_required = [
        skill
        for skill in required_skills
        if skill not in resume_set
    ]

    matched_preferred = [
        skill
        for skill in preferred_skills
        if skill in resume_set
    ]

    missing_preferred = [
        skill
        for skill in preferred_skills
        if skill not in resume_set
    ]

    # --------------------------------------------------------
    # Required score
    # --------------------------------------------------------

    if required_skills:

        required_percentage = (
            len(matched_required)
            / len(required_skills)
            * 100
        )

    else:

        required_percentage = 0

    # --------------------------------------------------------
    # Preferred score
    # --------------------------------------------------------

    if preferred_skills:

        preferred_percentage = (
            len(matched_preferred)
            / len(preferred_skills)
            * 100
        )

    else:

        preferred_percentage = 0

    # --------------------------------------------------------
    # Weighted score
    # --------------------------------------------------------

    if required_skills and preferred_skills:

        weighted_match_percentage = (
            required_percentage * 0.70
            + preferred_percentage * 0.30
        )

    elif required_skills:

        weighted_match_percentage = (
            required_percentage
        )

    elif preferred_skills:

        weighted_match_percentage = (
            preferred_percentage
        )

    else:

        weighted_match_percentage = 0

    weighted_match_percentage = round(
        weighted_match_percentage,
        2,
    )

    # --------------------------------------------------------
    # Match status
    # --------------------------------------------------------

    if weighted_match_percentage >= 80:

        resume_status = "Strong Match"

    elif weighted_match_percentage >= 60:

        resume_status = "Good Match"

    elif weighted_match_percentage >= 40:

        resume_status = "Moderate Match"

    else:

        resume_status = "Weak Match"

    return {
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,

        "matched_required": matched_required,
        "missing_required": missing_required,

        "matched_preferred": matched_preferred,
        "missing_preferred": missing_preferred,

        "weighted_match_percentage":
            weighted_match_percentage,

        "resume_status":
            resume_status,
    }


# ============================================================
# SKILL GAP CATEGORIES
# ============================================================

def categorize_skill_gaps(
    missing_required,
    missing_preferred,
):

    all_missing = list(
        dict.fromkeys(
            missing_required
            + missing_preferred
        )
    )

    categories = {
        "Programming Languages": [],
        "Web Development": [],
        "Database Skills": [],
        "Cloud / DevOps": [],
        "AI / Machine Learning": [],
        "Tools": [],
        "Core Computer Science": [],
        "Other": [],
    }

    programming = {
        "python",
        "java",
        "javascript",
        "typescript",
        "c",
        "c++",
        "c#",
    }

    web = {
        "html",
        "css",
        "bootstrap",
        "tailwind css",
        "react",
        "angular",
        "vue",
        "next.js",
        "node.js",
        "express",
        "fastapi",
        "flask",
        "django",
        "rest api",
        "graphql",
    }

    databases = {
        "sql",
        "mysql",
        "postgresql",
        "mongodb",
        "oracle",
        "firebase",
    }

    cloud_devops = {
        "aws",
        "azure",
        "google cloud",
        "docker",
        "kubernetes",
        "linux",
    }

    ai_ml = {
        "artificial intelligence",
        "machine learning",
        "deep learning",
        "natural language processing",
        "nlp",
        "ml",
        "genai",
        "generative ai",
        "pandas",
        "numpy",
        "scikit-learn",
        "tensorflow",
        "pytorch",
    }

    tools = {
        "git",
        "github",
        "gitlab",
    }

    core_cs = {
        "problem solving",
        "data structures",
        "algorithms",
        "object-oriented programming",
    }

    for skill in all_missing:

        if skill in programming:

            categories[
                "Programming Languages"
            ].append(skill)

        elif skill in web:

            categories[
                "Web Development"
            ].append(skill)

        elif skill in databases:

            categories[
                "Database Skills"
            ].append(skill)

        elif skill in cloud_devops:

            categories[
                "Cloud / DevOps"
            ].append(skill)

        elif skill in ai_ml:

            categories[
                "AI / Machine Learning"
            ].append(skill)

        elif skill in tools:

            categories[
                "Tools"
            ].append(skill)

        elif skill in core_cs:

            categories[
                "Core Computer Science"
            ].append(skill)

        else:

            categories[
                "Other"
            ].append(skill)

    return {
        category: skills
        for category, skills in categories.items()
        if skills
    }


# ============================================================
# RESUME STRENGTH
# ============================================================

def analyze_resume_strength(
    weighted_match_percentage,
):

    if weighted_match_percentage >= 80:

        status = "Strong Match"

        suggestions = [
            "Resume has strong alignment with the job description."
        ]

    elif weighted_match_percentage >= 60:

        status = "Good Match"

        suggestions = [
            "Add more relevant job-specific skills where applicable.",
            "Strengthen project descriptions with measurable results.",
        ]

    elif weighted_match_percentage >= 40:

        status = "Moderate Match"

        suggestions = [
            "Improve required skill coverage.",
            "Add more relevant project experience.",
            "Tailor the resume to the job description.",
        ]

    else:

        status = "Weak Match"

        suggestions = [
            "Increase required skill coverage.",
            "Build relevant projects.",
            "Tailor the resume strongly to the target role.",
        ]

    return {
        "resume_status": status,
        "suggestions": suggestions,
    }


# ============================================================
# RESUME QUALITY
# ============================================================

def analyze_resume_quality(sections):

    major_sections = [
        "summary",
        "education",
        "technical_skills",
        "projects",
        "experience",
        "certifications",
    ]

    missing_sections = [
        section
        for section in major_sections
        if not sections.get(
            section,
            False,
        )
    ]

    section_score = round(
        (
            len(major_sections)
            - len(missing_sections)
        )
        / len(major_sections)
        * 100,
        2,
    )

    if section_score >= 80:

        quality_status = "Strong Resume Structure"

    elif section_score >= 60:

        quality_status = "Good Resume Structure"

    else:

        quality_status = "Needs Structural Improvement"

    return {
        "missing_sections":
            missing_sections,

        "section_score":
            section_score,

        "quality_status":
            quality_status,
    }


# ============================================================
# RESUME CONTENT QUALITY
# ============================================================

def analyze_resume_content(
    word_counts,
    text,
):

    project_count = len(
        re.findall(
            r"\bproject\b",
            text,
            re.IGNORECASE,
        )
    )

    # Avoid counting "projects" as separate project references.
    if project_count > 2:
        project_count = min(
            project_count,
            10,
        )

    suggestions = []

    summary_words = word_counts.get(
        "summary",
        0,
    )

    if summary_words == 0:

        summary_status = "Missing"

        suggestions.append(
            "Add a concise professional summary."
        )

    elif summary_words < 30:

        summary_status = "Too Short"

        suggestions.append(
            "Expand the professional summary slightly."
        )

    elif summary_words <= 80:

        summary_status = "Good Length"

    else:

        summary_status = "Too Long"

        suggestions.append(
            "Shorten the professional summary."
        )

    experience_words = word_counts.get(
        "experience",
        0,
    )

    if experience_words == 0:

        experience_status = "No experience content"

        suggestions.append(
            "Add internships, work experience, practical training, "
            "or relevant real-world experience if applicable."
        )

    else:

        experience_status = "Experience Content Present"

    certification_words = word_counts.get(
        "certifications",
        0,
    )

    if certification_words == 0:

        certification_status = (
            "No certification details detected"
        )

        suggestions.append(
            "If applicable, add relevant certifications."
        )

    else:

        certification_status = (
            "Certification Content Present"
        )

    short_sections = [
        section
        for section, count in word_counts.items()
        if section != "additional_information"
        and 0 < count < 10
    ]

    content_score = 100

    if summary_words == 0:
        content_score -= 15

    if experience_words == 0:
        content_score -= 10

    if certification_words == 0:
        content_score -= 5

    content_score = max(
        0,
        min(
            100,
            content_score,
        ),
    )

    if content_score >= 80:

        content_status = "Strong Content"

    elif content_score >= 60:

        content_status = "Good Content"

    else:

        content_status = "Needs Content Improvement"

    return {
        "word_counts":
            word_counts,

        "summary_status":
            summary_status,

        "project_count":
            project_count,

        "project_status":
            f"{project_count} project references detected",

        "experience_status":
            experience_status,

        "certification_status":
            certification_status,

        "short_sections":
            short_sections,

        "content_score":
            content_score,

        "content_status":
            content_status,

        "content_suggestions":
            suggestions,
    }


# ============================================================
# CONTACT INFORMATION
# ============================================================

def extract_contact_information(text):

    email_match = re.search(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        text,
        re.IGNORECASE,
    )

    phone_match = re.search(
        r"(?:\+91[\s-]?)?[6-9]\d{9}\b",
        text,
    )

    linkedin_match = re.search(
        r"(?:https?://)?(?:www\.)?linkedin\.com/[^\s|,]+",
        text,
        re.IGNORECASE,
    )

    github_match = re.search(
        r"(?:https?://)?(?:www\.)?github\.com/[^\s|,]+",
        text,
        re.IGNORECASE,
    )

    all_urls = re.findall(
        r"https?://[^\s|,]+",
        text,
        re.IGNORECASE,
    )

    portfolio = None

    for url in all_urls:

        url_clean = url.rstrip(
            ".,;:)]}"
        )

        url_lower = url_clean.lower()

        if (
            "linkedin.com" not in url_lower
            and "github.com" not in url_lower
        ):

            portfolio = url_clean
            break

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    name = None

    excluded_words = {
        "resume",
        "curriculum",
        "vitae",
        "email",
        "phone",
        "mobile",
        "contact",
        "linkedin",
        "github",
        "portfolio",
        "profile",
        "objective",
        "software",
        "developer",
        "engineer",
        "student",
        "computer",
        "science",
        "technology",
        "python",
        "java",
        "javascript",
        "react",
    }

    for line in lines[:15]:

        cleaned = re.sub(
            r"[^A-Za-z .'-]",
            " ",
            line,
        )

        cleaned = re.sub(
            r"\s+",
            " ",
            cleaned,
        ).strip()

        words = cleaned.split()

        if not words:
            continue

        filtered_words = [
            word
            for word in words
            if word.lower()
            not in excluded_words
        ]

        candidate = " ".join(
            filtered_words
        ).strip()

        if (
            2 <= len(candidate.split()) <= 5
            and len(candidate) <= 50
            and all(
                re.fullmatch(
                    r"[A-Za-z][A-Za-z.'-]*",
                    word,
                )
                for word in candidate.split()
            )
        ):

            name = candidate

            break

    return {
        "name":
            name,

        "email":
            email_match.group(0)
            if email_match
            else None,

        "phone":
            phone_match.group(0)
            if phone_match
            else None,

        "linkedin":
            linkedin_match.group(0)
            if linkedin_match
            else None,

        "github":
            github_match.group(0)
            if github_match
            else None,

        "portfolio":
            portfolio,
    }


# ============================================================
# ATS KEYWORD ANALYSIS
# ============================================================

def analyze_ats_keywords(
    resume_text,
    job_text,
):

    job_text = clean_job_description(
        job_text
    )

    resume_lower = resume_text.lower()

    job_skills = extract_job_skills(
        job_text
    )

    matched_keywords = []
    missing_keywords = []

    # --------------------------------------------------------
    # Technical job keywords
    # --------------------------------------------------------

    for skill in job_skills:

        normalized = normalize_skill(
            skill
        )

        if skill_exists_in_text(
            normalized,
            resume_text,
        ):

            if normalized not in matched_keywords:

                matched_keywords.append(
                    normalized
                )

        else:

            if normalized not in missing_keywords:

                missing_keywords.append(
                    normalized
                )

    # --------------------------------------------------------
    # General job keywords
    # --------------------------------------------------------

    general_keywords = [
        "software developer",
        "software engineer",
        "problem solving",
        "communication",
        "leadership",
        "teamwork",
        "code review",
        "testing",
        "performance",
        "agile",
        "scrum",
        "database",
        "cloud",
    ]

    job_lower = job_text.lower()

    for keyword in general_keywords:

        if keyword not in job_lower:
            continue

        pattern = (
            r"(?<![a-zA-Z0-9])"
            + re.escape(keyword)
            + r"(?![a-zA-Z0-9])"
        )

        if re.search(
            pattern,
            resume_lower,
        ):

            if keyword not in matched_keywords:

                matched_keywords.append(
                    keyword
                )

        else:

            if keyword not in missing_keywords:

                missing_keywords.append(
                    keyword
                )

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    matched_keywords = list(
        dict.fromkeys(
            matched_keywords
        )
    )

    missing_keywords = [
        keyword
        for keyword in missing_keywords
        if keyword not in matched_keywords
    ]

    all_keywords = (
        matched_keywords
        + missing_keywords
    )

    if all_keywords:

        match_percentage = round(
            len(matched_keywords)
            / len(all_keywords)
            * 100,
            2,
        )

    else:

        match_percentage = 0

    if match_percentage >= 80:

        ats_status = "Strong ATS Keyword Match"

    elif match_percentage >= 60:

        ats_status = "Good ATS Keyword Match"

    elif match_percentage >= 40:

        ats_status = "Moderate ATS Keyword Match"

    else:

        ats_status = "Weak ATS Keyword Match"

    return {
        "ats_keywords":
            all_keywords,

        "total_keywords":
            len(all_keywords),

        "matched_keywords":
            matched_keywords,

        "missing_keywords":
            missing_keywords,

        "keyword_match_percentage":
            match_percentage,

        "ats_status":
            ats_status,
    }


# ============================================================
# OVERALL ATS SCORE
# ============================================================

def calculate_overall_ats_score(
    keyword_score,
    skill_score,
    structure_score,
    content_score,
):

    ats_score = round(
        (
            keyword_score * 0.30
            + skill_score * 0.35
            + structure_score * 0.20
            + content_score * 0.15
        ),
        2,
    )

    if ats_score >= 80:

        rating = "Strong"

    elif ats_score >= 60:

        rating = "Good"

    elif ats_score >= 40:

        rating = "Moderate"

    else:

        rating = "Weak"

    suggestions = []

    if keyword_score < 60:

        suggestions.append(
            "Improve relevant ATS keyword coverage by naturally "
            "including important job description terms that accurately "
            "represent your experience."
        )

    if skill_score < 60:

        suggestions.append(
            "Strengthen coverage of required and preferred technical skills."
        )

    if structure_score < 80:

        suggestions.append(
            "Improve resume section structure and completeness."
        )

    if content_score < 70:

        suggestions.append(
            "Add stronger project, experience, achievement, and "
            "certification details where applicable."
        )

    return {
        "ats_score":
            ats_score,

        "ats_rating":
            rating,

        "ats_breakdown": {
            "keyword_score":
                keyword_score,

            "skill_score":
                skill_score,

            "structure_score":
                structure_score,

            "content_score":
                content_score,
        },

        "ats_score_suggestions":
            suggestions,
    }


# ============================================================
# MAIN ANALYSIS ENDPOINT
# ============================================================

@app.post("/analyze-resume")
async def analyze_resume(

    file: UploadFile = File(...),

    # New frontend field
    job_description: str = Form(""),

    # Compatibility with older frontend/backend
    job_text: str = Form(""),
):

    # --------------------------------------------------------
    # Choose whichever job description was supplied
    # --------------------------------------------------------

    final_job_description = (
        job_description.strip()
        if job_description.strip()
        else job_text.strip()
    )

    # --------------------------------------------------------
    # FILE VALIDATION
    # --------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Resume file is required.",
        )

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    file_bytes = await file.read()

    if not file_bytes:

        raise HTTPException(
            status_code=400,
            detail="Uploaded PDF is empty.",
        )

    resume_text = extract_pdf_text(
        file_bytes
    )

    if not resume_text.strip():

        raise HTTPException(
            status_code=400,
            detail="No readable text found in the PDF.",
        )

    # --------------------------------------------------------
    # BASIC ANALYSIS
    # --------------------------------------------------------

    sections = detect_sections(
        resume_text
    )

    word_counts = calculate_section_word_counts(
        resume_text
    )

    resume_skills = extract_skills(
        resume_text
    )

    # --------------------------------------------------------
    # JOB ANALYSIS
    # --------------------------------------------------------

    job_skills = extract_required_preferred_skills(
        final_job_description
    )

    required_skills = job_skills[
        "required"
    ]

    preferred_skills = job_skills[
        "preferred"
    ]

    # --------------------------------------------------------
    # SKILL MATCHING
    # --------------------------------------------------------

    skill_match = match_skills(
        resume_skills,
        required_skills,
        preferred_skills,
    )

    matched_required = skill_match[
        "matched_required"
    ]

    missing_required = skill_match[
        "missing_required"
    ]

    matched_preferred = skill_match[
        "matched_preferred"
    ]

    missing_preferred = skill_match[
        "missing_preferred"
    ]

    weighted_match_percentage = skill_match[
        "weighted_match_percentage"
    ]

    resume_status = skill_match[
        "resume_status"
    ]

    # --------------------------------------------------------
    # SKILL GAPS
    # --------------------------------------------------------

    skill_gap_categories = categorize_skill_gaps(
        missing_required,
        missing_preferred,
    )

    skill_gaps = [
        skill
        for skills in skill_gap_categories.values()
        for skill in skills
    ]

    # --------------------------------------------------------
    # RESUME STRENGTH
    # --------------------------------------------------------

    resume_strength = analyze_resume_strength(
        weighted_match_percentage
    )

    # --------------------------------------------------------
    # RESUME QUALITY
    # --------------------------------------------------------

    resume_quality_base = analyze_resume_quality(
        sections
    )

    section_score = resume_quality_base[
        "section_score"
    ]

    # --------------------------------------------------------
    # CONTENT ANALYSIS
    # --------------------------------------------------------

    content_analysis = analyze_resume_content(
        word_counts,
        resume_text,
    )

    content_score = content_analysis[
        "content_score"
    ]

    # --------------------------------------------------------
    # CONTACT INFORMATION
    # --------------------------------------------------------

    contact_information = extract_contact_information(
        resume_text
    )

    # --------------------------------------------------------
    # ATS KEYWORD ANALYSIS
    # --------------------------------------------------------

    ats_keywords = analyze_ats_keywords(
        resume_text,
        final_job_description,
    )

    keyword_score = ats_keywords[
        "keyword_match_percentage"
    ]

    # --------------------------------------------------------
    # OVERALL ATS
    # --------------------------------------------------------

    overall_ats = calculate_overall_ats_score(
        keyword_score=keyword_score,
        skill_score=weighted_match_percentage,
        structure_score=section_score,
        content_score=content_score,
    )

    ats_score = overall_ats[
        "ats_score"
    ]

    # --------------------------------------------------------
    # STEP 34
    # --------------------------------------------------------

    improvement_plan = generate_improvement_plan(
        missing_required=missing_required,
        missing_preferred=missing_preferred,
        missing_keywords=ats_keywords[
            "missing_keywords"
        ],
        content_suggestions=content_analysis[
            "content_suggestions"
        ],
        resume_status=resume_status,
        ats_score=ats_score,
    )

    # --------------------------------------------------------
    # STEP 35
    # --------------------------------------------------------

    bullet_analysis_base = analyze_resume_bullets(
        resume_text
    )

    bullet_analysis = {
        **bullet_analysis_base,

        "score":
            bullet_analysis_base.get(
                "action_verb_percentage",
                0,
            ),
    }

    # --------------------------------------------------------
    # STEP 36
    # --------------------------------------------------------

    achievement_analysis_base = analyze_achievements(
        resume_text
    )

    achievement_analysis = {
        **achievement_analysis_base,

        "quantified_count":
            achievement_analysis_base.get(
                "quantified_lines",
                0,
            ),

        "achievement_count":
            achievement_analysis_base.get(
                "achievement_lines",
                0,
            ),

        "status":
            achievement_analysis_base.get(
                "achievement_status",
                "Limited Quantified Achievements",
            ),
    }

    # --------------------------------------------------------
    # STEP 37
    # --------------------------------------------------------

    section_scores = calculate_section_scores(
        word_counts=word_counts,
        resume_sections=sections,
    )

    overall_section_score = section_scores.get(
        "overall_section_score",
        section_score,
    )

    # --------------------------------------------------------
    # STEP 38
    # --------------------------------------------------------

    job_title_alignment = analyze_job_title_alignment(
        resume_text=resume_text,
        job_text=final_job_description,
    )

    # --------------------------------------------------------
    # STEP 39
    # --------------------------------------------------------

    resume_health = generate_resume_health_report(
        ats_score=ats_score,
        content_score=content_score,
        section_score=overall_section_score,
        weighted_match_percentage=weighted_match_percentage,
        bullet_analysis=bullet_analysis,
        achievement_analysis=achievement_analysis,
        job_alignment=job_title_alignment,
    )

    health_score = resume_health.get(
        "health_score",
        resume_health.get(
            "resume_health_score",
            0,
        ),
    )

    # --------------------------------------------------------
    # STEP 40
    # --------------------------------------------------------

    analysis_summary = generate_analysis_summary(
        resume_status=resume_status,
        ats_score=ats_score,
        weighted_match_percentage=weighted_match_percentage,
        content_score=content_score,
        health_score=health_score,
    )

    # --------------------------------------------------------
    # RESUME QUALITY COMPATIBILITY OBJECT
    # --------------------------------------------------------

    resume_quality = {
        **resume_quality_base,

        "structure_score":
            resume_quality_base.get(
                "section_score",
                0,
            ),

        "structure_quality":
            resume_quality_base.get(
                "quality_status",
                "N/A",
            ),

        "project_count":
            content_analysis.get(
                "project_count",
                0,
            ),

        "total_lines":
            achievement_analysis.get(
                "total_resume_lines",
                len(
                    resume_text.splitlines()
                ),
            ),

        "content_score":
            content_score,
    }

    # --------------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------------

    return {

        "filename":
            file.filename,

        "contact_information":
            contact_information,

        "resume_text":
            resume_text,

        "resume_sections":
            sections,

        "section_word_counts":
            word_counts,

        "word_counts":
            word_counts,

        "resume_skills":
            resume_skills,

        # ----------------------------------------------------
        # JOB REQUIREMENTS
        # ----------------------------------------------------

        "job_requirements": {
            "required":
                required_skills,

            "preferred":
                preferred_skills,
        },

        "required_skills":
            required_skills,

        "preferred_skills":
            preferred_skills,

        # ----------------------------------------------------
        # SKILL MATCHING
        # ----------------------------------------------------

        "skill_matching": {

            "matched_required":
                matched_required,

            "missing_required":
                missing_required,

            "matched_preferred":
                matched_preferred,

            "missing_preferred":
                missing_preferred,

            "weighted_match_percentage":
                weighted_match_percentage,

            "resume_status":
                resume_status,
        },

        # Compatibility names
        "matched_required_skills":
            matched_required,

        "missing_required_skills":
            missing_required,

        "matched_preferred_skills":
            matched_preferred,

        "missing_preferred_skills":
            missing_preferred,

        "weighted_match_percentage":
            weighted_match_percentage,

        "match_status":
            resume_status,

        # ----------------------------------------------------
        # SKILL GAPS
        # ----------------------------------------------------

        "skill_gaps":
            skill_gaps,

        "skill_gap_categories":
            skill_gap_categories,

        # ----------------------------------------------------
        # RESUME STRENGTH
        # ----------------------------------------------------

        "resume_strength":
            resume_strength,

        "resume_status":
            resume_status,

        "suggestions":
            resume_strength[
                "suggestions"
            ],

        # ----------------------------------------------------
        # RESUME QUALITY
        # ----------------------------------------------------

        "resume_quality":
            resume_quality,

        "missing_sections":
            resume_quality[
                "missing_sections"
            ],

        "quality_status":
            resume_quality[
                "quality_status"
            ],

        # ----------------------------------------------------
        # CONTENT
        # ----------------------------------------------------

        "resume_content_analysis":
            content_analysis,

        "summary_status":
            content_analysis[
                "summary_status"
            ],

        "project_count":
            content_analysis[
                "project_count"
            ],

        "project_status":
            content_analysis[
                "project_status"
            ],

        "experience_status":
            content_analysis[
                "experience_status"
            ],

        "certification_status":
            content_analysis[
                "certification_status"
            ],

        "content_score":
            content_score,

        "content_status":
            content_analysis[
                "content_status"
            ],

        "content_suggestions":
            content_analysis[
                "content_suggestions"
            ],

        # ----------------------------------------------------
        # ATS KEYWORDS
        # ----------------------------------------------------

        "ats_keyword_analysis":
            ats_keywords,

        "ats_keywords":
            ats_keywords[
                "ats_keywords"
            ],

        "matched_keywords":
            ats_keywords[
                "matched_keywords"
            ],

        "missing_keywords":
            ats_keywords[
                "missing_keywords"
            ],

        "keyword_match_percentage":
            keyword_score,

        "ats_status":
            ats_keywords[
                "ats_status"
            ],

        # ----------------------------------------------------
        # OVERALL ATS
        # ----------------------------------------------------

        "overall_ats":
            overall_ats,

        "ats_score":
            ats_score,

        "ats_rating":
            overall_ats[
                "ats_rating"
            ],

        "ats_breakdown":
            overall_ats[
                "ats_breakdown"
            ],

        # ----------------------------------------------------
        # STEP 34
        # ----------------------------------------------------

        "step_34_improvement_plan":
            improvement_plan,

        "improvement_plan":
            improvement_plan,

        # ----------------------------------------------------
        # STEP 35
        # ----------------------------------------------------

        "step_35_bullet_analysis":
            bullet_analysis,

        "bullet_analysis":
            bullet_analysis,

        # ----------------------------------------------------
        # STEP 36
        # ----------------------------------------------------

        "step_36_achievement_analysis":
            achievement_analysis,

        "achievement_analysis":
            achievement_analysis,

        # ----------------------------------------------------
        # STEP 37
        # ----------------------------------------------------

        "step_37_section_scores":
            section_scores,

        "section_scores":
            section_scores.get(
                "section_scores",
                {},
            ),

        # ----------------------------------------------------
        # STEP 38
        # ----------------------------------------------------

        "step_38_job_title_alignment":
            job_title_alignment,

        "step_38_job_role_alignment":
            job_title_alignment,

        "job_title_alignment":
            job_title_alignment,

        # ----------------------------------------------------
        # STEP 39
        # ----------------------------------------------------

        "step_39_resume_health":
            resume_health,

        "resume_health":
            resume_health,

        # ----------------------------------------------------
        # STEP 40
        # ----------------------------------------------------

        "step_40_analysis_summary":
            analysis_summary,

        "analysis_summary":
            analysis_summary,
    }