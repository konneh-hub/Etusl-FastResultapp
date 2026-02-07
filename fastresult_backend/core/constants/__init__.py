ROLE_CHOICES = [
    ('university_admin', 'University Administrator'),
    ('dean', 'Dean'),
    ('hod', 'Head of Department'),
    ('exam_officer', 'Exam Officer'),
    ('lecturer', 'Lecturer'),
    ('student', 'Student'),
]

GRADE_SCALE = {
    'A': {'min': 90, 'max': 100, 'points': 4.0},
    'B': {'min': 80, 'max': 89, 'points': 3.0},
    'C': {'min': 70, 'max': 79, 'points': 2.0},
    'D': {'min': 60, 'max': 69, 'points': 1.0},
    'F': {'min': 0, 'max': 59, 'points': 0.0},
}

SEMESTER_CHOICES = [
    (1, 'First Semester'),
    (2, 'Second Semester'),
]

RESULT_STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('submitted', 'Submitted'),
    ('under_review', 'Under Review'),
    ('approved', 'Approved'),
    ('published', 'Published'),
    ('rejected', 'Rejected'),
]

APPROVAL_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('revision_requested', 'Revision Requested'),
]
