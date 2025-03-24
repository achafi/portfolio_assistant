from pydantic import BaseModel
from typing import List


class WorkExperience(BaseModel):
    job_title: str
    company: str
    start_date: str
    end_date: str
    description: str


class Education(BaseModel):
    degree: str
    institution: str
    graduation_year: str


class Project(BaseModel):
    name: str
    description: str
    technologies: List[str]


class Certification(BaseModel):
    name: str
    issuing_organization: str


class CVInfo(BaseModel):
    work_experience: List[WorkExperience]
    education: List[Education]
    skills: List[str]
    projects: List[Project]
    certifications: List[Certification]


class CVReference(BaseModel):
    section: str  # Example: "work_experience", "skills", "education"
    details: str  # Summary of relevant data from `CVInfo`


class VisitorResponse(BaseModel):
    question: str
    answer: str
    references: List[CVReference]  # Where the answer is derived from
