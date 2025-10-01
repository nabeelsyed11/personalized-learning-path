import json
import numpy as np
from typing import Dict, List, Tuple, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import sqlite3
from pathlib import Path
import os

class HybridRecommender:
    def __init__(self, db_path: str = None):
        """Initialize the recommender with database connection."""
        if db_path is None:
            # Default to instance/app.db relative to this file
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'instance',
                'app.db'
            )
        self.db_path = db_path
        self.vectorizer = TfidfVectorizer(lowercase=True, stop_words='english')
        self.job_roles = []
        self.nsqf_levels = []
        self._load_data()
        self._train_model()

    def _get_db_connection(self):
        """Create and return a database connection."""
        return sqlite3.connect(self.db_path)

    def _load_data(self) -> None:
        """Load job roles and NSQF levels from the database."""
        conn = self._get_db_connection()
        try:
            # Load job roles
            cursor = conn.execute('SELECT * FROM job_roles')
            columns = [column[0] for column in cursor.description]
            self.job_roles = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Load NSQF levels
            cursor = conn.execute('SELECT * FROM nsqf_levels')
            columns = [column[0] for column in cursor.description]
            self.nsqf_levels = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        finally:
            conn.close()

    def _train_model(self) -> None:
        """Train the recommendation model on job role skills."""
        if not self.job_roles:
            raise ValueError("No job roles found in the database")
            
        # Prepare skills data for vectorization
        skills_data = [role['skills'].lower() for role in self.job_roles]
        self.skills_matrix = self.vectorizer.fit_transform(skills_data)
        
        # Initialize and fit NearestNeighbors
        self.nn_model = NearestNeighbors(metric='cosine', n_neighbors=3, n_jobs=-1)
        self.nn_model.fit(self.skills_matrix)

    def _normalize_skills(self, skills: List[str]) -> List[str]:
        """Normalize skills by converting to lowercase and stripping whitespace."""
        return [skill.lower().strip() for skill in skills]

    def _calculate_skill_overlap(self, user_skills: List[str], job_skills: str) -> float:
        """Calculate skill overlap score between user skills and job skills."""
        job_skill_set = set(skill.strip().lower() for skill in job_skills.split(','))
        user_skill_set = set(user_skills)
        
        if not job_skill_set:
            return 0.0
            
        return len(user_skill_set.intersection(job_skill_set)) / len(job_skill_set)

    def _map_to_nsqf_pathway(self, current_level: int, target_level: int) -> List[Dict[str, Any]]:
        """Map the learning pathway from current to target NSQF level."""
        if current_level >= target_level:
            return []
            
        # Filter NSQF levels within the target range
        pathway_levels = [
            level for level in self.nsqf_levels 
            if current_level < level['level'] <= target_level
        ]
        
        # Sort by level in ascending order
        pathway_levels.sort(key=lambda x: x['level'])
        
        return pathway_levels

    def _create_learning_pathway(self, job_role: Dict[str, Any], current_level: int) -> List[Dict[str, str]]:
        """Create a 4-step learning pathway based on job role and current level."""
        target_level = 7  # Assuming level 7 as target for professional roles
        
        # Get NSQF pathway
        nsqf_pathway = self._map_to_nsqf_pathway(current_level, target_level)
        
        # Split suggested microcredentials
        microcredentials = [m.strip() for m in job_role['suggested_microcredentials'].split(',')]
        
        # Build the 4-step pathway
        pathway = []
        
        # Step 1: Foundational
        if nsqf_pathway and len(nsqf_pathway) > 0:
            pathway.append({
                'step': 'Foundational',
                'title': nsqf_pathway[0]['qualification'],
                'description': f"Build fundamental knowledge with {nsqf_pathway[0]['qualification']}",
                'duration_weeks': 12,
                'type': 'course',
                'level': nsqf_pathway[0]['level']
            })
        
        # Step 2: Core
        if len(nsqf_pathway) > 1:
            pathway.append({
                'step': 'Core',
                'title': nsqf_pathway[-1]['qualification'],
                'description': f"Deepen your expertise with {nsqf_pathway[-1]['qualification']}",
                'duration_weeks': 16,
                'type': 'course',
                'level': nsqf_pathway[-1]['level']
            })
        
        # Step 3: Micro-credential
        if microcredentials:
            pathway.append({
                'step': 'Micro-credential',
                'title': microcredentials[0],
                'description': f"Specialize with {microcredentials[0]} certification",
                'duration_weeks': 8,
                'type': 'certification',
                'level': target_level
            })
        
        # Step 4: On-the-job/Internship
        pathway.append({
            'step': 'On-the-job/Internship',
            'title': f"{job_role['job_title']} Internship",
            'description': f"Gain practical experience as a {job_role['job_title']}",
            'duration_weeks': 12,
            'type': 'internship',
            'level': target_level
        })
        
        return pathway

    def _generate_explanation(self, job_role: Dict[str, Any], skill_overlap: float, demand_score: int) -> str:
        """Generate an explanation for the recommendation."""
        base = f"This role matches {int(skill_overlap * 100)}% of your existing skills "
        base += f"and has a high demand score of {demand_score}/100. "
        base += f"The role typically requires skills in: {job_role['skills']}."
        return base

    def compute_recommendations(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute personalized learning pathway recommendations.
        
        Args:
            profile: Dictionary containing:
                - education_level: int (current NSQF level)
                - prior_skills: List[str] (list of skills)
                - aspirations: str (career aspiration text)
                - learning_pace: str ("slow"|"normal"|"fast")
                
        Returns:
            Dict containing recommended pathways and explanations
        """
        # Normalize inputs
        normalized_skills = self._normalize_skills(profile.get('prior_skills', []))
        
        if not normalized_skills:
            raise ValueError("No skills provided in the profile")
        
        # Prepare user skills for prediction
        user_skills_text = ', '.join(normalized_skills)
        user_vector = self.vectorizer.transform([user_skills_text])
        
        # Find nearest job roles
        distances, indices = self.nn_model.kneighbors(user_vector, n_neighbors=3)
        
        recommendations = []
        
        for idx, distance in zip(indices[0], distances[0]):
            job_role = self.job_roles[idx]
            
            # Calculate scores
            skill_overlap = 1 - distance  # Convert cosine distance to similarity
            demand_score = job_role.get('demand_score', 50)  # Default to 50 if not available
            
            # Calculate combined score (weighted average)
            combined_score = (skill_overlap * 0.6) + (demand_score / 100 * 0.4)
            
            # Create learning pathway
            pathway = self._create_learning_pathway(
                job_role,
                profile.get('education_level', 1)  # Default to level 1 if not specified
            )
            
            # Adjust duration based on learning pace
            pace_multiplier = {
                'slow': 1.3,
                'normal': 1.0,
                'fast': 0.7
            }.get(profile.get('learning_pace', 'normal'), 1.0)
            
            for step in pathway:
                step['duration_weeks'] = int(step['duration_weeks'] * pace_multiplier)
            
            # Generate explanation
            explanation = self._generate_explanation(job_role, skill_overlap, demand_score)
            
            recommendations.append({
                'job_title': job_role['job_title'],
                'match_score': round(combined_score * 100, 1),  # Convert to percentage
                'pathway': pathway,
                'explanation': explanation
            })
        
        # Sort recommendations by match score (descending)
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        
        return {
            'recommendations': recommendations,
            'profile': {
                'education_level': profile.get('education_level', 1),
                'skills_count': len(normalized_skills),
                'learning_pace': profile.get('learning_pace', 'normal')
            }
        }

def compute_recommendations(profile: Dict[str, Any], db_path: str = None) -> Dict[str, Any]:
    """
    Convenience function to get recommendations without instantiating the class.
    
    Args:
        profile: Learner profile dictionary
        db_path: Optional path to SQLite database
        
    Returns:
        Dictionary with recommendations
    """
    recommender = HybridRecommender(db_path)
    return recommender.compute_recommendations(profile)
