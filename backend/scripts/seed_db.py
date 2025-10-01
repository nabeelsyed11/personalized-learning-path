import os
import json
import csv
import sqlite3
from pathlib import Path
from typing import List, Dict, Any

# Database configuration
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance', 'app.db')
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def create_tables(conn: sqlite3.Connection) -> None:
    """Create necessary tables if they don't exist."""
    cursor = conn.cursor()
    
    # Create NSQF levels table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS nsqf_levels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        level INTEGER NOT NULL,
        qualification TEXT NOT NULL,
        example_courses TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create job roles table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS job_roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_title TEXT NOT NULL,
        skills TEXT NOT NULL,
        demand_score INTEGER NOT NULL,
        suggested_microcredentials TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()

def seed_nsqf_levels(conn: sqlite3.Connection) -> None:
    """Seed NSQF levels data from JSON file."""
    json_file = os.path.join(DATA_DIR, 'nsqf.json')
    
    with open(json_file, 'r', encoding='utf-8') as f:
        nsqf_data = json.load(f)
    
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute('DELETE FROM nsqf_levels')
    
    # Insert new data
    for item in nsqf_data:
        cursor.execute(
            'INSERT INTO nsqf_levels (level, qualification, example_courses) VALUES (?, ?, ?)',
            (item['level'], item['qualification'], ', '.join(item['example_courses']))
        )
    
    conn.commit()
    print(f"Seeded {len(nsqf_data)} NSQF levels")

def seed_job_roles(conn: sqlite3.Connection) -> None:
    """Seed job roles data from CSV file."""
    csv_file = os.path.join(DATA_DIR, 'job_roles.csv')
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        job_roles = list(reader)
    
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute('DELETE FROM job_roles')
    
    # Insert new data
    for role in job_roles:
        cursor.execute(
            'INSERT INTO job_roles (job_title, skills, demand_score, suggested_microcredentials) VALUES (?, ?, ?, ?)',
            (role['job_title'], role['skills'], int(role['demand_score']), role['suggested_microcredentials'])
        )
    
    conn.commit()
    print(f"Seeded {len(job_roles)} job roles")

def main():
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Connect to SQLite database
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Create tables
        create_tables(conn)
        
        # Seed data
        seed_nsqf_levels(conn)
        seed_job_roles(conn)
        
        print("Database seeding completed successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
