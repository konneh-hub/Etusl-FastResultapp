from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from notifications.models import Notification, Announcement, Broadcast
from notifications.serializers import (
    NotificationSerializer,
    AnnouncementSerializer,
    BroadcastSerializer,
    BroadcastDetailSerializer,
)


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for Notification model"""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'notification_type', 'read']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_notifications(self, request):
        """Get current user's notifications"""
        notifications = Notification.objects.filter(user=request.user)
        
        page = self.paginate_queryset(notifications)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def unread(self, request):
        """Get unread notifications for current user"""
        notifications = Notification.objects.filter(user=request.user, read=False)
        
        page = self.paginate_queryset(notifications)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_as_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.read = True
        notification.read_at = timezone.now()
        notification.save()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_all_as_read(self, request):
        """Mark all notifications as read for current user"""
        from django.utils import timezone
        notifications = Notification.objects.filter(user=request.user, read=False)
        notifications.update(read=True, read_at=timezone.now())
        return Response({'message': 'All notifications marked as read'})


class AnnouncementViewSet(viewsets.ModelViewSet):
    """ViewSet for Announcement model"""
    queryset = Announcement.objects.filter(is_active=True)
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['target_role', 'is_active']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class BroadcastViewSet(viewsets.ModelViewSet):
    """ViewSet for Broadcast model"""
    queryset = Broadcast.objects.all()
    serializer_class = BroadcastSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BroadcastDetailSerializer
        return BroadcastSerializer
