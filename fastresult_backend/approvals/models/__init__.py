from django.db import models
from core.constants import APPROVAL_STATUS_CHOICES


class ResultSubmission(models.Model):
    """Result submission for approval"""
    result = models.ForeignKey('results.Result', on_delete=models.CASCADE, related_name='submissions')
    submitted_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return f"Submission - {self.result}"


class ApprovalStage(models.Model):
    """Approval workflow stages"""
    submission = models.ForeignKey(ResultSubmission, on_delete=models.CASCADE, related_name='stages')
    stage_number = models.IntegerField()  # 1, 2, 3 etc
    approver_role = models.CharField(max_length=50)  # hod, dean, admin
    status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='pending')
    assigned_to = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['stage_number']
    
    def __str__(self):
        return f"Stage {self.stage_number} - {self.approver_role}"


class ApprovalAction(models.Model):
    """Individual approval actions"""
    stage = models.ForeignKey(ApprovalStage, on_delete=models.CASCADE, related_name='actions')
    approver = models.ForeignKey('accounts.User', on_delete=models.PROTECT)
    action = models.CharField(max_length=20, choices=[('approved', 'Approved'), ('rejected', 'Rejected'), ('revision_requested', 'Revision Requested')])
    comments = models.TextField(blank=True)
    acted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.approver.username} - {self.action}"


class ApprovalHistory(models.Model):
    """Approval history tracking"""
    submission = models.ForeignKey(ResultSubmission, on_delete=models.CASCADE, related_name='histories')
    action_type = models.CharField(max_length=50)
    performed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.action_type} - {self.timestamp}"


class CorrectionRequest(models.Model):
    """Correction requests during approval"""
    submission = models.ForeignKey(ResultSubmission, on_delete=models.CASCADE, related_name='corrections')
    requested_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT)
    issue_description = models.TextField()
    requested_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Correction - {self.submission}"
