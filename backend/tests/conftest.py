import os
import sys
import tempfile
import pytest
import sqlite3
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture(scope="session")
def test_db_path():
    """Create a test database with sample data."""
    # Create a temporary database
    fd, path = tempfile.mkstemp(suffix='.db')
    
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS job_roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_title TEXT NOT NULL,
        skills TEXT NOT NULL,
        demand_score INTEGER NOT NULL,
        suggested_microcredentials TEXT NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS nsqf_levels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        level INTEGER NOT NULL,
        qualification TEXT NOT NULL,
        example_courses TEXT NOT NULL
    )
    ''')
    
    # Insert test data
    job_roles = [
        ('Data Analyst', 'python, data analysis, statistics, sql', 90, 'Data Analysis with Python, SQL for Data Science'),
        ('Data Scientist', 'python, machine learning, statistics, data visualization', 95, 'Machine Learning, Data Visualization'),
        ('IT Support', 'troubleshooting, networking, customer service', 80, 'CompTIA A+, ITIL')
    ]
    
    nsqf_levels = [
        (4, 'Diploma in Data Science', 'Python Basics, Statistics'),
        (5, 'Advanced Diploma in Data Science', 'Machine Learning, Data Visualization'),
        (6, 'Bachelor in Data Science', 'Deep Learning, Big Data')
    ]
    
    cursor.executemany(
        'INSERT INTO job_roles (job_title, skills, demand_score, suggested_microcredentials) VALUES (?, ?, ?, ?)',
        job_roles
    )
    
    cursor.executemany(
        'INSERT INTO nsqf_levels (level, qualification, example_courses) VALUES (?, ?, ?)',
        nsqf_levels
    )
    
    conn.commit()
    conn.close()
    
    yield path
    
    # Cleanup
    try:
        os.unlink(path)
    except:
        pass

@pytest.fixture
def sample_profile():
    """Return a sample learner profile for testing."""
    return {
        'education_level': 4,  # Diploma level
        'prior_skills': ['python', 'data analysis', 'statistics'],
        'aspirations': 'I want to become a data scientist',
        'learning_pace': 'normal'
    }
