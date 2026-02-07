"""GPA Calculation Engine"""

def calculate_gpa(grade_records):
    """Calculate GPA from grade records"""
    if not grade_records:
        return 0.0
    
    total_quality_points = sum(record['points'] * record['credits'] for record in grade_records)
    total_credits = sum(record['credits'] for record in grade_records)
    
    return total_quality_points / total_credits if total_credits > 0 else 0.0


def calculate_cgpa(student):
    """Calculate cumulative GPA for a student"""
    gpa_records = student.gpa_records.all()
    if not gpa_records:
        return 0.0
    
    total_quality_points = sum(record.quality_points for record in gpa_records)
    total_credits = sum(record.total_credits for record in gpa_records)
    
    return total_quality_points / total_credits if total_credits > 0 else 0.0
