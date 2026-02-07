from django.db import models
from core.constants import RESULT_STATUS_CHOICES


class Result(models.Model):
    """Main result model"""
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='results')
    course = models.ForeignKey('academics.Course', on_delete=models.CASCADE, related_name='results')
    semester = models.ForeignKey('universities.Semester', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=RESULT_STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'course', 'semester']
    
    def __str__(self):
        return f"{self.student.matric_number} - {self.course.code}"


class ResultComponent(models.Model):
    """Result components (CA, exam, etc.)"""
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='components')
    component_name = models.CharField(max_length=100)  # e.g., "Continuous Assessment", "Final Exam"
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    marks_total = models.DecimalField(max_digits=5, decimal_places=2)
    weight = models.DecimalField(max_digits=3, decimal_places=2, default=1.0)  # Weight in calculation
    
    def __str__(self):
        return f"{self.result} - {self.component_name}"


class Grade(models.Model):
    """Grade assignment"""
    result = models.OneToOneField(Result, on_delete=models.CASCADE, related_name='grade')
    total_score = models.DecimalField(max_digits=5, decimal_places=2)
    letter_grade = models.CharField(max_length=2)
    grade_point = models.DecimalField(max_digits=3, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.result} - {self.letter_grade}"


class GPARecord(models.Model):
    """Student GPA per semester"""
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='gpa_records')
    semester = models.ForeignKey('universities.Semester', on_delete=models.CASCADE)
    gpa = models.DecimalField(max_digits=3, decimal_places=2)
    total_credits = models.IntegerField()
    quality_points = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'semester']
    
    def __str__(self):
        return f"{self.student.matric_number} - {self.semester}: {self.gpa}"


class CGPARecord(models.Model):
    """Student Cumulative GPA"""
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='cgpa_records')
    cgpa = models.DecimalField(max_digits=3, decimal_places=2)
    total_credits = models.IntegerField()
    quality_points = models.DecimalField(max_digits=8, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.matric_number} - CGPA: {self.cgpa}"


class Transcript(models.Model):
    """Student transcript"""
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='transcripts')
    generated_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='transcripts/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.student.matric_number} - {self.generated_date.date()}"


class ResultLock(models.Model):
    """Lock results from editing"""
    semester = models.ForeignKey('universities.Semester', on_delete=models.CASCADE)
    course = models.ForeignKey('academics.Course', on_delete=models.CASCADE)
    locked_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    locked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['semester', 'course']
    
    def __str__(self):
        return f"{self.course.code} - Locked"


class ResultRelease(models.Model):
    """Control result release to students"""
    semester = models.ForeignKey('universities.Semester', on_delete=models.CASCADE)
    course = models.ForeignKey('academics.Course', on_delete=models.CASCADE, null=True, blank=True)
    released_at = models.DateTimeField(auto_now_add=True)
    released_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"Results Released - {self.semester}"
