from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from approvals.models import ResultSubmission, ApprovalStage, ApprovalAction, ApprovalHistory, CorrectionRequest
from approvals.serializers import (
    ResultSubmissionSerializer,
    ResultSubmissionDetailSerializer,
    ApprovalStageSerializer,
    ApprovalActionSerializer,
    ApprovalHistorySerializer,
    CorrectionRequestSerializer,
)


class ResultSubmissionViewSet(viewsets.ModelViewSet):
    """ViewSet for ResultSubmission model"""
    queryset = ResultSubmission.objects.all()
    serializer_class = ResultSubmissionSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'submitted_by']
    ordering_fields = ['submitted_at']
    ordering = ['-submitted_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ResultSubmissionDetailSerializer
        return ResultSubmissionSerializer
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        """Approve a submission"""
        submission = self.get_object()
        submission.status = 'approved'
        submission.save()
        serializer = self.get_serializer(submission)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        """Reject a submission"""
        submission = self.get_object()
        submission.status = 'rejected'
        submission.save()
        serializer = self.get_serializer(submission)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def request_revision(self, request, pk=None):
        """Request revision on a submission"""
        submission = self.get_object()
        submission.status = 'revision_requested'
        submission.save()
        serializer = self.get_serializer(submission)
        return Response(serializer.data)


class ApprovalStageViewSet(viewsets.ModelViewSet):
    """ViewSet for ApprovalStage model"""
    queryset = ApprovalStage.objects.all()
    serializer_class = ApprovalStageSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['submission', 'status', 'approver_role']
    ordering_fields = ['stage_number']
    ordering = ['stage_number']


class ApprovalActionViewSet(viewsets.ModelViewSet):
    """ViewSet for ApprovalAction model"""
    queryset = ApprovalAction.objects.all()
    serializer_class = ApprovalActionSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['stage', 'approver', 'action']
    ordering_fields = ['acted_at']
    ordering = ['-acted_at']


class ApprovalHistoryViewSet(viewsets.ModelViewSet):
    """ViewSet for ApprovalHistory model"""
    queryset = ApprovalHistory.objects.all()
    serializer_class = ApprovalHistorySerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['submission', 'action_type']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']


class CorrectionRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for CorrectionRequest model"""
    queryset = CorrectionRequest.objects.all()
    serializer_class = CorrectionRequestSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['submission', 'requested_by']
    ordering_fields = ['requested_at']
    ordering = ['-requested_at']
