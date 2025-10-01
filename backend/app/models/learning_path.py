from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
import enum

class LearningPathStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(LearningPathStatus), default=LearningPathStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="learning_paths")
    items = relationship("LearningPathItem", back_populates="learning_path", cascade="all, delete-orphan")

class LearningPathItemType(str, enum.Enum):
    COURSE = "course"
    ARTICLE = "article"
    VIDEO = "video"
    EXERCISE = "exercise"
    PROJECT = "project"

class LearningPathItem(Base):
    __tablename__ = "learning_path_items"

    id = Column(Integer, primary_key=True, index=True)
    learning_path_id = Column(Integer, ForeignKey("learning_paths.id"))
    item_type = Column(Enum(LearningPathItemType), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    resource_url = Column(String, nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # in minutes
    order = Column(Integer, nullable=False, default=0)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    learning_path = relationship("LearningPath", back_populates="items")
