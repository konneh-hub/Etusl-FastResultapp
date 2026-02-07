from django.db import models


class FileUpload(models.Model):
    """Uploaded files"""
    FILE_TYPES = [
        ('transcript', 'Transcript'),
        ('certificate', 'Certificate'),
        ('document', 'Document'),
        ('result', 'Result'),
    ]
    
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='uploads')
    file_type = models.CharField(max_length=50, choices=FILE_TYPES)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_file_type_display()}"
