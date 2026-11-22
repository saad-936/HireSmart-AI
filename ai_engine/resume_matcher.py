
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Skills database
SKILLS_DATABASE = [
    "python",
    "java",
    "javascript",
    "c++",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "natural language processing",
    "computer vision",
    "data science",
    "data analysis",
    "sql",
    "mysql",
    "mongodb",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "flask",
    "django",
    "html",
    "css",
    "react",
    "git",
    "docker",
    "aws",
    "excel",
    "power bi",
    "communication",
    "problem solving"
]


def extract_skills(text):
    """
    Extract known skills from resume or job description.
    """

    if not text:
        return []

    text = text.lower()
    found_skills = []

    for skill in SKILLS_DATABASE:

        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text):
            found_skills.append(skill)

    return found_skills


def calculate_match(resume_text, job_description):
    """
    Calculate resume similarity and skills match percentage.
    """

    if not resume_text or not job_description:
        return {
            "match_percentage": 0,
            "skill_match_percentage": 0,
            "resume_skills": [],
            "required_skills": [],
            "matched_skills": [],
            "missing_skills": []
        }

    # Extract skills
    resume_skills = extract_skills(resume_text)
    required_skills = extract_skills(job_description)

    # Find matched skills
    matched_skills = [
        skill for skill in required_skills
        if skill in resume_skills
    ]

    # Find missing skills
    missing_skills = [
        skill for skill in required_skills
        if skill not in resume_skills
    ]

    # Calculate skills match percentage
    if required_skills:
        skill_match_percentage = round(
            (len(matched_skills) / len(required_skills)) * 100,
            2
        )
    else:
        skill_match_percentage = 0

    # Calculate TF-IDF text similarity
    vectorizer = TfidfVectorizer()

    try:
        vectors = vectorizer.fit_transform([
            resume_text,
            job_description
        ])

        similarity = cosine_similarity(
            vectors[0:1],
            vectors[1:2]
        )[0][0]

        match_percentage = round(
            float(similarity) * 100,
            2
        )

    except ValueError:
        match_percentage = 0

    return {
        "match_percentage": match_percentage,
        "skill_match_percentage": skill_match_percentage,
        "resume_skills": resume_skills,
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }
