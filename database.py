import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/sahakarconnect")

connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args["check_same_thread"] = False

try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        connect_args=connect_args
    )
except Exception as e:
    print(f"⚠️ Database engine initialization note: {e}")
    engine = None

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db(drop_first: bool = False):
    if not engine:
        raise RuntimeError("Database engine not configured.")
    
    # Cleanly drop existing tables if requested using SQLAlchemy metadata
    if drop_first:
        Base.metadata.drop_all(bind=engine)

    # Recreate all tables cleanly from SQLAlchemy schema
    Base.metadata.create_all(bind=engine)

def get_db():
    if not SessionLocal:
        raise RuntimeError("Database session not configured.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
