"""
Tests for accounts app - Controlled Registration System
"""
import pytest
from datetime import date
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def preloaded_user():
    """Create a preloaded but inactive user"""
    return User.objects.create(
        username='preloaded_student',
        email='student@example.com',
        first_name='John',
        last_name='Doe',
        student_id='STU001',
        date_of_birth=date(2000, 1, 15),
        role='student',
        is_preloaded=True,
        is_active=False,
        is_verified=False,
    )


@pytest.fixture
def activated_user():
    """Create an activated user for login"""
    user = User.objects.create(
        username='activated_student',
        email='activated@example.com',
        first_name='Jane',
        last_name='Smith',
        student_id='STU002',
        role='student',
        is_preloaded=False,
        is_active=True,
        is_verified=True,
    )
    user.set_password('secure123')
    user.save()
    return user


@pytest.mark.django_db
class TestControlledRegistration:
    """Test the controlled registration system (no public signup)"""
    
    def test_no_public_registration(self, api_client):
        """Verify registration endpoint does not exist"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'secure123',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        # Should return 404 or not allowed
        response = api_client.post('/api/v1/auth/register/', data)
        assert response.status_code in [404, 405]
    
    def test_claim_account_with_valid_data(self, api_client, preloaded_user):
        """Test account claiming with valid preloaded user data"""
        data = {
            'student_id': 'STU001',
            'email': 'student@example.com',
            'date_of_birth': '2000-01-15',
            'password': 'NewSecure123!',
            'password_confirm': 'NewSecure123!',
        }
        response = api_client.post('/api/v1/auth/claim-account/', data)
        assert response.status_code == 200
        assert 'token' in response.data
        
        # Verify user is now active and verified
        preloaded_user.refresh_from_db()
        assert preloaded_user.is_active is True
        assert preloaded_user.is_verified is True
        assert preloaded_user.is_preloaded is False
    
    def test_claim_account_wrong_email(self, api_client, preloaded_user):
        """Test account claiming fails with wrong email"""
        data = {
            'student_id': 'STU001',
            'email': 'wrong@example.com',
            'date_of_birth': '2000-01-15',
            'password': 'NewSecure123!',
            'password_confirm': 'NewSecure123!',
        }
        response = api_client.post('/api/v1/auth/claim-account/', data)
        assert response.status_code == 400
    
    def test_claim_account_wrong_dob(self, api_client, preloaded_user):
        """Test account claiming fails with wrong DOB"""
        data = {
            'student_id': 'STU001',
            'email': 'student@example.com',
            'date_of_birth': '2000-02-15',  # Wrong date
            'password': 'NewSecure123!',
            'password_confirm': 'NewSecure123!',
        }
        response = api_client.post('/api/v1/auth/claim-account/', data)
        assert response.status_code == 400
    
    def test_login_email_based(self, api_client, activated_user):
        """Test email-based login (not username)"""
        data = {
            'email': 'activated@example.com',
            'password': 'secure123'
        }
        response = api_client.post('/api/v1/auth/login/', data)
        assert response.status_code == 200
        assert 'token' in response.data
        assert response.data['role'] == 'student'
        assert 'dashboard_route' in response.data
    
    def test_login_wrong_email(self, api_client):
        """Test login fails with wrong email"""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'anypassword'
        }
        response = api_client.post('/api/v1/auth/login/', data)
        assert response.status_code == 401
    
    def test_login_wrong_password(self, api_client, activated_user):
        """Test login fails with wrong password"""
        data = {
            'email': 'activated@example.com',
            'password': 'wrongpassword'
        }
        response = api_client.post('/api/v1/auth/login/', data)
        assert response.status_code == 401
    
    def test_login_preloaded_inactive_user_fails(self, api_client, preloaded_user):
        """Test login fails for inactive preloaded users"""
        preloaded_user.set_password('anypassword')
        preloaded_user.save()
        
        data = {
            'email': 'student@example.com',
            'password': 'anypassword'
        }
        response = api_client.post('/api/v1/auth/login/', data)
        assert response.status_code == 403  # Not activated
    
    def test_dashboard_route_by_role(self, api_client):
        """Test dashboard routes are correct for different roles"""
        roles_and_routes = {
            'student': '/student',
            'lecturer': '/lecturer',
            'dean': '/dean',
            'hod': '/hod',
            'exam_officer': '/exam',
            'university_admin': '/admin',
        }
        
        for role, expected_route in roles_and_routes.items():
            user = User.objects.create(
                username=f'user_{role}',
                email=f'{role}@example.com',
                role=role,
                is_active=True,
                is_verified=True,
            )
            user.set_password('password123')
            user.save()
            
            response = api_client.post('/api/v1/auth/login/', {
                'email': f'{role}@example.com',
                'password': 'password123'
            })
            assert response.status_code == 200
            assert response.data['dashboard_route'] == expected_route

