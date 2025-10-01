import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import engine, Base
from app.models import NSQFCourse

def init_db():
    """Initialize the database with sample data."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if we already have data
        if db.query(NSQFCourse).count() == 0:
            # Add sample NSQF courses
            nsqf_courses = [
                {
                    "level": 4,
                    "qualification": "Certificate in IT-ITeS",
                    "example_courses": "Basics of IT, Digital Literacy, Communication Skills",
                    "description": "Entry-level IT qualification focusing on basic digital literacy and communication skills."
                },
                {
                    "level": 5,
                    "qualification": "Diploma in Web Development",
                    "example_courses": "HTML/CSS, JavaScript, Responsive Design",
                    "description": "Foundational web development skills for building responsive websites."
                },
                {
                    "level": 6,
                    "qualification": "Advanced Diploma in Data Science",
                    "example_courses": "Python, Statistics, Data Analysis, Machine Learning",
                    "description": "Comprehensive data science program covering programming, statistics, and machine learning."
                },
                {
                    "level": 7,
                    "qualification": "Bachelor of Technology in Artificial Intelligence",
                    "example_courses": "Deep Learning, NLP, Computer Vision, Reinforcement Learning",
                    "description": "Advanced program in AI covering modern machine learning techniques and applications."
                },
                {
                    "level": 8,
                    "qualification": "Master of Technology in Data Science",
                    "example_courses": "Advanced Machine Learning, Big Data Technologies, Research Methods",
                    "description": "Postgraduate program focusing on advanced topics in data science and analytics."
                }
            ]
            
            # Add courses to database
            for course_data in nsqf_courses:
                course = NSQFCourse(**course_data)
                db.add(course)
            
            db.commit()
            print("✅ Database initialized with sample data")
        else:
            print("✅ Database already contains data")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
