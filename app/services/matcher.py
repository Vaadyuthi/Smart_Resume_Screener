import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

try:
    from groq import Groq
except ImportError:
    Groq = None

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

SKILL_ALIASES = {
    "python": ["python", "python3"],
    "java": ["java", "core java", "java se", "java ee"],
    "c": ["c programming", "c language"],
    "c++": ["c++", "cpp"],
    "c#": ["c#", "c sharp"],
    "javascript": ["javascript", "js", "ecmascript"],
    "typescript": ["typescript", "ts"],
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "react": ["react", "react.js", "reactjs"],
    "angular": ["angular", "angularjs"],
    "vue": ["vue", "vue.js", "vuejs"],
    "node.js": ["node", "node.js", "nodejs"],
    "express.js": ["express", "express.js", "expressjs"],
    "flask": ["flask"],
    "django": ["django"],
    "spring": ["spring", "spring boot", "springboot"],
    "fastapi": ["fastapi", "fast api"],
    "sql": ["sql", "structured query language"],
    "mysql": ["mysql"],
    "postgresql": ["postgresql", "postgres"],
    "mongodb": ["mongodb", "mongo db", "mongo"],
    "redis": ["redis"],
    "aws": ["aws", "amazon web services"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "docker": ["docker", "docker containers"],
    "kubernetes": ["kubernetes", "k8s"],
    "git": ["git"],
    "github": ["github", "github actions"],
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning", "dl"],
    "rest api": ["rest api", "restful api", "rest apis"]
}

STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "with", "for", "from", "into", "using", "use",
    "work", "working", "role", "job", "position", "candidate", "company", "team", "will",
    "should", "must", "can", "have", "has", "this", "that", "their", "your", "our", "are",
    "is", "was", "were", "to", "of", "in", "on", "at", "by", "required", "requirements"
}

def normalize_text(text: Any) -> str:
    if text is None:
        return ""
    text = str(text).replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()

def normalize_for_matching(text: str) -> str:
    text = normalize_text(text).lower()
    replacements = {
        "node.js": "nodejs", "node js": "nodejs",
        "react.js": "reactjs", "react js": "reactjs",
        "express.js": "expressjs", "express js": "expressjs",
        "c++": "cplusplus", "c#": "csharp",
        "machine-learning": "machine learning"
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def tokenize(text: str) -> List[str]:
    text = normalize_for_matching(text)
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]*", text)
    return [t.lower().strip(".,;:!?()[]{}<>\"'`") for t in tokens if t.lower() not in STOP_WORDS and len(t) > 2]

def phrase_present(text: str, phrase: str) -> bool:
    escaped = re.escape(normalize_for_matching(phrase))
    return bool(re.search(r"(?<![a-zA-Z0-9])" + escaped + r"(?![a-zA-Z0-9])", normalize_for_matching(text)))

def extract_skills(text: str) -> List[str]:
    norm = normalize_for_matching(text)
    found = [canonical for canonical, aliases in SKILL_ALIASES.items() if any(phrase_present(norm, a) for a in aliases)]
    return sorted(list(set(found)))

def extract_experience_years(text: str) -> Optional[float]:
    patterns = [r"(\d+(?:\.\d+)?)\+?\s*years?\s*(?:of)?\s*experience", r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\+?\s*years?"]
    values = []
    for pattern in patterns:
        matches = re.findall(pattern, text.lower())
        for v in matches:
            try:
                values.append(float(v))
            except ValueError:
                pass
    return max(values) if values else None

def fallback_match(resume_data: Dict[str, Any], job_description: str) -> Dict[str, Any]:
    resume_text = resume_data.get("raw_text", "")
    resume_skills = set(resume_data.get("skills", []) or extract_skills(resume_text))
    jd_skills = set(extract_skills(job_description))

    matched = sorted(resume_skills.intersection(jd_skills))
    missing = sorted(jd_skills.difference(resume_skills))
    skill_score = (len(matched) / len(jd_skills) * 10.0) if jd_skills else 5.0

    resume_exp = extract_experience_years(resume_text)
    jd_exp = extract_experience_years(job_description)
    exp_multiplier = 1.0
    if jd_exp and resume_exp:
        exp_multiplier = min(1.2, resume_exp / jd_exp)

    final_score = round(min(10.0, max(1.0, skill_score * exp_multiplier)), 1)
    
    if final_score >= 8.0:
        rec = "Strong Match"
    elif final_score >= 6.5:
        rec = "Match"
    elif final_score >= 4.5:
        rec = "Partial Match"
    else:
        rec = "Low Match"

    return {
        "score": final_score,
        "strengths": [f"Demonstrates required skill: {s}" for s in matched],
        "gaps": [f"Missing required skill: {s}" for s in missing],
        "recommendation": rec,
        "justification": f"Candidate matches {len(matched)}/{len(jd_skills)} required core skills with an estimated fit score of {final_score}/10."
    }

async def match_resume(resume_data: Dict[str, Any], job_description: str) -> Dict[str, Any]:
    """Evaluates candidate fit via LLM with automatic fallback."""
    from .llm import llm_match
    
    resume_text = resume_data.get("raw_text", "")
    llm_res = await llm_match(resume_text=resume_text, job_description=job_description)
    
    if llm_res:
        return {
            "score": round(llm_res.score, 1),
            "strengths": llm_res.strengths,
            "gaps": llm_res.gaps,
            "recommendation": llm_res.recommendation,
            "justification": llm_res.justification
        }
    
    return fallback_match(resume_data, job_description)