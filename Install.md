# Installation Guide

## Prerequisites

- Python 3.10+ 
- Node.js 18+
- Git

## Backend Installation

```bash
# Clone repository
git clone <repository-url>
cd Job-Resume-Maker-Auto

# Create virtual environment
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Frontend Installation

```bash
cd frontend
npm install
```

## Environment Setup

Create `backend/.env`:

```env
# Required for AI optimization
GEMINI_API_KEY=your-gemini-api-key

# Optional
OPENAI_API_KEY=your-openai-key
DEBUG=true
```

## Verify Installation

```bash
# Test backend
cd backend
pytest tests/test_api.py -v

# Expected: 18 passed
```

## Dependencies

### Backend (requirements.txt)
- fastapi
- uvicorn
- pdfplumber
- python-docx
- reportlab
- google-generativeai
- openai
- pytest
- httpx

### Frontend (package.json)
- react
- typescript
- vite
- axios
- tailwindcss
