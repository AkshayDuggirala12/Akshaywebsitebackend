from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import engine, SessionLocal
import models

# Auto-creates tables in PostgreSQL
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Akshay's Portfolio API")

# --- CORS SETUP ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# --- DATABASE DEPENDENCY ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- PYDANTIC SCHEMAS (For Data Validation) ---
class EducationCreate(BaseModel):
    degree: str
    institution: str
    year: str

class ProjectCreate(BaseModel):
    title: str
    description: str
    tech_stack: str
    link: str

class LeadCreate(BaseModel):
    name: str
    email: str
    message: str

class ExperienceCreate(BaseModel):
    role: str
    company: str
    duration: str
    location: str
    description: str
    technologies: str


# --- ENDPOINTS ---

@app.get("/")
def read_root():
    return {"message": "Backend connected to isolated CMD PostgreSQL server successfully!"}


# --- EDUCATION ---
@app.get("/education", tags=["Education"])
def get_education(db: Session = Depends(get_db)):
    return db.query(models.Education).all()

@app.post("/education", tags=["Education"])
def add_education(edu: EducationCreate, db: Session = Depends(get_db)):
    new_edu = models.Education(degree=edu.degree, institution=edu.institution, year=edu.year)
    db.add(new_edu)
    db.commit()
    db.refresh(new_edu)
    return new_edu


# --- PROJECTS ---
@app.get("/projects", tags=["Projects"])
def get_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).all()

@app.post("/projects", tags=["Projects"])
def add_project(project: ProjectCreate, db: Session = Depends(get_db)):
    new_project = models.Project(
        title=project.title, 
        description=project.description, 
        tech_stack=project.tech_stack, 
        link=project.link
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


# --- LEADS ---
@app.get("/leads", tags=["Leads"])
def get_leads(db: Session = Depends(get_db)):
    return db.query(models.Lead).all()

@app.post("/leads", tags=["Leads"])
def add_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    new_lead = models.Lead(name=lead.name, email=lead.email, message=lead.message)
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    return new_lead


# --- EXPERIENCE ---
@app.get("/experience", tags=["Experience"])
def get_experience(db: Session = Depends(get_db)):
    return db.query(models.Experience).all()

@app.post("/experience", tags=["Experience"])
def add_experience(exp: ExperienceCreate, db: Session = Depends(get_db)):
    new_exp = models.Experience(
        role=exp.role,
        company=exp.company,
        duration=exp.duration,
        location=exp.location,
        description=exp.description,
        technologies=exp.technologies
    )
    db.add(new_exp)
    db.commit()
    db.refresh(new_exp)
    return new_exp