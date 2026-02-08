# DRF API Layer Design Rules - SRMS

**Scope**: REST API layer principles for Django REST Framework  
**Status**: Design Specification (No Implementation Code)

---

## PART I: API LAYER ARCHITECTURE

### **Pattern: Service-First API Layer**

```
Request
  ↓
┌─────────────────────────────┐
│ ViewSet (Routing Layer)     │ ← Handles HTTP only
│ - URL routing              │ ← Calls service
│ - 404/405 responses        │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│ Serializer (Data Layer)     │ ← Validation + Transformation
│ - Input validation          │ ← Calls business logic
│ - Output formatting         │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│ Service Layer (Business)    │ ← Where work happens
│ - Authorization             │ ← Calls models
│ - Data updates              │
│ - Business rules            │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│ Models (Data Layer)         │ ← Database
│ - ORM queries               │
│ - Constraints               │
└─────────────────────────────┘
```

**Critical Rule**: ViewSets ONLY handle HTTP.  
All business logic MUST go in Services.

---

## PART II: VIEWSET PATTERNS

### **Pattern 1: Read-Only ViewSet (Results)**

**Purpose**: List and retrieve results (filtering/pagination)

```python
# Directory: results/views/__init__.py
# or: results/views/result_views.py

class ResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/results/ - List results (paginated)
    GET /api/results/{id}/ - Retrieve result detail
    
    Filtering: ?status=submitted&semester=1
    Pagination: ?page=1&page_size=20
    """
    
    permission_classes = [IsAuthenticated]
    # Applied to all actions
    
    serializer_class = ResultDetailSerializer
    pagination_class = StandardResultPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'is_locked']
    search_fields = ['student_enrollment__student_profile__matric_number']
    ordering_fields = ['entered_at', 'submitted_at', 'total_score']
    ordering = ['-entered_at']
    
    def get_queryset(self):
        """
        CRITICAL: Apply university scoping here
        Every queryset MUST filter by user's university
        """
        user = self.request.user
        university = user.get_primary_university()
        
        # Scope: Only results from user's university
        return ResultRecord.objects.filter(
            student_enrollment__course__program__department__faculty__university=university
        ).select_related(
            'student_enrollment__student_profile',
            'student_enrollment__course',
        )
    
    def get_serializer_context(self):
        """Add request context to serializer"""
        context = super().get_serializer_context()
        context['university'] = self.request.user.get_primary_university()
        return context
```

### **Pattern 2: Create/Update ViewSet (Results)**

**Purpose**: Create and update results (calls service layer)

```python
class ResultEntryViewSet(viewsets.ModelViewSet):
    """
    POST /api/result-entry/ - Create new result entry
    PATCH /api/result-entry/{id}/ - Update result (if draft)
    GET /api/result-entry/{id}/submit/ - Submit result
    GET /api/result-entry/{id}/ - Retrieve result
    """
    
    permission_classes = [IsAuthenticated, IsLecturerOrAbove]
    
    serializer_class = ResultEntrySerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create new result for student+course.
        Calls ResultService.create_result()
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Call service layer
        result_service = ResultEntryService(
            user=request.user,
            university=request.user.get_primary_university(),
            audit_service=self._get_audit_service(request),
        )
        
        result = result_service.create_result(
            student_enrollment_id=serializer.validated_data['student_enrollment_id'],
        )
        
        # Serialize response
        output_serializer = ResultDetailSerializer(result)
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    def partial_update(self, request, *args, **kwargs):
        """
        Update result (if draft).
        Updates scores via service layer.
        """
        result = self.get_object()
        serializer = self.get_serializer(result, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Call service layer
        result_service = ResultEntryService(request.user, request.user.get_primary_university())
        updated_result = result_service.update_scores(
            result_id=result.id,
            component_data=serializer.validated_data['component_scores'],
        )
        
        output_serializer = ResultDetailSerializer(updated_result)
        return Response(output_serializer.data)
    
    def get_queryset(self):
        """Scope to user's university + lecturer's courses"""
        user = self.request.user
        university = user.get_primary_university()
        
        # Lecturer can only see own result entries
        return ResultRecord.objects.filter(
            student_enrollment__course__program__department__faculty__university=university,
            lecturer=user.university_users.get(university=university),
        )
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        POST /api/result-entry/{id}/submit/
        Submit result for approval.
        """
        result = self.get_object()
        
        # Call service
        result_service = ResultEntryService(request.user, request.user.get_primary_university())
        submitted_result = result_service.submit_result(result.id)
        
        serializer = ResultDetailSerializer(submitted_result)
        return Response(serializer.data)
    
    def _get_audit_service(self, request):
        """Helper to get audit service"""
        from core.audit.services import AuditLoggingService
        return AuditLoggingService(request, request.user.get_primary_university())
```

---

## PART III: SERIALIZER PATTERNS

### **Pattern 1: List Serializer (Minimal)**

**Purpose**: For list endpoints, return minimal data

```python
class ResultListSerializer(serializers.ModelSerializer):
    """Minimal serializer for list endpoints"""
    
    student_matric = serializers.CharField(
        source='student_enrollment.student_profile.matric_number',
        read_only=True
    )
    
    course_code = serializers.CharField(
        source='student_enrollment.course.code',
        read_only=True
    )
    
    class Meta:
        model = ResultRecord
        fields = [
            'id',
            'student_matric',
            'course_code',
            'total_score',
            'grade',
            'status',
            'entered_at',
        ]
        read_only_fields = fields
```

### **Pattern 2: Detail Serializer (Complete)**

**Purpose**: For detail endpoints, return all data

```python
class ResultDetailSerializer(serializers.ModelSerializer):
    """Complete serializer for detail/update endpoints"""
    
    student = StudentProfileSerializer(
        source='student_enrollment.student_profile',
        read_only=True
    )
    
    course = CourseBasicSerializer(
        source='student_enrollment.course',
        read_only=True
    )
    
    component_scores = ResultComponentScoreSerializer(
        many=True,
        read_only=True
    )
    
    class Meta:
        model = ResultRecord
        fields = [
            'id',
            'student',
            'course',
            'status',
            'total_score',
            'grade',
            'component_scores',
            'entered_at',
            'submitted_at',
            'last_modified_at',
        ]
        read_only_fields = [
            'id', 'status', 'total_score', 'grade',
            'entered_at', 'submitted_at', 'last_modified_at',
        ]
```

### **Pattern 3: Input Serializer (For Creates)**

**Purpose**: Validates and transforms input data

```python
class ResultEntryInputSerializer(serializers.Serializer):
    """Input validation for creating result"""
    
    student_enrollment_id = serializers.IntegerField()
    
    component_scores = serializers.ListField(
        child=serializers.DictField(
            child=serializers.DecimalField(max_digits=5, decimal_places=2)
        )
    )
    # [
    #   {"ca": 28, "exam": 47.5},
    # ]
    
    def validate_student_enrollment_id(self, value):
        """Validate enrollment exists and is active"""
        try:
            enrollment = StudentCourseEnrollment.objects.get(
                id=value,
                status='active'
            )
            return value
        except StudentCourseEnrollment.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive enrollment")
    
    def validate_component_scores(self, value):
        """Validate scores match assessment components"""
        if not value:
            raise serializers.ValidationError("At least one component score required")
        return value
```

---

## PART IV: ERROR HANDLING

### **Pattern: Standard Error Responses**

```python
class StandardErrorResponse:
    """All error responses follow this pattern"""
    
    # 400 Bad Request (Validation error)
    {
        "error": "validation_error",
        "message": "Invalid input data",
        "details": {
            "component_scores": ["This field is required"]
        }
    }
    
    # 401 Unauthorized (Not authenticated)
    {
        "error": "authentication_required",
        "message": "Authentication credentials were not provided"
    }
    
    # 403 Forbidden (Permission denied)
    {
        "error": "permission_denied",
        "message": "You do not have permission to perform this action",
        "detail": "Only lecturer can enter results"
    }
    
    # 404 Not Found
    {
        "error": "not_found",
        "message": "Result not found"
    }
    
    # 409 Conflict (State error)
    {
        "error": "invalid_state",
        "message": "Cannot update locked result"
    }
    
    # 500 Server Error
    {
        "error": "server_error",
        "message": "An unexpected error occurred",
        "reference_id": "abc123"  # For support tickets
    }
```

### **Pattern: Custom Exception Handler**

```python
def custom_exception_handler(exc, context):
    """
    Custom exception handler for consistency
    Applied in settings.py REST_FRAMEWORK config
    """
    
    if isinstance(exc, ValidationError):
        return Response(
            {
                "error": "validation_error",
                "details": exc.detail
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    elif isinstance(exc, PermissionDenied):
        return Response(
            {
                "error": "permission_denied",
                "message": "You don't have permission for this action"
            },
            status=status.HTTP_403_FORBIDDEN
        )
    
    elif isinstance(exc, NotFound):
        return Response(
            {
                "error": "not_found",
                "message": "Resource not found"
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    else:
        # Log unexpected error
        logger.error(f"Unexpected error: {exc}")
        return Response(
            {
                "error": "server_error",
                "reference_id": context.get('request').id
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
```

---

## PART V: FILTERING & PAGINATION

### **Pattern 1: University Scoped Filter**

**Purpose**: Every ViewSet MUST filter by university in get_queryset()

```python
class UniversityScopedMixin:
    """Mixin to ensure all queries are university-scoped"""
    
    def get_queryset(self):
        """Override in subclass - MUST filter by university"""
        user = self.request.user
        university = user.get_primary_university()
        
        # Base queryset - to be extended in subclass
        queryset = self.model.objects.all()
        
        # Apply university scoping (pattern varies by model)
        # Some: direct FK to university
        # Some: nested FK (course → program → department → faculty → university)
        
        return queryset
```

### **Pattern 2: Standard Pagination**

```python
class StandardResultPagination(pagination.PageNumberPagination):
    """Standard pagination for all result lists"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class StandardUserPagination(pagination.PageNumberPagination):
    """Standard pagination for user lists"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200
```

### **Pattern 3: Filtering Examples**

```
GET /api/results/?status=submitted&course_code=CS101&page=1&page_size=20
GET /api/users/?role=lecturer&department_id=5
GET /api/transcripts/?classification=1st_class
```

---

## PART VI: AUTHENTICATION & SCOPING

### **Pattern: Multi-Layer Scoping**

```python
# Layer 1: Authentication
# Verified by: @permission_classes([IsAuthenticated])

# Layer 2: University Scoping
# Verified in: ViewSet.get_queryset()
# Example: filter(..., university=user.get_primary_university())

# Layer 3: Department/Faculty Scoping (if applicable)
# Verified in: Permission class + service layer
# Example: HOD can only see own department results

# Layer 4: University-User Assignment
# Verified: UniversityUser.is_active & is_approved


class ExampleScoping:
    """Complete scoping example"""
    
    def get_queryset(self):
        user = self.request.user
        university_user = user.get_university_user(self.university_id)
        
        if university_user.role.code == 'lecturer':
            # Lecturer sees only own course results
            return ResultRecord.objects.filter(
                student_enrollment__course__lecturer=university_user,
                student_enrollment__course__program__department__faculty__university=self.university_id
            )
        
        elif university_user.role.code == 'hod':
            # HOD sees all department results
            return ResultRecord.objects.filter(
                student_enrollment__course__program__department=university_user.department,
            )
        
        elif university_user.role.code == 'dean':
            # Dean sees all faculty results
            return ResultRecord.objects.filter(
                student_enrollment__course__program__department__faculty=university_user.faculty,
            )
        
        elif university_user.role.code == 'university_admin':
            # Admin sees all university results
            return ResultRecord.objects.filter(
                student_enrollment__course__program__department__faculty__university=self.university_id
            )
```

---

## PART VII: API ENDPOINTS ORGANIZATION

### **URL Routing Pattern**

```
# backend/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Results app
from results.views import ResultViewSet, ResultEntryViewSet

router = DefaultRouter()
router.register(r'results', ResultViewSet, basename='result')
router.register(r'result-entry', ResultEntryViewSet, basename='result-entry')

urlpatterns = [
    path('api/', include(router.urls)),
    
    # Custom endpoints (if needed)
    path('api/results/<int:pk>/approve/', 
         ApproveResultView.as_view(), 
         name='approve-result'),
]
```

### **Endpoint List Pattern**

```
# Results Module
GET    /api/results/                    List results (paginated)
GET    /api/results/{id}/               Retrieve result
GET    /api/results/?status=submitted   Filter by status
POST   /api/result-entry/               Create new result
PATCH  /api/result-entry/{id}/          Update result (if draft)
POST   /api/result-entry/{id}/submit/   Submit result
POST   /api/result-entry/{id}/approve/  Approve result
POST   /api/result-entry/{id}/reject/   Reject result

# Users Module
GET    /api/users/                      List users
GET    /api/users/{id}/                 Retrieve user
POST   /api/users/                      Create user (admin only)
PATCH  /api/users/{id}/                 Update user (admin only)
POST   /api/users/{id}/assign-role/     Assign role (admin only)

# Transcripts Module
GET    /api/transcripts/my/             Get own transcript
GET    /api/transcripts/{id}/           Get transcript (admin)
POST   /api/transcripts/{id}/issue/     Issue transcript (admin only)
GET    /api/transcripts/{id}/pdf/       Download as PDF
POST   /api/transcripts/{id}/verify/    Verify transcript
```

---

## PART VIII: RESPONSE FORMAT

### **Standard Success Response**

```python
# Single resource
{
    "id": 123,
    "student_matric": "STU-2020-001",
    "course_code": "CS101",
    "total_score": 78.5,
    "grade": "B",
    "status": "submitted",
    "entered_at": "2024-01-15T10:30:00Z"
}

# List with pagination
{
    "count": 450,
    "next": "http://api.example.com/results/?page=2",
    "previous": null,
    "results": [
        {...},
        {...}
    ]
}

# Create/Update response
{
    "id": 123,
    "message": "Result created successfully",
    "data": {...}
}
```

---

## PART IX: VERSIONING

### **Optional: API Versioning**

```python
# If versioning needed later:
# Option 1: URL versioning
GET /api/v1/results/
GET /api/v2/results/

# Option 2: Header versioning
GET /api/results/
Headers: Accept: application/json; version=1.0

# Current: No versioning (v1 only)
# Can add later if breaking changes needed
```

---

## SUMMARY

**API Layer Principles**:
1. ✅ ViewSets handle HTTP only
2. ✅ Serializers validate + transform input
3. ✅ Services contain business logic
4. ✅ Every query scoped to university
5. ✅ Consistent error responses
6. ✅ Standard pagination + filtering
7. ✅ Multi-layer authentication + scoping
8. ✅ Audit all write operations
9. ✅ Required fields documented in serializers
10. ✅ All actions require IsAuthenticated

---

**Status**: DRF API Layer Design Complete  
**Next Steps**: Permission System, React Frontend Structure  
**Last Updated**: 2026-02-07
