"""
ATS Resume Builder - Main FastAPI Application
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from api import resume, jd, optimize, job, download

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle."""
    os.makedirs(settings.upload_dir, exist_ok=True)
    yield


app = FastAPI(
    title=settings.app_name,
    description="Transform resumes into ATS-optimized documents",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(resume.router, prefix="/api", tags=["Resume"])
app.include_router(jd.router, prefix="/api", tags=["Job Description"])
app.include_router(optimize.router, prefix="/api", tags=["Optimize"])
app.include_router(job.router, prefix="/api", tags=["Job Status"])
app.include_router(download.router, prefix="/api", tags=["Download"])


@app.get("/")
async def root():
    return {"service": settings.app_name, "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
