import os
import sys
import random
from pathlib import Path
from sqlalchemy.orm import Session

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal, engine, Base
from app.models import Resume, ScreeningResult
from app.services.extractor import dumps

FIRST_NAMES = [
    # Male
    "Aarav", "Aditya", "Arjun", "Rohan", "Rahul", "Vikram", "Siddharth", "Sai",
    "Karthik", "Rishi", "Varun", "Pranav", "Naveen", "Abhishek", "Harsha", 
    "Venkat", "Srikanth", "Anil", "Suresh", "Manoj", "Teja", "Gautam", 
    "Surya", "Nikhil", "Tarun", "Kiran", "Akhil", "Chaitanya", "Vamsi", "Dinesh",
    "Praneeth", "Manish", "Harish", "Deepak", "Vivek", "Vishal", "Ajay", "Raghav",
    # Female
    "Priya", "Sneha", "Ananya", "Kavya", "Pooja", "Meera", "Tanvi", "Neha",
    "Swathi", "Divya", "Anusha", "Deepika", "Bhavana", "Keerthi", "Lavanya",
    "Sravani", "Harini", "Pavithra", "Aishwarya", "Shruti", "Ritu", "Pallavi",
    "Vaishnavi", "Meghana", "Radhika", "Samyuktha", "Nandini", "Pranathi", "Sandhya"
]

LAST_NAMES = [
    "Reddy", "Rao", "Chowdary", "Nair", "Iyer", "Iyengar", "Menon", "Pillai",
    "Murthy", "Naidu", "Varma", "Goud", "Babu", "Hegde", "Shetty", "Gowda",
    "Sharma", "Verma", "Patel", "Mehta", "Gupta", "Agarwal", "Jain", "Shah",
    "Mishra", "Pandey", "Chopra", "Malhotra", "Bhatia", "Kapoor", "Saxena",
    "Mukherjee", "Banerjee", "Chatterjee", "Bose", "Dutta", "Das", "Sen",
    "Yadav", "Singh", "Kumar", "Thakur", "Joshi", "Kulkarni", "Deshmukh"
]

ROLES_SKILLS = [
    {
        "role": "Full Stack Developer",
        "skills": ["Python", "FastAPI", "React", "JavaScript", "TypeScript", "PostgreSQL", "Docker", "Git", "REST API", "Tailwind CSS"],
        "summary": "Full Stack Engineer experienced with React interfaces, Python FastAPI microservices, and PostgreSQL database optimization."
    },
    {
        "role": "Machine Learning Engineer",
        "skills": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-Learn", "NLP", "Git"],
        "summary": "ML Engineer with a practical focus on predictive modeling, NLP pipelines, data preprocessing, and model deployment using REST APIs."
    },
    {
        "role": "Backend Engineer",
        "skills": ["Python", "Django", "Flask", "SQL", "MySQL", "PostgreSQL", "Redis", "Docker", "REST API", "Linux", "Microservices"],
        "summary": "Backend specialist focused on high-throughput REST APIs, database indexing, caching strategies, and containerized architectures."
    },
    {
        "role": "DevOps & Cloud Engineer",
        "skills": ["AWS", "Azure", "Docker", "Kubernetes", "Linux", "Git", "GitHub Actions", "Python", "CI/CD", "Terraform"],
        "summary": "Cloud practitioner skilled in AWS infrastructure orchestration, CI/CD pipeline automation, and Docker container security."
    },
    {
        "role": "Data Analyst / Scientist",
        "skills": ["Python", "SQL", "Pandas", "NumPy", "Power BI", "Tableau", "Data Analysis", "Excel", "Scikit-Learn"],
        "summary": "Data analyst proficient in business intelligence dashboarding, statistical modeling, exploratory data analysis, and SQL queries."
    }
]

DEGREES = [
    "B.Tech in Computer Science and Engineering",
    "B.Tech in Information Technology",
    "B.E in Computer Science",
    "B.Tech in Artificial Intelligence & Data Science",
    "M.Tech in Software Engineering",
    "Master of Computer Applications (MCA)"
]

def generate_indian_dataset(target_count: int = 100):
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    print("Clearing existing records...")
    db.query(ScreeningResult).delete()
    db.query(Resume).delete()
    db.commit()

    print(f"Generating exactly {target_count} Indian candidate profiles...")
    resumes = []

    for _ in range(target_count):
        fname = random.choice(FIRST_NAMES)
        lname = random.choice(LAST_NAMES)
        name = f"{fname} {lname}"
        
        email = f"{fname.lower()}.{lname.lower()}{random.randint(10, 999)}@gmail.com"
        phone = f"+91 {random.choice([6, 7, 8, 9])}{random.randint(100000000, 999999999)}"
        
        role_profile = random.choice(ROLES_SKILLS)
        
        selected_skills = random.sample(role_profile["skills"], k=random.randint(4, len(role_profile["skills"])))
        selected_skills_lower = [s.lower() for s in selected_skills]
        
        years_exp = random.choice([0.5, 1, 2, 3, 4, 5])
        degree = random.choice(DEGREES)

        raw_text = f"""
{name}
Email: {email} | Phone: {phone}
Role: {role_profile['role']}

Professional Summary:
{role_profile['summary']}

Technical Skills:
{", ".join(selected_skills)}

Experience:
- {role_profile['role']} ({years_exp} years of experience)
- Built production applications, automated workflows, and handled backend databases.

Education:
- {degree} (Graduated 2025)
"""

        resume = Resume(
            filename=f"{fname.lower()}_{lname.lower()}_resume.txt",
            name=name,
            email=email,
            phone=phone,
            skills=dumps(selected_skills_lower),
            education=dumps([degree]),
            experience=dumps([f"{role_profile['role']} ({years_exp} yrs)"]),
            raw_text=raw_text.strip()
        )
        resumes.append(resume)

    db.bulk_save_objects(resumes)
    db.commit()
    db.close()

    print(f"Database reset and successfully loaded with {target_count} Indian candidates.")

if __name__ == "__main__":
    generate_indian_dataset(100)