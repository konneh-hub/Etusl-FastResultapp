from django.db import models


class ActivityLog(models.Model):
    """Activity logging"""
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='activity_logs')
    action = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=100)
    resource_id = models.IntegerField(null=True, blank=True)
    details = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user} - {self.action}"


class LoginLog(models.Model):
    """User login tracking"""
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='login_logs')
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time}"


class ResultChangeLog(models.Model):
    """Track result changes"""
    result = models.ForeignKey('results.Result', on_delete=models.CASCADE, related_name='change_logs')
    changed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    old_value = models.JSONField()
    new_value = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Result Change - {self.result}"


class ApprovalLog(models.Model):
    """Approval workflow logging"""
    submission = models.ForeignKey('approvals.ResultSubmission', on_delete=models.CASCADE, related_name='approval_logs')
    action = models.CharField(max_length=100)
    performed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Approval Log - {self.action}"
