import csv
import io
from django.db import transaction
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django_filters.rest_framework import DjangoFilterBackend
from accounts.models import User
from accounts.serializers import (
    UserSerializer, 
    UserDetailSerializer,
    UserCreateSerializer, 
    LoginSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer,
    AccountClaimSerializer,
    BulkPreloadSerializer,
    PreloadedUserSerializer,
)


class AccountClaimView(APIView):
    """Claim and activate a preloaded account"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = AccountClaimSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            password = serializer.validated_data['password']
            
            # Set password and activate account
            user.set_password(password)
            user.is_active = True
            user.is_verified = True
            user.is_preloaded = False
            user.save()
            
            # Generate token
            token, _ = Token.objects.get_or_create(user=user)
            
            return Response({
                'message': 'Account activated successfully',
                'user': UserSerializer(user).data,
                'token': token.key,
                'role': user.role,
                'email': user.email,
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthLoginView(APIView):
    """User login endpoint - returns token"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            # Find user by email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {'error': 'Invalid email or password'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Check password
            if not user.check_password(password):
                return Response(
                    {'error': 'Invalid email or password'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # User must be active and verified
            if not user.is_active or not user.is_verified:
                return Response(
                    {'error': 'Account not activated. Please activate your account first.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Generate token
            token, _ = Token.objects.get_or_create(user=user)
            user.last_login = timezone.now()
            user.save()
            
            # Return with dashboard route based on role
            dashboard_routes = {
                'student': '/student',
                'lecturer': '/lecturer',
                'dean': '/dean',
                'hod': '/hod',
                'exam_officer': '/exam',
                'university_admin': '/admin',
            }
            
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key,
                'role': user.role,
                'dashboard_route': dashboard_routes.get(user.role, '/student'),
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BulkPreloadView(APIView):
    """Bulk preload users from CSV"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Only university_admin can bulk preload
        if request.user.role != 'university_admin':
            return Response(
                {'error': 'Only University Admin can bulk preload users'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = BulkPreloadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        csv_file = serializer.validated_data['csv_file']
        university_id = serializer.validated_data['university_id']
        role = serializer.validated_data['role']
        
        try:
            # Parse CSV
            decoded_file = csv_file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded_file))
            
            created = 0
            skipped = 0
            errors = []
            
            with transaction.atomic():
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (skip header)
                    try:
                        email = row.get('email', '').strip()
                        first_name = row.get('first_name', '').strip()
                        last_name = row.get('last_name', '').strip()
                        id_field = row.get('student_id' if role == 'student' else 'staff_id', '').strip()
                        dob = row.get('date_of_birth', '').strip()
                        
                        # Validate required fields
                        if not all([email, first_name, last_name, id_field]):
                            errors.append(f'Row {row_num}: Missing required fields')
                            skipped += 1
                            continue
                        
                        # Check if user already exists
                        if role == 'student' and User.objects.filter(student_id=id_field).exists():
                            skipped += 1
                            continue
                        elif role == 'lecturer' and User.objects.filter(staff_id=id_field).exists():
                            skipped += 1
                            continue
                        
                        # Check if email already exists
                        if User.objects.filter(email=email).exists():
                            skipped += 1
                            continue
                        
                        # Create user
                        username = f"{id_field.lower()}"
                        kwargs = {
                            'username': username,
                            'email': email,
                            'first_name': first_name,
                            'last_name': last_name,
                            'role': role,
                            'university_id': university_id,
                            'is_preloaded': True,
                            'is_active': False,
                        }
                        
                        if role == 'student':
                            kwargs['student_id'] = id_field
                        else:
                            kwargs['staff_id'] = id_field
                        
                        if dob:
                            try:
                                kwargs['date_of_birth'] = dob
                            except:
                                pass
                        
                        user = User.objects.create(**kwargs)
                        created += 1
                    
                    except Exception as e:
                        errors.append(f'Row {row_num}: {str(e)}')
                        skipped += 1
            
            return Response({
                'message': f'Bulk preload completed',
                'created': created,
                'skipped': skipped,
                'errors': errors if errors else None,
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': f'Failed to process CSV: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserViewSet(viewsets.ModelViewSet):
    """User management endpoints"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active', 'is_verified', 'is_preloaded', 'university']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'student_id', 'staff_id']
    ordering_fields = ['username', 'email', 'created_at']
    ordering = ['username']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action in ['partial_update', 'update_profile']:
            return UserUpdateSerializer
        elif self.action == 'change_password':
            return PasswordChangeSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user profile"""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """Update current user profile"""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserDetailSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """Change password for current user"""
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            if not request.user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'error': 'Old password is incorrect'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({'message': 'Password changed successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Logout user"""
        try:
            request.user.auth_token.delete()
        except:
            pass
        return Response({'message': 'Logged out successfully'})


