import json
import re

from pathlib import Path

import fitz


SKILL_VOCAB = [

    "python",
    "java",
    "c",
    "c++",

    "javascript",
    "typescript",

    "react",
    "node.js",
    "nodejs",

    "fastapi",
    "flask",
    "django",

    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "redis",

    "docker",
    "kubernetes",

    "aws",
    "azure",
    "gcp",

    "git",
    "github",

    "machine learning",
    "deep learning",

    "nlp",
    "computer vision",

    "tensorflow",
    "pytorch",

    "pandas",
    "numpy",
    "scikit-learn",

    "llm",
    "rag",
    "generative ai",

    "rest api",

    "html",
    "css",

    "linux",

    "spark",

    "power bi",
    "tableau"
]


def extract_text(path: str) -> str:

    suffix = Path(path).suffix.lower()

    if suffix == ".pdf":

        text = []

        with fitz.open(path) as document:

            for page in document:

                text.append(
                    page.get_text()
                )

        return "\n".join(text)


    if suffix in {".txt", ".md"}:

        return Path(path).read_text(
            encoding="utf-8",
            errors="ignore"
        )


    raise ValueError(
        "Unsupported file type"
    )


def extract_structured(text: str) -> dict:

    clean_text = re.sub(
        r"[ \t]+",
        " ",
        text
    ).strip()


    lower_text = clean_text.lower()


    lines = [
        line.strip()
        for line in clean_text.splitlines()
        if line.strip()
    ]

    name = "Unknown"

    if lines:

        name = lines[0][:100]

        if name.lower() in {
            "resume",
            "curriculum vitae",
            "cv"
        }:

            if len(lines) > 1:
                name = lines[1][:100]

    # EMAIL
    email_match = re.search(
        r"[\w.+-]+@[\w-]+\.[\w.-]+",
        clean_text
    )

    email = ""

    if email_match:
        email = email_match.group(0)

    # PHONE
    phone_match = re.search(
        r"(?:\+?\d[\d ()-]{8,}\d)",
        clean_text
    )

    phone = ""

    if phone_match:
        phone = phone_match.group(0)

    # SKILLS
    skills = []

    for skill in SKILL_VOCAB:

        pattern = (
            r"(?<!\w)"
            + re.escape(skill)
            + r"(?!\w)"
        )

        if re.search(
            pattern,
            lower_text
        ):

            skills.append(skill)

    # SECTION EXTRACTION
    def extract_section(
        titles
    ):

        for title in titles:

            pattern = (
                r"\b"
                + re.escape(title)
                + r"\b"
            )

            match = re.search(
                pattern,
                lower_text
            )

            if not match:
                continue


            start = match.end()

            section = clean_text[
                start:start + 1500
            ]


            return [
                item.strip("•- ")
                for item in section.splitlines()
                if item.strip()
            ][:10]


        return []


    education = extract_section(
        [
            "education",
            "academic background"
        ]
    )


    experience = extract_section(
        [
            "experience",
            "work experience",
            "internship",
            "employment"
        ]
    )


    return {

        "name": name,

        "email": email,

        "phone": phone,

        "skills": skills,

        "education": education,

        "experience": experience,

        "raw_text": clean_text

    }


def dumps(value) -> str:

    return json.dumps(
        value,
        ensure_ascii=False
    )