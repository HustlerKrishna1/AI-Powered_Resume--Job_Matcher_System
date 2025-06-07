from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uuid
from datetime import datetime
import re
import io
try:
    import PyPDF2
except ImportError:
    # Try alternative import for newer versions
    from PyPDF2 import PdfReader as PyPDF2Reader
import docx
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import urllib.parse

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class ResumeProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    skills: List[str]
    experience_years: int
    education: str
    certifications: List[str]
    raw_text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class JobMatch(BaseModel):
    id: str
    title: str
    company: str
    required_skills: List[str]
    experience_required: int
    description: str
    location: str
    salary_range: str
    fit_score: float
    matched_skills: List[str]
    missing_skills: List[str]

class LearningRecommendation(BaseModel):
    skill: str
    google_search_url: str
    priority: str  # "high", "medium", "low"

# Sample job database
SAMPLE_JOBS = [
    {
        "id": "job_1",
        "title": "Senior Python Developer",
        "company": "TechCorp Inc",
        "required_skills": ["python", "django", "fastapi", "postgresql", "docker", "aws", "git", "testing"],
        "experience_required": 5,
        "description": "We're looking for a senior Python developer to join our backend team. You'll be working on scalable web applications using modern Python frameworks.",
        "location": "Remote",
        "salary_range": "$120k - $150k"
    },
    {
        "id": "job_2", 
        "title": "Frontend React Developer",
        "company": "StartupXYZ",
        "required_skills": ["react", "javascript", "typescript", "css", "html", "redux", "webpack", "testing"],
        "experience_required": 3,
        "description": "Join our growing team to build beautiful, responsive user interfaces using React and modern JavaScript.",
        "location": "San Francisco, CA",
        "salary_range": "$90k - $120k"
    },
    {
        "id": "job_3",
        "title": "Full Stack Engineer",
        "company": "InnovateLabs",
        "required_skills": ["nodejs", "react", "mongodb", "express", "javascript", "css", "git", "agile"],
        "experience_required": 4,
        "description": "Looking for a versatile full-stack engineer to work on both frontend and backend of our SaaS platform.",
        "location": "Austin, TX",
        "salary_range": "$100k - $130k"
    },
    {
        "id": "job_4",
        "title": "Data Scientist",
        "company": "DataDriven Co",
        "required_skills": ["python", "machine learning", "pandas", "numpy", "scikit-learn", "sql", "statistics", "jupyter"],
        "experience_required": 3,
        "description": "Analyze large datasets and build predictive models to drive business insights and decision making.",
        "location": "New York, NY", 
        "salary_range": "$110k - $140k"
    },
    {
        "id": "job_5",
        "title": "DevOps Engineer",
        "company": "CloudFirst Solutions",
        "required_skills": ["aws", "docker", "kubernetes", "terraform", "jenkins", "linux", "python", "monitoring"],
        "experience_required": 4,
        "description": "Manage cloud infrastructure and deployment pipelines for our microservices architecture.",
        "location": "Seattle, WA",
        "salary_range": "$115k - $145k"
    },
    {
        "id": "job_6",
        "title": "Machine Learning Engineer",
        "company": "AI Innovations",
        "required_skills": ["python", "tensorflow", "pytorch", "machine learning", "deep learning", "mlops", "docker", "aws"],
        "experience_required": 4,
        "description": "Build and deploy machine learning models at scale for our AI-powered products.",
        "location": "Remote",
        "salary_range": "$130k - $160k"
    }
]

# Utility functions
def extract_text_from_pdf(file_content):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

def extract_text_from_docx(file_content):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(io.BytesIO(file_content))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading DOCX: {str(e)}")

def extract_skills_from_text(text):
    """Extract skills from resume text using pattern matching"""
    # Common tech skills pattern
    tech_skills = [
        "python", "java", "javascript", "typescript", "react", "angular", "vue",
        "nodejs", "express", "django", "fastapi", "flask", "spring", "html", "css",
        "sql", "mongodb", "postgresql", "mysql", "redis", "docker", "kubernetes",
        "aws", "azure", "gcp", "git", "jenkins", "terraform", "linux", "windows",
        "machine learning", "deep learning", "tensorflow", "pytorch", "pandas",
        "numpy", "scikit-learn", "jupyter", "r", "matlab", "tableau", "power bi",
        "agile", "scrum", "testing", "unit testing", "integration testing",
        "webpack", "redux", "graphql", "rest api", "microservices", "devops",
        "ci/cd", "monitoring", "elasticsearch", "kafka", "spark", "hadoop",
        "blockchain", "solidity", "php", "ruby", "go", "rust", "swift", "kotlin"
    ]
    
    text_lower = text.lower()
    found_skills = []
    
    for skill in tech_skills:
        if skill in text_lower:
            found_skills.append(skill)
    
    return list(set(found_skills))  # Remove duplicates

def extract_experience_years(text):
    """Extract years of experience from resume text"""
    patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'experience\s*[:\-]?\s*(\d+)\+?\s*years?',
        r'(\d+)\+?\s*years?\s*in\s*(?:software|development|programming)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text.lower())
        if matches:
            return int(matches[0])
    
    # Default fallback based on text length and complexity
    if len(text) > 2000:
        return 3
    elif len(text) > 1000:
        return 2
    else:
        return 1

def extract_basic_info(text):
    """Extract name and email from resume text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    email = emails[0] if emails else "Not found"
    
    # Simple name extraction (first line often contains name)
    lines = text.strip().split('\n')
    name = "Not found"
    for line in lines[:5]:  # Check first 5 lines
        line = line.strip()
        if len(line) > 2 and len(line) < 50 and not '@' in line:
            # Simple heuristic: name is usually short and doesn't contain symbols
            if re.match(r'^[A-Za-z\s]+$', line):
                name = line
                break
    
    return name, email

def calculate_job_match_score(candidate_skills, job_skills):
    """Calculate match score between candidate and job skills"""
    if not candidate_skills or not job_skills:
        return 0.0
    
    candidate_set = set([skill.lower() for skill in candidate_skills])
    job_set = set([skill.lower() for skill in job_skills])
    
    matched_skills = candidate_set.intersection(job_set)
    match_ratio = len(matched_skills) / len(job_set)
    
    return round(match_ratio * 100, 1)

def generate_learning_recommendations(missing_skills):
    """Generate Google search URLs for learning missing skills"""
    recommendations = []
    
    # Priority mapping
    high_priority_skills = ["python", "javascript", "react", "sql", "aws", "docker"]
    
    for skill in missing_skills[:8]:  # Limit to top 8 missing skills
        priority = "high" if skill.lower() in high_priority_skills else "medium"
        
        # Create targeted search query
        search_query = f"learn {skill} online course tutorial"
        encoded_query = urllib.parse.quote(search_query)
        search_url = f"https://www.google.com/search?q={encoded_query}"
        
        recommendations.append(LearningRecommendation(
            skill=skill,
            google_search_url=search_url,
            priority=priority
        ))
    
    return recommendations

# Routes
@api_router.get("/")
async def root():
    return {"message": "Smart Job Recommendation Platform API"}

@api_router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Upload and parse resume file"""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.docx', '.txt')):
            raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are supported")
        
        file_content = await file.read()
        
        # Extract text based on file type
        if file.filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(file_content)
        elif file.filename.lower().endswith('.docx'):
            text = extract_text_from_docx(file_content)
        else:  # txt
            text = file_content.decode('utf-8')
        
        # Parse resume
        name, email = extract_basic_info(text)
        skills = extract_skills_from_text(text)
        experience_years = extract_experience_years(text)
        
        # Create profile
        profile = ResumeProfile(
            name=name,
            email=email,
            skills=skills,
            experience_years=experience_years,
            education="Extracted from resume",  # Could be enhanced
            certifications=[],  # Could be enhanced
            raw_text=text
        )
        
        # Save to database
        await db.resume_profiles.insert_one(profile.dict())
        
        return {
            "success": True,
            "profile": profile,
            "message": f"Resume parsed successfully! Found {len(skills)} skills."
        }
        
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

@api_router.post("/match-jobs/{profile_id}")
async def match_jobs(profile_id: str):
    """Find matching jobs for a candidate profile"""
    try:
        # Get profile from database
        profile_doc = await db.resume_profiles.find_one({"id": profile_id})
        if not profile_doc:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        profile = ResumeProfile(**profile_doc)
        job_matches = []
        
        for job_data in SAMPLE_JOBS:
            # Calculate match score
            fit_score = calculate_job_match_score(profile.skills, job_data["required_skills"])
            
            # Find matched and missing skills
            candidate_skills_lower = [skill.lower() for skill in profile.skills]
            job_skills_lower = [skill.lower() for skill in job_data["required_skills"]]
            
            matched_skills = [skill for skill in job_data["required_skills"] 
                            if skill.lower() in candidate_skills_lower]
            missing_skills = [skill for skill in job_data["required_skills"] 
                            if skill.lower() not in candidate_skills_lower]
            
            # Experience factor
            exp_factor = 1.0
            if profile.experience_years < job_data["experience_required"]:
                exp_factor = 0.8  # Reduce score if under-experienced
            elif profile.experience_years > job_data["experience_required"] + 2:
                exp_factor = 1.1  # Boost score if over-qualified
            
            final_score = min(fit_score * exp_factor, 100.0)
            
            job_match = JobMatch(
                id=job_data["id"],
                title=job_data["title"],
                company=job_data["company"],
                required_skills=job_data["required_skills"],
                experience_required=job_data["experience_required"],
                description=job_data["description"],
                location=job_data["location"],
                salary_range=job_data["salary_range"],
                fit_score=round(final_score, 1),
                matched_skills=matched_skills,
                missing_skills=missing_skills
            )
            
            job_matches.append(job_match)
        
        # Sort by fit score
        job_matches.sort(key=lambda x: x.fit_score, reverse=True)
        
        return {
            "success": True,
            "profile_id": profile_id,
            "matches": job_matches,
            "total_matches": len(job_matches)
        }
        
    except Exception as e:
        logger.error(f"Error matching jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error matching jobs: {str(e)}")

@api_router.post("/learning-recommendations/{profile_id}")
async def get_learning_recommendations(profile_id: str):
    """Get personalized learning recommendations"""
    try:
        # Get profile from database
        profile_doc = await db.resume_profiles.find_one({"id": profile_id})
        if not profile_doc:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        profile = ResumeProfile(**profile_doc)
        
        # Get all required skills from top job matches
        all_required_skills = set()
        candidate_skills_lower = [skill.lower() for skill in profile.skills]
        
        for job_data in SAMPLE_JOBS[:3]:  # Top 3 jobs
            for skill in job_data["required_skills"]:
                if skill.lower() not in candidate_skills_lower:
                    all_required_skills.add(skill)
        
        # Generate recommendations
        missing_skills = list(all_required_skills)
        recommendations = generate_learning_recommendations(missing_skills)
        
        return {
            "success": True,
            "profile_id": profile_id,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations)
        }
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@api_router.get("/profiles")
async def get_profiles():
    """Get all resume profiles"""
    try:
        profiles = await db.resume_profiles.find().to_list(100)
        return {
            "success": True,
            "profiles": [ResumeProfile(**profile) for profile in profiles]
        }
    except Exception as e:
        logger.error(f"Error fetching profiles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching profiles: {str(e)}")

# Legacy routes
@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
