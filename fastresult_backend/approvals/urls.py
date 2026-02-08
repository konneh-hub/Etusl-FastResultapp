from django.urls import path, include
from rest_framework.routers import DefaultRouter
from approvals.views import (
    ResultSubmissionViewSet,
    ApprovalStageViewSet,
    ApprovalActionViewSet,
    ApprovalHistoryViewSet,
    CorrectionRequestViewSet,
)

router = DefaultRouter()
router.register(r'submissions', ResultSubmissionViewSet, basename='result-submission')
router.register(r'stages', ApprovalStageViewSet, basename='approval-stage')
router.register(r'actions', ApprovalActionViewSet, basename='approval-action')
router.register(r'histories', ApprovalHistoryViewSet, basename='approval-history')
router.register(r'corrections', CorrectionRequestViewSet, basename='correction-request')

urlpatterns = [
    path('', include(router.urls)),
]
