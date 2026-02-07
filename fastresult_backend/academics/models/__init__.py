from django.db import models
from universities.models import University


class Faculty(models.Model):
    """Faculty model"""
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='faculties')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    head = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='faculty_head')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['university', 'code']
    
    def __str__(self):
        return self.name


class Department(models.Model):
    """Department model"""
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    head = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='department_head')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['faculty', 'code']
    
    def __str__(self):
        return self.name


class Program(models.Model):
    """Study Program model"""
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programs')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    level = models.IntegerField()  # 100, 200, 300, 400
    description = models.TextField(blank=True)
    duration_years = models.IntegerField(default=4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['department', 'code']
    
    def __str__(self):
        return self.name


class Course(models.Model):
    """Course model"""
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='courses')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    credit_hours = models.IntegerField()
    description = models.TextField(blank=True)
    is_required = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['program', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Subject(models.Model):
    """Subject model"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class CourseAllocation(models.Model):
    """Course allocation to lecturers"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='allocations')
    lecturer = models.ForeignKey('lecturers.Lecturer', on_delete=models.CASCADE, related_name='course_allocations')
    semester = models.ForeignKey('universities.Semester', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['course', 'lecturer', 'semester']
    
    def __str__(self):
        return f"{self.course.code} - {self.lecturer.user.get_full_name()}"
