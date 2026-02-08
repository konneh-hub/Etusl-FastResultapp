"""
Grading engine tests
"""
import pytest
from results.services.grading_engine import get_grade


class TestGradingEngine:
    
    def test_grade_a(self):
        """Test Grade A (90-100)"""
        grade, points = get_grade(95)
        assert grade == 'A'
        assert points == 4.0
    
    def test_grade_b(self):
        """Test Grade B (80-89)"""
        grade, points = get_grade(85)
        assert grade == 'B'
        assert points == 3.0
    
    def test_grade_f(self):
        """Test Grade F (0-59)"""
        grade, points = get_grade(45)
        assert grade == 'F'
        assert points == 0.0
    
    def test_boundary_scores(self):
        """Test boundary scores"""
        # Minimum A
        grade, _ = get_grade(90)
        assert grade == 'A'
        
        # Maximum F
        grade, _ = get_grade(59)
        assert grade == 'F'
