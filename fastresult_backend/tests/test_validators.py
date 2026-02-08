"""
Validators test
"""
import pytest
from core.validators import validate_gpa, validate_percentage


def test_valid_gpa():
    """Test valid GPA"""
    validate_gpa(3.5)  # Should not raise


def test_invalid_gpa_above_max():
    """Test invalid GPA above max"""
    with pytest.raises(ValueError):
        validate_gpa(4.5)


def test_invalid_gpa_below_min():
    """Test invalid GPA below min"""
    with pytest.raises(ValueError):
        validate_gpa(-1.0)


def test_valid_percentage():
    """Test valid percentage"""
    validate_percentage(75)  # Should not raise


def test_invalid_percentage():
    """Test invalid percentage"""
    with pytest.raises(ValueError):
        validate_percentage(150)
