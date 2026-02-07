from django.db import models


class Notification(models.Model):
    """User notifications"""
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50)  # result_release, deadline, etc
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class Announcement(models.Model):
    """System announcements"""
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='announcements')
    created_at = models.DateTimeField(auto_now_add=True)
    target_role = models.CharField(max_length=50, blank=True, null=True)  # All, students, lecturers
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Broadcast(models.Model):
    """Broadcast messages"""
    title = models.CharField(max_length=255)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    recipients = models.ManyToManyField('accounts.User', related_name='broadcasts')
    
    def __str__(self):
        return self.title
