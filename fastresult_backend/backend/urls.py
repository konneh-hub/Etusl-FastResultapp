"""
URL Configuration for FastResult backend.
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', include('health_check.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API versioning
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/universities/', include('universities.urls')),
    path('api/v1/academics/', include('academics.urls')),
    path('api/v1/students/', include('students.urls')),
    path('api/v1/lecturers/', include('lecturers.urls')),
    path('api/v1/exams/', include('exams.urls')),
    path('api/v1/results/', include('results.urls')),
    path('api/v1/approvals/', include('approvals.urls')),
    path('api/v1/reports/', include('reports.urls')),
    path('api/v1/notifications/', include('notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
