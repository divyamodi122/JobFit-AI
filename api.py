from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from extractor import extract_skills_from_pdf, extract_skills_from_text
from scorer import get_overall_score, get_fit_level, get_recommendations
from database import save_result, get_all_results

app = FastAPI(
    title="JobFit AI API",
    description="Resume & Job Description Analyzer — NLP + ML Powered",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Welcome to JobFit AI API",
        "version": "1.0.0",
        "endpoints": ["/analyze", "/results", "/health"]
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "JobFit AI"}


@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(..., description="Resume PDF file"),
    job_description: str = Form(..., description="Job description text")
):

    if not resume.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await resume.read()
            tmp.write(content)
            tmp_path = tmp.name

        
        resume_skills = extract_skills_from_pdf(tmp_path)
        jd_skills = extract_skills_from_text(job_description)

        
        try:
            import PyPDF2
            with open(tmp_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                resume_text = " ".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            resume_text = ""

        
        result = get_overall_score(resume_skills, jd_skills, resume_text, job_description)
        result['fit_level'] = get_fit_level(result['overall_score'])
        result['recommendations'] = get_recommendations(
            result['missing_skills'], result['overall_score']
        )

        
        result['matched_skills'] = list(result.get('matched_skills', []))
        result['missing_skills'] = list(result.get('missing_skills', []))
        result['extra_skills'] = list(result.get('extra_skills', []))
        result['resume_skills'] = list(result.get('resume_skills', []))
        result['jd_skills'] = list(result.get('jd_skills', []))

    
        try:
            save_result(
                filename=resume.filename,
                job_description=job_description[:500],
                overall_score=result['overall_score'],
                matched_skills=",".join(result['matched_skills']),
                missing_skills=",".join(result['missing_skills'])
            )
        except Exception:
            pass  

        return {
            "status": "success",
            "filename": resume.filename,
            **result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


@app.get("/results")
def get_results(limit: int = 10):
    """Get recent analysis results from database"""
    try:
        results = get_all_results(limit=limit)
        return {"status": "success", "count": len(results), "results": results}
    except Exception as e:
        return {"status": "error", "message": str(e), "results": []}


@app.post("/analyze/text")
def analyze_text_only(
    resume_text: str = Form(..., description="Resume as plain text"),
    job_description: str = Form(..., description="Job description text")
):
    """Analyze using plain text instead of PDF (useful for testing)"""
    resume_skills = extract_skills_from_text(resume_text)
    jd_skills = extract_skills_from_text(job_description)

    result = get_overall_score(resume_skills, jd_skills, resume_text, job_description)
    result['fit_level'] = get_fit_level(result['overall_score'])
    result['recommendations'] = get_recommendations(
        result['missing_skills'], result['overall_score']
    )

    
    for key in ['matched_skills', 'missing_skills', 'extra_skills', 'resume_skills', 'jd_skills']:
        result[key] = list(result.get(key, []))

    return {"status": "success", **result}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)