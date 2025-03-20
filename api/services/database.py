from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models.task import Base

DATABASE_URL = "postgresql://taskpulse:secret@localhost:5432/taskpulse_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()