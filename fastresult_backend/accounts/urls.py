from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import AuthRegisterView, AuthLoginView, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('register/', AuthRegisterView.as_view(), name='register'),
    path('login/', AuthLoginView.as_view(), name='login'),
    path('', include(router.urls)),
]
