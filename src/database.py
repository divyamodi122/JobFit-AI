from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# ─── Config ──────────────────────────────────────────────────────────────────
# Default: SQLite (no setup needed). Switch to MySQL if you want.
# MySQL:  "mysql+pymysql://user:password@localhost/jobfit_db"
# SQLite: "sqlite:///jobfit.db"

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///jobfit.db")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=True)
    job_description = Column(Text, nullable=True)
    overall_score = Column(Float)
    matched_skills = Column(Text)   # comma-separated
    missing_skills = Column(Text)   # comma-separated
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "overall_score": round(self.overall_score, 2),
            "matched_skills": self.matched_skills.split(",") if self.matched_skills else [],
            "missing_skills": self.missing_skills.split(",") if self.missing_skills else [],
            "created_at": str(self.created_at)
        }


try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"[DB] Could not create tables: {e}")



def save_result(filename, job_description, overall_score, matched_skills, missing_skills):
    """Save one analysis result to the database."""
    db = SessionLocal()
    try:
        record = AnalysisResult(
            filename=filename,
            job_description=job_description,
            overall_score=overall_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record.id
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_all_results(limit=10):
    """Fetch recent results from the database."""
    db = SessionLocal()
    try:
        records = db.query(AnalysisResult)\
                    .order_by(AnalysisResult.created_at.desc())\
                    .limit(limit)\
                    .all()
        return [r.to_dict() for r in records]
    except Exception as e:
        return []
    finally:
        db.close()


def get_result_by_id(result_id):
    """Fetch a single result by ID."""
    db = SessionLocal()
    try:
        record = db.query(AnalysisResult).filter(AnalysisResult.id == result_id).first()
        return record.to_dict() if record else None
    finally:
        db.close()