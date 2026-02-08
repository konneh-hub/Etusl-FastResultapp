from django.db import models
from accounts.models import User


class Report(models.Model):
    """Report model for tracking generated reports"""
    REPORT_TYPES = [
        ('academic_performance', 'Academic Performance'),
        ('result_summary', 'Result Summary'),
        ('gpa_analysis', 'GPA Analysis'),
        ('student_list', 'Student List'),
        ('course_enrollment', 'Course Enrollment'),
        ('exam_statistics', 'Exam Statistics'),
        ('attendance', 'Attendance'),
        ('custom', 'Custom Report'),
    ]
    
    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='generated_reports')
    generated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    file = models.FileField(upload_to='reports/', blank=True, null=True)
    filters = models.JSONField(null=True, blank=True)  # Store filter parameters
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.title} - {self.generated_at.date()}"
