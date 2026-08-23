import os
import sys
from pathlib import Path
from sqlalchemy.orm import Session

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal, engine, Base
from app.models import Resume
from app.services.extractor import extract_text, extract_structured, dumps

def bulk_import_resumes(directory_path: str, batch_size: int = 100):
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    
    source_dir = Path(directory_path)
    supported_files = list(source_dir.glob("**/*.pdf")) + list(source_dir.glob("**/*.txt")) + list(source_dir.glob("**/*.md"))
    
    total = len(supported_files)
    print(f"Found {total} resumes to ingest from: {directory_path}")
    
    resumes_to_add = []
    
    for idx, file_path in enumerate(supported_files, 1):
        try:
            text = extract_text(str(file_path))
            structured = extract_structured(text)
            
            resume = Resume(
                filename=file_path.name,
                name=structured["name"],
                email=structured["email"],
                phone=structured["phone"],
                skills=dumps(structured["skills"]),
                education=dumps(structured["education"]),
                experience=dumps(structured["experience"]),
                raw_text=structured["raw_text"]
            )
            resumes_to_add.append(resume)
            
            if len(resumes_to_add) >= batch_size:
                db.bulk_save_objects(resumes_to_add)
                db.commit()
                resumes_to_add.clear()
                print(f"Ingested {idx}/{total} resumes...")
                
        except Exception as e:
            print(f"Failed to parse {file_path.name}: {e}")

    if resumes_to_add:
        db.bulk_save_objects(resumes_to_add)
        db.commit()
        
    db.close()
    print(f"Import finished: {total} candidates added to database.")

if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "uploads"
    bulk_import_resumes(folder)