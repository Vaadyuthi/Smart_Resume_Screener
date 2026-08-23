import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

load_dotenv()

from .database import Base, engine, get_db
from .models import Resume, ScreeningResult
from .schemas import ScreeningRequest
from .services.extractor import dumps, extract_structured, extract_text
from .services.matcher import fallback_match, match_resume

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Resume Screener")

# Absolute path resolution
ROOT_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = ROOT_DIR / os.getenv("UPLOAD_DIR", "uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Mount static and templates
app.mount("/static", StaticFiles(directory=str(ROOT_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(ROOT_DIR / "app" / "templates"))

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Smart Resume Screener"}

@app.post("/api/resumes")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    extension = Path(file.filename or "").suffix.lower()
    if extension not in {".pdf", ".txt", ".md"}:
        raise HTTPException(status_code=400, detail="Only PDF, TXT and MD files are supported.")

    content = await file.read()
    filename = Path(file.filename or "resume").name
    file_path = UPLOAD_DIR / filename
    file_path.write_bytes(content)

    try:
        text = extract_text(str(file_path))
        structured = extract_structured(text)
    except Exception as error:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=str(error))

    resume = Resume(
        filename=filename,
        name=structured["name"],
        email=structured["email"],
        phone=structured["phone"],
        skills=dumps(structured["skills"]),
        education=dumps(structured["education"]),
        experience=dumps(structured["experience"]),
        raw_text=structured["raw_text"]
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {
        "id": resume.id,
        "filename": resume.filename,
        "name": resume.name,
        "email": resume.email,
        "skills": structured["skills"]
    }

@app.get("/api/resumes")
def list_resumes(db: Session = Depends(get_db)):
    resumes = db.query(Resume).order_by(Resume.id.desc()).all()
    return [
        {
            "id": r.id,
            "filename": r.filename,
            "name": r.name,
            "email": r.email,
            "skills": json.loads(r.skills)
        }
        for r in resumes
    ]

@app.post("/api/screen")
async def screen_candidates(request: ScreeningRequest, db: Session = Depends(get_db)):
    query = db.query(Resume)
    if request.resume_ids:
        query = query.filter(Resume.id.in_(request.resume_ids))

    resumes = query.all()
    if not resumes:
        raise HTTPException(status_code=404, detail="No resumes found.")

    pre_screened = []
    for resume in resumes:
        structured = {
            "name": resume.name,
            "email": resume.email,
            "skills": json.loads(resume.skills),
            "raw_text": resume.raw_text
        }
        quick_result = fallback_match(structured, request.job_description)
        pre_screened.append((resume, structured, quick_result))

    pre_screened.sort(key=lambda x: x[2]["score"], reverse=True)

    results = []
    top_candidates = pre_screened[:25]
    remainder = pre_screened[25:]

    for resume, structured, _ in top_candidates:
        match = await match_resume(structured, request.job_description)
        screening = ScreeningResult(
            resume_id=resume.id,
            job_description=request.job_description,
            score=match["score"],
            strengths=dumps(match["strengths"]),
            gaps=dumps(match["gaps"]),
            recommendation=match["recommendation"],
            justification=match["justification"]
        )
        db.add(screening)
        results.append({
            "resume_id": resume.id,
            "candidate_name": resume.name,
            **match
        })

    for resume, _, quick_result in remainder:
        results.append({
            "resume_id": resume.id,
            "candidate_name": resume.name,
            **quick_result
        })

    db.commit()
    results.sort(key=lambda item: item["score"], reverse=True)

    return {"count": len(results), "results": results}