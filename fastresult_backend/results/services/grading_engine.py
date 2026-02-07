"""Grading Engine"""

GRADE_SCALE = {
    'A': {'min': 90, 'max': 100, 'points': 4.0},
    'B': {'min': 80, 'max': 89, 'points': 3.0},
    'C': {'min': 70, 'max': 79, 'points': 2.0},
    'D': {'min': 60, 'max': 69, 'points': 1.0},
    'F': {'min': 0, 'max': 59, 'points': 0.0},
}


def get_grade(score):
    """Get letter grade from score"""
    for grade, scale in GRADE_SCALE.items():
        if scale['min'] <= score <= scale['max']:
            return grade, scale['points']
    return 'F', 0.0
