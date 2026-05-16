# JobFit AI — Resume & Job Description Analyzer

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green)
![ML](https://img.shields.io/badge/ML-Scikit--learn-orange)

> **Know your fit before you apply.**  
> JobFit AI parses your resume, extracts skills using NLP, and scores how well you match any job description — instantl

# Live Demo
> Coming soon (AWS deployment)

# What It Does

- Upload your **PDF Resume**
- Paste any **Job Description**
- NLP extracts skills from both
- ML model gives a **Match Score (0–100%)**
- Shows **matched skills**, **missing skills**,**bonus skills**
- Beautiful dashboard with **Gauge, Bar & Radar charts**
- Actionable **recommendations** to improve your profile

# Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit, Plotly |
| Backend | FastAPI, Uvicorn |
| NLP | NLTK, TF-IDF (Scikit-learn) |
| ML | Cosine Similarity, Scikit-learn |
| Database | SQLite / MySQL (SQLAlchemy) |
| PDF Processing | PyPDF2 |
| Deployment | AWS EC2 (coming soon) |

# Project Structure

```
JobFit-AI/
├── app.py              # Streamlit dashboard
├── api.py              # FastAPI backend
├── requirements.txt    # Dependencies
├── src/
│   ├── extractor.py    # PDF parser + NLP skill extractor
│   ├── scorer.py       # ML match scoring logic
│   └── database.py     # SQLAlchemy DB models & queries
└── README.md
```

# Setup & Run Locally
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/JobFit-AI.git
cd JobFit-AI

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the Streamlit app
streamlit run app.py

# 5. (Optional) Run FastAPI backend
python api.py

# Skills Showcased

`NLP` `Machine Learning` `Python` `PDF Processing` `FastAPI` `Streamlit` `SQL` `Data Visualization` `REST API` `AWS`


# Interview Talking Point

> *"I built JobFit AI while job hunting myself. It parses any resume and job description, extracts skills using NLP, and gives a match score. I built the full stack — NLP backend, FastAPI, and Streamlit dashboard with interactive charts."*


# Contact

**Divya** — [LinkedIn](https://linkedin.com) | [GitHub](https://github.com)