"""
GPA calculation tests
"""
import pytest
from results.services.gpa_engine import calculate_gpa, GRADE_SCALE


class TestGPACalculation:
    
    def test_gpa_calculation(self):
        """Test GPA calculation"""
        grade_records = [
            {'points': 4.0, 'credits': 3},
            {'points': 3.0, 'credits': 4},
            {'points': 2.0, 'credits': 3},
        ]
        gpa = calculate_gpa(grade_records)
        expected = (4.0*3 + 3.0*4 + 2.0*3) / (3+4+3)
        assert abs(gpa - expected) < 0.01
    
    def test_empty_records(self):
        """Test empty records return 0"""
        gpa = calculate_gpa([])
        assert gpa == 0.0
    
    def test_perfect_gpa(self):
        """Test perfect GPA"""
        grade_records = [
            {'points': 4.0, 'credits': 3},
            {'points': 4.0, 'credits': 3},
        ]
        gpa = calculate_gpa(grade_records)
        assert gpa == 4.0
