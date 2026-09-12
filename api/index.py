import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Any, Dict

from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import Session, declarative_base, relationship, sessionmaker

# ---------------------------------------------------------------------------
# Database — a Vercel Postgres/Neon integration injects DATABASE_URL automatically.
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "")


def _normalize(url: str) -> str:
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://") and "+psycopg" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


engine = (
    create_engine(
        _normalize(DATABASE_URL),
        pool_pre_ping=True,
        pool_size=1,
        max_overflow=2,
        pool_recycle=280,
    )
    if DATABASE_URL
    else None
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False) if engine else None
Base = declarative_base()


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def gen_id() -> str:
    return uuid.uuid4().hex


def get_db():
    if SessionLocal is None:
        raise HTTPException(status_code=500, detail="DATABASE_URL is not configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class Student(Base):
    __tablename__ = "codewar_students"

    id = Column(String(32), primary_key=True, default=gen_id)
    name = Column(String(120), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    college_id = Column(String(80), default="")
    language = Column(String(20), default="python")
    created_at = Column(DateTime(timezone=True), default=now_utc)

    submissions = relationship("Submission", back_populates="student", cascade="all, delete-orphan")


class Submission(Base):
    __tablename__ = "codewar_submissions"
    __table_args__ = (
        UniqueConstraint("student_id", "problem_slug", "stage", name="uq_codewar_submission"),
    )

    id = Column(String(32), primary_key=True, default=gen_id)
    student_id = Column(String(32), ForeignKey("codewar_students.id", ondelete="CASCADE"))
    problem_slug = Column(String(220), index=True)
    stage = Column(Integer)
    stage_title = Column(String(200), default="")
    language = Column(String(20))
    code = Column(Text, default="")
    submitted_at = Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    student = relationship("Student", back_populates="submissions")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    collegeId: str = Field(default="", max_length=80)
    language: str = Field(default="python", max_length=20)


class SubmitRequest(BaseModel):
    studentId: str
    problemSlug: str = Field(min_length=1, max_length=220)
    stage: int = Field(ge=1)
    stageTitle: str = ""
    language: str = Field(max_length=20)
    code: str = ""


class BulkStageSubmission(BaseModel):
    stage: int
    title: str
    submission: Optional[Dict[str, Any]] = None


class BulkSubmitRequest(BaseModel):
    student: Dict[str, Any]
    problem: Dict[str, Any]
    exportedAt: str
    stages: List[BulkStageSubmission]


def student_out(s: Student) -> dict:
    return {
        "id": s.id,
        "name": s.name,
        "email": s.email,
        "collegeId": s.college_id,
        "language": s.language,
    }


def submission_out(sub: Submission) -> dict:
    return {
        "stage": sub.stage,
        "stageTitle": sub.stage_title,
        "language": sub.language,
        "code": sub.code,
        "submittedAt": sub.submitted_at.isoformat(),
    }


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(title="Code War Offline API")

cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Admin-Key"],
)


@app.on_event("startup")
def on_startup():
    # In serverless environments, avoid creating tables on startup 
    # to prevent race conditions during multiple cold starts.
    # Use the /api/initdb endpoint instead.
    pass


@app.post("/api/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = payload.email.lower()
    student = db.query(Student).filter(Student.email == email).first()
    if student:
        student.name = payload.name.strip()
        student.college_id = payload.collegeId.strip()
        student.language = payload.language
    else:
        student = Student(
            name=payload.name.strip(),
            email=email,
            college_id=payload.collegeId.strip(),
            language=payload.language,
        )
        db.add(student)
    db.commit()
    db.refresh(student)
    return student_out(student)


@app.post("/api/submit")
def submit(payload: SubmitRequest, db: Session = Depends(get_db)):
    student = db.get(Student, payload.studentId)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found — please enter your details again")

    row = (
        db.query(Submission)
        .filter(
            Submission.student_id == student.id,
            Submission.problem_slug == payload.problemSlug,
            Submission.stage == payload.stage,
        )
        .first()
    )
    if row:
        row.stage_title = payload.stageTitle
        row.language = payload.language
        row.code = payload.code
        row.submitted_at = now_utc()
    else:
        row = Submission(
            student_id=student.id,
            problem_slug=payload.problemSlug,
            stage=payload.stage,
            stage_title=payload.stageTitle,
            language=payload.language,
            code=payload.code,
        )
        db.add(row)
    db.commit()
    db.refresh(row)
    return submission_out(row)


@app.post("/api/submit-bulk")
def submit_bulk(payload: BulkSubmitRequest, db: Session = Depends(get_db)):
    student_id = payload.student.get("id")
    problem_slug = payload.problem.get("slug")
    if not student_id or not problem_slug:
        raise HTTPException(status_code=400, detail="Missing student ID or problem slug")

    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    count = 0
    for stage_data in payload.stages:
        sub_data = stage_data.submission
        if not sub_data:
            continue
            
        stage_num = stage_data.stage
        
        row = (
            db.query(Submission)
            .filter(
                Submission.student_id == student.id,
                Submission.problem_slug == problem_slug,
                Submission.stage == stage_num,
            )
            .first()
        )
        if row:
            row.stage_title = stage_data.title
            row.language = sub_data.get("language", "")
            row.code = sub_data.get("code", "")
            row.submitted_at = now_utc()
        else:
            row = Submission(
                student_id=student.id,
                problem_slug=problem_slug,
                stage=stage_num,
                stage_title=stage_data.title,
                language=sub_data.get("language", ""),
                code=sub_data.get("code", ""),
            )
            db.add(row)
        count += 1
        
    db.commit()
    return {"ok": True, "stagesSynced": count}


@app.get("/api/submissions")
def list_submissions(
    studentId: str = Query(...),
    problemSlug: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Submission).filter(Submission.student_id == studentId)
    if problemSlug:
        q = q.filter(Submission.problem_slug == problemSlug)
    rows = q.order_by(Submission.stage).all()
    return [submission_out(r) for r in rows]


ADMIN_KEY = os.getenv("ADMIN_KEY", "")


@app.get("/api/all")
def all_submissions(
    problemSlug: Optional[str] = None,
    key: str = Query(default=""),
    db: Session = Depends(get_db),
):
    """Instructor export of every student's submissions. Protect with the ADMIN_KEY env var."""
    if not ADMIN_KEY or key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")
    q = db.query(Submission).join(Student)
    if problemSlug:
        q = q.filter(Submission.problem_slug == problemSlug)
    rows = q.order_by(Student.name, Submission.stage).all()
    return [
        {
            "student": {
                "name": r.student.name,
                "email": r.student.email,
                "collegeId": r.student.college_id,
            },
            **submission_out(r),
        }
        for r in rows
    ]


@app.get("/api/initdb")
def initdb(key: str = Query(default="")):
    """Initialize the database tables. Protect with the ADMIN_KEY env var."""
    if not ADMIN_KEY or key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")
    if engine is not None:
        Base.metadata.create_all(bind=engine)
        return {"ok": True, "message": "Tables created successfully"}
    return {"ok": False, "message": "Database not configured"}


@app.get("/api/health")
def health():
    return {"ok": True, "dbConfigured": engine is not None}


@app.get("/api/config")
def config():
    """Public runtime config. Set PUBLIC_API_BASE in the Vercel project's env vars only
    if the frontend and this API are deployed to different domains; leave unset otherwise."""
    return {"apiBase": os.getenv("PUBLIC_API_BASE", "")}


@app.get("/api")
def root():
    return {"ok": True, "service": "Code War Offline API"}
