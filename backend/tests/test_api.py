"""
ATS Resume Builder - Test Suite
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns service info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert data["service"] == "ATS Resume Builder"
    
    def test_health_endpoint(self):
        """Test health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestResumeEndpoints:
    """Test resume upload and parsing endpoints."""
    
    def test_upload_text_resume(self):
        """Test uploading resume as text."""
        resume_text = """
        John Doe
        Software Engineer
        
        SUMMARY
        Experienced software engineer with 5 years in Python development.
        
        EXPERIENCE
        Senior Developer at TechCorp (2020-2024)
        - Developed REST APIs using Python and FastAPI
        - Led team of 3 developers
        - Increased system performance by 40%
        
        SKILLS
        Python, FastAPI, PostgreSQL, Docker, AWS
        
        EDUCATION
        BS Computer Science, MIT, 2019
        """
        
        response = client.post(
            "/api/resume/upload",
            data={"text": resume_text}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "resume_id" in data
        assert data["resume_id"].startswith("res-")
        assert "sections" in data
        assert "summary" in data["sections"]
        assert "experience" in data["sections"]
        assert "skills" in data["sections"]
    
    def test_upload_empty_resume_fails(self):
        """Test that empty resume upload fails."""
        response = client.post(
            "/api/resume/upload",
            data={"text": ""}
        )
        assert response.status_code == 400
    
    def test_get_resume(self):
        """Test retrieving uploaded resume."""
        # First upload
        resume_text = "SUMMARY\nTest resume content\nSKILLS\nPython"
        upload_response = client.post(
            "/api/resume/upload",
            data={"text": resume_text}
        )
        resume_id = upload_response.json()["resume_id"]
        
        # Then retrieve
        response = client.get(f"/api/resume/{resume_id}")
        assert response.status_code == 200
        assert response.json()["resume_id"] == resume_id
    
    def test_get_nonexistent_resume(self):
        """Test getting non-existent resume returns 404."""
        response = client.get("/api/resume/res-nonexistent")
        assert response.status_code == 404


class TestJDEndpoints:
    """Test job description extraction endpoints."""
    
    def test_extract_jd(self):
        """Test JD extraction from text."""
        jd_text = """
        Senior Python Developer
        
        We are looking for a Senior Python Developer with 5+ years experience.
        
        Requirements:
        - Python programming
        - FastAPI or Django experience
        - PostgreSQL database knowledge
        - Docker containerization
        - AWS cloud services
        
        Nice to have:
        - React frontend experience
        - Kubernetes knowledge
        
        Responsibilities:
        - Lead backend development
        - Mentor junior developers
        - Design system architecture
        """
        
        response = client.post(
            "/api/jd/extract",
            json={"text": jd_text}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "jd_id" in data
        assert data["jd_id"].startswith("jd-")
        assert "role" in data
        assert "hard_skills" in data
        assert "keywords" in data
        assert len(data["hard_skills"]) > 0
    
    def test_extract_short_jd_fails(self):
        """Test that too short JD fails."""
        response = client.post(
            "/api/jd/extract",
            json={"text": "Short"}
        )
        assert response.status_code == 400
    
    def test_extract_empty_jd_fails(self):
        """Test that empty JD fails."""
        response = client.post(
            "/api/jd/extract",
            json={}
        )
        assert response.status_code == 400


class TestOptimizeEndpoints:
    """Test optimization endpoints."""
    
    def test_full_optimization_flow(self):
        """Test complete optimization flow."""
        # 1. Upload resume
        resume_text = """
        SUMMARY
        Software developer with Python experience.
        
        EXPERIENCE
        Developer at Company (2020-2024)
        - Worked on web applications
        - Used Python for backend
        
        SKILLS
        Python, JavaScript, SQL
        
        EDUCATION
        BS Computer Science
        """
        
        resume_response = client.post(
            "/api/resume/upload",
            data={"text": resume_text}
        )
        resume_id = resume_response.json()["resume_id"]
        
        # 2. Extract JD
        jd_text = """
        Python Developer
        
        We need a Python developer with FastAPI experience.
        Requirements: Python, FastAPI, PostgreSQL, Docker, AWS.
        You will build REST APIs and work with databases.
        """
        
        jd_response = client.post(
            "/api/jd/extract",
            json={"text": jd_text}
        )
        jd_id = jd_response.json()["jd_id"]
        
        # 3. Start optimization
        optimize_response = client.post(
            "/api/optimize",
            json={"resume_id": resume_id, "jd_id": jd_id}
        )
        
        assert optimize_response.status_code == 200
        data = optimize_response.json()
        assert "job_id" in data
        job_id = data["job_id"]
        
        # 4. Check status
        status_response = client.get(f"/api/job/{job_id}/status")
        assert status_response.status_code == 200
        
        # 5. Get result
        result_response = client.get(f"/api/job/{job_id}/result")
        assert result_response.status_code == 200
        result = result_response.json()
        assert "ats_score" in result
        assert "optimized_resume" in result
        assert 0 <= result["ats_score"] <= 100
    
    def test_optimize_invalid_resume(self):
        """Test optimization with invalid resume ID fails."""
        response = client.post(
            "/api/optimize",
            json={"resume_id": "res-invalid", "jd_id": "jd-invalid"}
        )
        assert response.status_code == 404


class TestSectionDetection:
    """Test resume section detection."""
    
    def test_detects_all_sections(self):
        """Test detection of all major sections."""
        resume_text = """
        PROFESSIONAL SUMMARY
        Experienced developer.
        
        WORK EXPERIENCE
        Company A - Developer
        - Task 1
        - Task 2
        
        TECHNICAL SKILLS
        Python, Java, SQL
        
        EDUCATION
        BS in CS
        
        CERTIFICATIONS
        AWS Certified
        """
        
        response = client.post(
            "/api/resume/upload",
            data={"text": resume_text}
        )
        
        sections = response.json()["sections"]
        assert "summary" in sections or any("summary" in k for k in sections)
        assert "experience" in sections
        assert "skills" in sections
        assert "education" in sections


class TestJDIntelligence:
    """Test JD intelligence extraction."""
    
    def test_extracts_seniority(self):
        """Test seniority level detection."""
        senior_jd = "Senior Software Engineer with 5+ years experience. Python, AWS required. We need someone to lead teams and architect systems."
        
        response = client.post(
            "/api/jd/extract",
            json={"text": senior_jd}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "seniority" in data
        assert data["seniority"] == "senior"
    
    def test_extracts_skills(self):
        """Test skill extraction from JD."""
        jd = """
        Python Developer needed.
        Must know Python, FastAPI, PostgreSQL.
        Docker and Kubernetes experience preferred.
        """ + " " * 100
        
        response = client.post(
            "/api/jd/extract",
            json={"text": jd}
        )
        
        skills = [s.lower() for s in response.json()["hard_skills"]]
        assert "python" in skills


class TestATSScoring:
    """Test ATS scoring algorithm."""
    
    def test_high_match_gets_high_score(self):
        """Test that matching resume gets high score."""
        # Resume with matching skills
        resume_text = """
        SUMMARY
        Senior Python developer with FastAPI and AWS experience.
        
        EXPERIENCE
        Lead Developer (2020-2024)
        - Developed REST APIs using Python and FastAPI
        - Deployed applications on AWS using Docker
        - Managed PostgreSQL databases
        - Led Agile development process
        
        SKILLS
        Python, FastAPI, PostgreSQL, Docker, AWS, Kubernetes
        
        EDUCATION
        MS Computer Science
        """
        
        # JD with same skills
        jd_text = """
        Senior Python Developer
        
        Requirements:
        Python, FastAPI, PostgreSQL, Docker, AWS
        
        You will build scalable APIs and deploy to cloud.
        """ + " " * 100
        
        # Upload and optimize
        resume_resp = client.post("/api/resume/upload", data={"text": resume_text})
        jd_resp = client.post("/api/jd/extract", json={"text": jd_text})
        
        optimize_resp = client.post("/api/optimize", json={
            "resume_id": resume_resp.json()["resume_id"],
            "jd_id": jd_resp.json()["jd_id"]
        })
        
        job_id = optimize_resp.json()["job_id"]
        result = client.get(f"/api/job/{job_id}/result").json()
        
        # Should have decent score with matching skills
        assert result["ats_score"] >= 50


class TestDownloadEndpoints:
    """Test resume download/export endpoints."""
    
    def test_download_resume_text(self):
        """Test downloading resume as text."""
        # Create optimization first
        resume_text = """
        SUMMARY
        Software developer with Python experience.
        
        EXPERIENCE
        Developer (2020-2024)
        - Built REST APIs
        
        SKILLS
        Python, SQL
        
        EDUCATION
        BS CS
        """
        
        jd_text = "Python Developer position available. Requirements: Python programming, SQL databases, AWS cloud services required. Build scalable backend systems."
        
        resume_resp = client.post("/api/resume/upload", data={"text": resume_text})
        jd_resp = client.post("/api/jd/extract", json={"text": jd_text})
        
        optimize_resp = client.post("/api/optimize", json={
            "resume_id": resume_resp.json()["resume_id"],
            "jd_id": jd_resp.json()["jd_id"]
        })
        
        job_id = optimize_resp.json()["job_id"]
        
        # Download as PDF (default)
        download_resp = client.post("/api/resume/download", json={
            "job_id": job_id,
            "format": "pdf"
        })
        
        assert download_resp.status_code == 200
        assert download_resp.headers["content-type"] == "application/pdf"
        # PDF files start with %PDF
        assert download_resp.content[:4] == b'%PDF'
    
    def test_download_resume_docx(self):
        """Test downloading resume as DOCX."""
        resume_text = """
        SUMMARY
        Developer with experience.
        
        SKILLS
        Python, Java
        
        EXPERIENCE
        Dev (2020-2024)
        - Coded stuff
        
        EDUCATION
        BS
        """
        
        jd_text = "Software Engineer position. Python required for backend development. Build distributed systems and microservices architecture."
        
        resume_resp = client.post("/api/resume/upload", data={"text": resume_text})
        jd_resp = client.post("/api/jd/extract", json={"text": jd_text})
        
        optimize_resp = client.post("/api/optimize", json={
            "resume_id": resume_resp.json()["resume_id"],
            "jd_id": jd_resp.json()["jd_id"]
        })
        
        job_id = optimize_resp.json()["job_id"]
        
        # Download as DOCX
        download_resp = client.post("/api/resume/download", json={
            "job_id": job_id,
            "format": "docx"
        })
        
        assert download_resp.status_code == 200
        assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in download_resp.headers["content-type"]
        # DOCX files are ZIP archives starting with PK
        assert download_resp.content[:2] == b'PK'
    
    def test_get_formatted_resume(self):
        """Test getting formatted resume with keywords."""
        resume_text = """
        SUMMARY
        Python developer.
        
        SKILLS
        Python, AWS
        
        EXPERIENCE
        Dev at Company
        - Built APIs
        
        EDUCATION
        BS
        """
        
        jd_text = "Python Developer with AWS cloud experience. Build scalable distributed systems. Must have experience with backend development and API design."
        
        resume_resp = client.post("/api/resume/upload", data={"text": resume_text})
        resume_id = resume_resp.json()["resume_id"]
        
        jd_resp = client.post("/api/jd/extract", json={"text": jd_text})
        jd_id = jd_resp.json()["jd_id"]
        
        # Get formatted resume with keywords
        formatted_resp = client.get(f"/api/resume/{resume_id}/formatted?jd_id={jd_id}")
        
        assert formatted_resp.status_code == 200
        data = formatted_resp.json()
        assert "formatted_resume" in data
        assert "matched_keywords" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
