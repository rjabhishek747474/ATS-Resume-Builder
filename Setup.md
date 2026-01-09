# Setup Guide

## Development Setup

### 1. Start Backend Server

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Backend runs at: http://localhost:8000
API Docs at: http://localhost:8000/docs

### 2. Start Frontend Server

```bash
cd frontend
npm run dev
```

Frontend runs at: http://localhost:5173

## Configuration

### Gemini API Key (Required)

1. Go to https://aistudio.google.com/apikey
2. Create new API key
3. Add to `backend/.env`:
   ```
   GEMINI_API_KEY=your-key-here
   ```

### CORS Settings

Backend allows frontend origin `http://localhost:5173` by default.
Edit `backend/main.py` to change CORS settings.

## Project Structure

```
Job-Resume-Maker-Auto/
├── backend/
│   ├── api/           # API routes
│   │   ├── resume.py  # Resume upload
│   │   ├── jd.py      # JD extraction
│   │   ├── optimize.py # Optimization
│   │   └── download.py # PDF/DOCX export
│   ├── services/      # Business logic
│   │   ├── parser.py  # Resume parsing
│   │   ├── rewriter.py # AI optimization
│   │   ├── scorer.py  # ATS scoring
│   │   └── prompts.py # LLM prompts
│   ├── tests/         # Test suite
│   ├── main.py        # FastAPI app
│   └── config.py      # Settings
├── frontend/
│   ├── src/
│   │   ├── screens/   # UI screens
│   │   ├── App.tsx    # Main app
│   │   └── types.ts   # TypeScript types
│   └── index.html
└── docs/              # Documentation
```

## Testing

```bash
cd backend
pytest tests/test_api.py -v

# Run specific tests
pytest tests/test_api.py::TestDownloadEndpoints -v
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Blank screen | Check browser console for errors |
| API errors | Verify backend is running on port 8000 |
| Low ATS score | Add Gemini API key for AI optimization |
| PDF error | Install reportlab: `pip install reportlab` |
