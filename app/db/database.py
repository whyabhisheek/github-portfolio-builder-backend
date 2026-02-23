from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator, Union, Optional

Base = declarative_base()

engine = None
SessionLocal = None
DB_AVAILABLE = False


def init_db(database_url: str):
    global engine, SessionLocal, DB_AVAILABLE
    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)
        DB_AVAILABLE = True
    except Exception:
        engine = None
        SessionLocal = None
        DB_AVAILABLE = False


def get_db() -> Generator[Optional[Session], None, None]:
    if not DB_AVAILABLE:
        yield None
        return
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
