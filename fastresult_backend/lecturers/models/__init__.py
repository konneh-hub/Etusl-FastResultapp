from django.db import models


class Lecturer(models.Model):
    """Lecturer profile model"""
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='lecturer_profile')
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.ForeignKey('academics.Department', on_delete=models.PROTECT, related_name='lecturers')
    specialization = models.CharField(max_length=255, blank=True)
    qualification = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"


class LecturerQualification(models.Model):
    """Lecturer qualification records"""
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name='qualifications')
    qualification_type = models.CharField(max_length=100)
    institution = models.CharField(max_length=255)
    graduation_year = models.IntegerField()
    certificate = models.FileField(upload_to='qualifications/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.lecturer.user.get_full_name()} - {self.qualification_type}"
