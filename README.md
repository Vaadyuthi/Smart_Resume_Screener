# Smart Resume Screener

An end-to-end recruitment intelligence engine built with **FastAPI**, **PyMuPDF**, **SQLAlchemy**, and **LLaMA 3.1 (Groq)**. Engineered with a **Two-Tier Hybrid Architecture** to screen thousands of resumes in seconds while avoiding LLM rate limits and token costs.

---

## Architecture: Two-Tier High-Volume Pipeline

This platform resolves that bottleneck with a hybrid screening funnel:

1. **Tier 1 (Sub-Millisecond Heuristic Filter)**: Tokenizes, normalizes, and matches core technical skills, taxonomy aliases, and experience across the entire database in milliseconds.
2. **Tier 2 (Deep Semantic LLM Reasoning)**: Dispatches top-ranked candidates to `llama-3.1-8b-instant` for strict evidence-based fit scoring (1–10), justification analysis, strengths, and requirement gaps.

---

## Key Highlights

- **Multi-Format Extraction**: Ingests `.pdf`, `.txt`, and `.md` files; extracts contact details, skills, education, and experience.
- **Anti-Hallucination Guardrails**: System prompts strictly constrain the LLM to explicit resume evidence.
- **Zero-Setup Database**: Includes a dataset generation tool (`scripts/generate_dataset.py`) to pre-populate and benchmark hundreds of realistic candidate profiles instantly.
- **Interactive UI**: Dark-mode dashboard with real-time candidate search, live screening results, and single/bulk deletion tools.

---

## LLM Prompt Specification

```text
You are an expert technical recruiter and resume evaluation assistant.
Compare the candidate resume with the job description using ONLY explicit resume facts.

Rules:
1. Never invent skills, employers, degrees, or years of experience.
2. Evaluate technical alignment, experience relevance, and education.
3. Return fit score (1–10), strengths, gaps, recommendation, and justification.
4. Return ONLY valid JSON.

---

## Quickstart
1. Install Dependencies
Bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt

2. Configure Environment (.env)
Code snippet
LLM_API_KEY=your_groq_api_key_here
LLM_BASE_URL=[https://api.groq.com/openai/v1](https://api.groq.com/openai/v1)
LLM_MODEL=llama-3.1-8b-instant
DATABASE_URL=sqlite:///./resume_screener.db

3. Populate Database & Launch
Bash
python scripts/generate_dataset.py 100

# Start server
uvicorn app.main:app --reload --port 8000
Web App: http://127.0.0.1:8000

Swagger Docs: http://127.0.0.1:8000/docs
