from django.utils import timezone


class TimestampMixin:
    """Mixin that adds created_at and updated_at fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditMixin:
    """Mixin that adds audit tracking"""
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='%(class)s_created',
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='%(class)s_updated',
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
