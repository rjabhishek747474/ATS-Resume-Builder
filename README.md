# ATS Resume Builder - README

An AI-powered resume optimization tool that analyzes resumes against job descriptions and generates ATS-friendly versions with 90%+ compatibility scores.

## Features

- **Resume Parsing** - Upload PDF/TXT or paste resume text
- **JD Analysis** - Extract keywords, skills, and requirements from job descriptions
- **AI Optimization** - Gemini-powered rewriting with truth preservation
- **ATS Scoring** - 0-100 compatibility score with gap analysis
- **Export Options** - Download as PDF or DOCX

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python, FastAPI |
| Frontend | React, TypeScript, Vite |
| AI | Google Gemini API |
| PDF | ReportLab |
| DOCX | python-docx |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/resume/upload` | POST | Upload resume |
| `/api/jd/extract` | POST | Parse job description |
| `/api/optimize` | POST | Start optimization |
| `/api/resume/download` | POST | Download PDF/DOCX |

## Environment Variables

```env
GEMINI_API_KEY=your-gemini-api-key
OPENAI_API_KEY=optional-openai-key
```

## License

MIT
