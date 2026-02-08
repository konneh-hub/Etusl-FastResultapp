from rest_framework import serializers
from notifications.models import Notification, Announcement, Broadcast


class NotificationSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'user', 'user_email', 'title', 'message', 'notification_type', 'read', 'created_at', 'read_at']
        read_only_fields = ['id', 'created_at']


class AnnouncementSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'message', 'created_by', 'created_by_name', 'created_at', 'target_role', 'is_active']
        read_only_fields = ['id', 'created_at']


class BroadcastSerializer(serializers.ModelSerializer):
    recipient_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Broadcast
        fields = ['id', 'title', 'content', 'sent_at', 'recipient_count']
        read_only_fields = ['id', 'sent_at']
    
    def get_recipient_count(self, obj):
        return obj.recipients.count()


class BroadcastDetailSerializer(serializers.ModelSerializer):
    recipients = serializers.SerializerMethodField()
    
    class Meta:
        model = Broadcast
        fields = ['id', 'title', 'content', 'sent_at', 'recipients']
        read_only_fields = ['id', 'sent_at']
    
    def get_recipients(self, obj):
        return [
            {'id': user.id, 'email': user.email, 'name': user.get_full_name()}
            for user in obj.recipients.all()
        ]
