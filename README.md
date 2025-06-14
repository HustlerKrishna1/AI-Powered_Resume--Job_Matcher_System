# 🧠 **AI Powered Resume & Job Matcher System** 

AI Powered Resume & Job Matcher System is a smart, full-stack application that analyzes resumes, matches candidates to suitable job profiles using AI algorithms, and recommends personalized learning paths to bridge skill gaps. Built with FastAPI, MongoDB, React, and Tailwind CSS.

🔗 Live Demo — Upload a resume with skills like Python, JavaScript, or React to see your match scores and learning recommendations.
 Link : https://jobmatch-ai-1.preview.emergentagent.com/

Note : My agent will sleep sometimes if there is no work for long time 
email: hustlerkrishna18@gmail.com 
Ping me to wake up my agent

✅ Core Features
📄 Resume Intelligence Engine
Drag-and-drop resume upload (PDF, DOCX, TXT)

AI-based parsing to extract:

Name

Contact info

Years of experience

40+ tech skills using pattern recognition

🎯 AI Job Matching
Matches resumes with curated tech job profiles

Calculates semantic match scores via cosine similarity

Highlights:

Overall fit percentage

Matched and missing skills

Ranked job recommendations

📚 Personalized Learning Path
Analyzes missing skills from job match

Classifies skill priority (High / Medium)

Generates Google search queries for:

Online tutorials

Certification courses

Learning platforms

🖥️ Responsive Web Interface
Built with React + Tailwind CSS

Intuitive tabbed dashboard:

Profile Overview

Job Matches

Learning Path

Clean animations and responsive layout

Drag-and-drop file upload with validation

📋 Test Summary
Feature	Status
Resume Upload & Parsing	✅ Functional
Job Matching Algorithm	✅ Fit Scores Accurate
Learning Recommendations	✅ Search Links Generated
UI Navigation	✅ Smooth and Responsive
Skill Analysis	✅ Matched & Missing Skills Shown

🛠 Tech Stack
Backend
Framework: FastAPI

Database: MongoDB

Libraries: PyPDF2, python-docx, scikit-learn

APIs:

/api/upload-resume

/api/match-jobs

/api/learning-recommendations

Frontend
Framework: React

Styling: Tailwind CSS

UI Components:

Drag-and-drop resume upload

Skill match visualizer

Dashboard navigation

🤖 AI Logic & Intelligence
Resume Parsing: Extracts structured information from PDF, DOCX, and TXT files

Job Matching: Uses cosine similarity for semantic fit analysis

Gap Detection: Identifies missing skills vs. job requirements

Learning Suggestions: Smart search queries for upskilling

📦 Getting Started
bash
Copy
Edit
# Clone the repository
git clone https://github.com/yourusername/jobmatch-ai.git

# Backend setup
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend setup
cd frontend
npm install
npm start
🚀 MVP Status: COMPLETE
 Resume Upload

 Skill Extraction

 AI-Based Job Matching

 Learning Recommendation Engine

 Responsive Web Interface

🔧 Future Enhancements
🌐 Live Job Listings: Integration with real-time job board APIs (e.g., LinkedIn, Indeed)

🧠 Advanced NLP: Use transformer models for enhanced parsing and recommendations

👤 User Profiles: Save resumes, track skill progress, and match history

📊 Admin Dashboard: Track system usage, job trends, and insights

🧪 Testing & Validation
✅ API unit testing for all endpoints

✅ UI tests using Playwright

✅ End-to-end flow tested from upload → match → recommend

📃 License
MIT License — free to use, modify, and extend.
