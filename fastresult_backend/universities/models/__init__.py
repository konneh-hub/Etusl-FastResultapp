from django.db import models


class University(models.Model):
    """University model"""
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='universities/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    established_year = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Campus(models.Model):
    """Campus model"""
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='campuses')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    location = models.CharField(max_length=255)
    is_main = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['university', 'code']
    
    def __str__(self):
        return f"{self.university.name} - {self.name}"


class AcademicYear(models.Model):
    """Academic Year model"""
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='academic_years')
    year = models.CharField(max_length=9)  # 2023/2024
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['university', 'year']
        ordering = ['-year']
    
    def __str__(self):
        return f"{self.university.name} - {self.year}"


class Semester(models.Model):
    """Semester model"""
    SEMESTER_CHOICES = [(1, 'First'), (2, 'Second')]
    
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='semesters')
    number = models.IntegerField(choices=SEMESTER_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['academic_year', 'number']
    
    def __str__(self):
        return f"{self.academic_year.year} - Semester {self.number}"


class GradingScale(models.Model):
    """Grading Scale model"""
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='grading_scales')
    name = models.CharField(max_length=100)
    grade = models.CharField(max_length=2)
    min_score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=5, decimal_places=2)
    grade_point = models.DecimalField(max_digits=3, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['university', 'grade']
    
    def __str__(self):
        return f"{self.university.name} - {self.grade}"


class CreditRules(models.Model):
    """Credit Rules model"""
    university = models.OneToOneField(University, on_delete=models.CASCADE, related_name='credit_rules')
    min_credit_per_semester = models.IntegerField(default=12)
    max_credit_per_semester = models.IntegerField(default=30)
    gpa_threshold = models.DecimalField(max_digits=3, decimal_places=2, default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Credit Rules - {self.university.name}"
