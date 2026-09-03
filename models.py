from sqlalchemy import Column, Integer, String, Text
from database import Base

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    message = Column(Text)

class Education(Base):
    __tablename__ = "education"
    
    id = Column(Integer, primary_key=True, index=True)
    degree = Column(String)
    institution = Column(String)
    year = Column(String)

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    tech_stack = Column(String)
    link = Column(String)

class Experience(Base):
    __tablename__ = "experience"
    
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, index=True)
    company = Column(String, index=True)
    duration = Column(String)
    location = Column(String)
    description = Column(Text)
    technologies = Column(String)