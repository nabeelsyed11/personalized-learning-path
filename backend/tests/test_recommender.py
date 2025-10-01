import pytest
import os
import json
from unittest.mock import MagicMock, patch
from app.services.recommender import HybridRecommender, compute_recommendations

def test_hybrid_recommender_initialization(test_db_path):
    """Test that the recommender initializes correctly with a test database."""
    recommender = HybridRecommender(test_db_path)
    assert len(recommender.job_roles) > 0
    assert len(recommender.nsqf_levels) > 0
    assert hasattr(recommender, 'nn_model')
    assert hasattr(recommender, 'vectorizer')
    assert recommender.db_path == test_db_path

def test_skill_normalization():
    """Test that skills are properly normalized."""
    recommender = HybridRecommender()
    # Test various cases
    test_cases = [
        ([' Python ', 'DATA Analysis', ' Machine Learning '], 
         ['python', 'data analysis', 'machine learning']),
        (['SQL', 'NoSQL', 'PostgreSQL'], 
         ['sql', 'nosql', 'postgresql']),
        ([], []),  # Empty list
        ([''], ['']),  # Single empty string
    ]
    
    for skills, expected in test_cases:
        normalized = recommender._normalize_skills(skills)
        assert normalized == expected

def test_empty_skills_handling():
    """Test that empty skills are handled gracefully."""
    recommender = HybridRecommender()
    test_cases = [
        (['', ' ', '  '], []),  # Empty or whitespace-only skills
        (['', 'Python', '  '], ['python']),  # Mixed empty and valid skills
        (['Python', '', 'SQL'], ['python', 'sql']),  # Empty in the middle
    ]
    
    for skills, expected in test_cases:
        normalized = recommender._normalize_skills(skills)
        assert normalized == expected

def test_mock_recommendations():
    """Test recommendations with mocked data."""
    with patch('app.services.recommender.HybridRecommender') as mock_recommender:
        # Setup mock
        mock_instance = mock_recommender.return_value
        mock_instance.get_recommendations.return_value = {
            'recommendations': [
                {
                    'job_title': 'Mock Data Scientist',
                    'match_score': 0.95,
                    'pathway': [
                        {'step': 1, 'title': 'Learn Python', 'duration_weeks': 4},
                        {'step': 2, 'title': 'Learn Statistics', 'duration_weeks': 4}
                    ],
                    'explanation': 'Based on your skills in Python and statistics'
                }
            ]
        }
        
        # Call the function under test
        result = compute_recommendations({
            'skills': ['python', 'statistics'],
            'education_level': 'bachelor',
            'learning_pace': 'normal'
        })
        
        # Verify the results
        assert 'recommendations' in result
        assert len(result['recommendations']) > 0
        assert result['recommendations'][0]['job_title'] == 'Mock Data Scientist'

def test_error_handling():
    """Test that the recommender handles errors gracefully."""
    # Test with invalid database path
    with pytest.raises(Exception):
        recommender = HybridRecommender('/nonexistent/path.db')
        recommender._load_data()  # This should raise an exception
    
    # Test with invalid profile data
    with pytest.raises(ValueError):
        compute_recommendations({})  # Empty profile

def test_recommendation_structure(sample_profile, test_db_path):
    """Test that recommendations have the expected structure."""
    recommender = HybridRecommender(test_db_path)
    result = recommender.get_recommendations(sample_profile)
    
    # Check top-level structure
    assert 'recommendations' in result
    assert isinstance(result['recommendations'], list)
    
    # Check each recommendation
    for rec in result['recommendations']:
        assert 'job_title' in rec
        assert 'match_score' in rec
        assert 'pathway' in rec
        assert 'explanation' in rec
        
        # Check pathway items
        for step in rec['pathway']:
            assert 'step' in step
            assert 'title' in step
            assert 'duration_weeks' in step
            assert isinstance(step['duration_weeks'], int)
            assert step['duration_weeks'] > 0

def test_compute_recommendations(sample_profile, test_db_path):
    """Test that recommendations are generated correctly."""
    recommendations = compute_recommendations(sample_profile, test_db_path)
    
    # Basic structure checks
    assert 'recommendations' in recommendations
    assert 'profile' in recommendations
    assert len(recommendations['recommendations']) > 0
    
    # Check recommendation structure
    for rec in recommendations['recommendations']:
        assert 'job_title' in rec
        assert 'match_score' in rec
        assert 'pathway' in rec
        assert 'explanation' in rec
        
        # Check pathway structure
        assert len(rec['pathway']) > 0
        for step in rec['pathway']:
            assert 'step' in step
            assert 'title' in step
            assert 'duration_weeks' in step

def test_learning_pace_adjustment(test_db_path, sample_profile):
    """Test that learning pace affects the duration of the pathway."""
    # Test fast pace
    sample_profile['learning_pace'] = 'fast'
    fast_rec = compute_recommendations(sample_profile, test_db_path)
    
    # Test slow pace
    sample_profile['learning_pace'] = 'slow'
    slow_rec = compute_recommendations(sample_profile, test_db_path)
    
    # Get total duration for comparison
    def get_total_duration(recommendation):
        return sum(step['duration_weeks'] 
                 for rec in recommendation['recommendations'] 
                 for step in rec['pathway'])
    
    fast_duration = get_total_duration(fast_rec)
    slow_duration = get_total_duration(slow_rec)
    
    # Fast pace should have shorter duration than slow pace
    assert fast_duration < slow_duration
