from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import UserViewSet, AccountClaimView, AuthLoginView, BulkPreloadView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('claim-account/', AccountClaimView.as_view(), name='claim-account'),
    path('login/', AuthLoginView.as_view(), name='login'),
    path('bulk-preload/', BulkPreloadView.as_view(), name='bulk-preload'),
    path('', include(router.urls)),
]
