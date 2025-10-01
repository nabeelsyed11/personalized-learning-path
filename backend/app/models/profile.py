from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from ..database import Base

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    education_level = Column(Integer)
    prior_skills = Column(JSON)
    aspirations = Column(String)
    learning_pace = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
