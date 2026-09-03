import os
import secrets
from fastapi import FastAPI, Depends, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from dotenv import load_dotenv
from database import engine, SessionLocal
import models

load_dotenv()

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")
DOCS_USERNAME = os.getenv("DOCS_USERNAME")
DOCS_PASSWORD = os.getenv("DOCS_PASSWORD")

if not ADMIN_API_KEY:
    raise RuntimeError("ADMIN_API_KEY is not set in the environment (.env)")
if not DOCS_USERNAME or not DOCS_PASSWORD:
    raise RuntimeError("DOCS_USERNAME / DOCS_PASSWORD is not set in the environment (.env)")

# Auto-creates tables in PostgreSQL
models.Base.metadata.create_all(bind=engine)

# Docs are disabled by default here and re-added below behind Basic Auth
app = FastAPI(title="Akshay's Portfolio API", docs_url=None, redoc_url=None, openapi_url=None)

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

# --- ADMIN KEY DEPENDENCY (protects write endpoints) ---
def verify_admin_key(x_admin_key: str = Header(...)):
    if not secrets.compare_digest(x_admin_key, ADMIN_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin key",
        )

# --- BASIC AUTH FOR SWAGGER / REDOC / OPENAPI SCHEMA ---
security = HTTPBasic()

def verify_docs_access(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, DOCS_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, DOCS_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True

@app.get("/docs", include_in_schema=False)
def get_swagger(_: bool = Depends(verify_docs_access)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")

@app.get("/redoc", include_in_schema=False)
def get_redoc(_: bool = Depends(verify_docs_access)):
    return get_redoc_html(openapi_url="/openapi.json", title="redoc")

@app.get("/openapi.json", include_in_schema=False)
def get_openapi_json(_: bool = Depends(verify_docs_access)):
    return app.openapi()

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
def add_education(edu: EducationCreate, db: Session = Depends(get_db), _: None = Depends(verify_admin_key)):
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
def add_project(project: ProjectCreate, db: Session = Depends(get_db), _: None = Depends(verify_admin_key)):
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
def get_leads(db: Session = Depends(get_db), _: None = Depends(verify_admin_key)):
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
def add_experience(exp: ExperienceCreate, db: Session = Depends(get_db), _: None = Depends(verify_admin_key)):
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