from sqlalchemy import Column, Integer, String, Text
from ..database import Base

class NSQFCourse(Base):
    __tablename__ = "nsqf_courses"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(Integer)
    qualification = Column(String)
    example_courses = Column(String)
    description = Column(Text, nullable=True)
