from django.db import models


class StudentProfile(models.Model):
    """Student Profile model"""
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='student_profile')
    matric_number = models.CharField(max_length=50, unique=True)
    program = models.ForeignKey('academics.Program', on_delete=models.PROTECT)
    admission_date = models.DateField()
    current_level = models.IntegerField()  # 100, 200, 300, 400
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.matric_number} - {self.user.get_full_name()}"


class StudentEnrollment(models.Model):
    """Student enrollment in courses"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey('academics.Course', on_delete=models.PROTECT, related_name='student_enrollments')
    semester = models.ForeignKey('universities.Semester', on_delete=models.CASCADE)
    enrolled_date = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'course', 'semester']
    
    def __str__(self):
        return f"{self.student.matric_number} - {self.course.code}"


class StudentDocument(models.Model):
    """Student document storage"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50)
    document_file = models.FileField(upload_to='student_documents/')
    upload_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.matric_number} - {self.document_type}"


class StudentStatus(models.Model):
    """Student academic status"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('graduated', 'Graduated'),
        ('withdrawn', 'Withdrawn'),
        ('suspended', 'Suspended'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='status_records')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    academic_year = models.ForeignKey('universities.AcademicYear', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.matric_number} - {self.status}"
