from django.db import models

class Report(models.Model):
    """Report model for analytics and reporting"""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'reports'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

__all__ = ['Report']

