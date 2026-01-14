from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from models import StudySession

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "cybersyn.db"

Base = declarative_base()


class SessionDB(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task = Column(String, nullable=False)
    category = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, default=0)
    mode = Column(String, nullable=False)
    school_week = Column(Integer, nullable=False)
    paused_seconds = Column(Integer, default=0)


engine = create_engine(f"sqlite:///{DB_PATH}")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def save_session(session: StudySession) -> int:
    db = Session()
    db_session = SessionDB(
        task=session.task,
        category=session.category,
        start_time=session.start_time,
        end_time=session.end_time,
        duration_seconds=session.duration_seconds,
        mode=session.mode,
        school_week=session.school_week,
        paused_seconds=session.paused_seconds,
    )
    db.add(db_session)
    db.commit()
    session_id = db_session.id
    db.close()
    return session_id


def update_session(session_id: int, **kwargs) -> None:
    db = Session()
    db_session = db.query(SessionDB).filter(SessionDB.id == session_id).first()
    if db_session:
        for key, value in kwargs.items():
            setattr(db_session, key, value)
        db.commit()
    db.close()


def delete_session(session_id: int) -> bool:
    db = Session()
    db_session = db.query(SessionDB).filter(SessionDB.id == session_id).first()
    if db_session:
        db.delete(db_session)
        db.commit()
        db.close()
        return True
    db.close()
    return False


def get_session(session_id: int) -> StudySession | None:
    db = Session()
    db_session = db.query(SessionDB).filter(SessionDB.id == session_id).first()
    db.close()
    if not db_session:
        return None
    return StudySession(
        id=db_session.id,
        task=db_session.task,
        category=db_session.category,
        start_time=db_session.start_time,
        end_time=db_session.end_time,
        duration_seconds=db_session.duration_seconds,
        mode=db_session.mode,
        school_week=db_session.school_week,
        paused_seconds=db_session.paused_seconds,
    )


def get_all_sessions() -> list[StudySession]:
    db = Session()
    db_sessions = db.query(SessionDB).order_by(SessionDB.start_time.desc()).all()
    db.close()
    return [
        StudySession(
            id=s.id,
            task=s.task,
            category=s.category,
            start_time=s.start_time,
            end_time=s.end_time,
            duration_seconds=s.duration_seconds,
            mode=s.mode,
            school_week=s.school_week,
            paused_seconds=s.paused_seconds,
        )
        for s in db_sessions
    ]
