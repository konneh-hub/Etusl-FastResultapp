# Quick Start: Testing the Backend API

## Starting the Backend Server

```bash
cd c:\SRMS\fastresult_backend

# Create virtual environment (first time)
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements/base.txt

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

The backend will be available at: `http://localhost:8000`

## API Documentation

### Swagger UI
- **URL**: http://localhost:8000/api/docs/
- **Interactive** endpoint testing
- **Request/Response** examples
- **Authentication** support

### ReDoc
- **URL**: http://localhost:8000/api/redoc/
- **Alternative** documentation
- **Schema reference**

### OpenAPI Schema
- **URL**: http://localhost:8000/api/schema/
- **Machine-readable** specification

## Sample API Requests

### 1. Claim Account (Activate Preloaded)
```bash
POST http://localhost:8000/api/v1/auth/claim-account/
Content-Type: application/json

{
  "student_id": "STU001",
  "email": "john@example.com",
  "date_of_birth": "2000-01-15",
  "password": "SecurePass123",
  "password_confirm": "SecurePass123"
}

Response: 200 OK
{
  "message": "Account activated successfully",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "role": "student",
    ...
  },
  "token": "abc123xyz789...",
  "role": "student"
}
```

### 2. Login
```bash
POST http://localhost:8000/api/v1/auth/login/
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123"
}

Response: 200 OK
{
  "user": {...},
  "token": "abc123xyz789..."
}
```

### 3. Get Current User
```bash
GET http://localhost:8000/api/v1/auth/users/me/
Authorization: Token abc123xyz789...

Response: 200 OK
{
  "id": 1,
  "username": "john_student",
  "email": "john@example.com",
  "role": "student",
  "is_verified": false,
  "is_active": true,
  ...
}
```

### 4. List Faculties with Filtering
```bash
GET http://localhost:8000/api/v1/academics/faculties/?page=1&page_size=10
Authorization: Token abc123xyz789...

Response: 200 OK
{
  "count": 25,
  "next": "http://localhost:8000/api/v1/academics/faculties/?page=2&page_size=10",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Faculty of Science",
      "code": "FS",
      ...
    }
  ]
}
```

### 5. Search Courses
```bash
GET http://localhost:8000/api/v1/academics/courses/?search=mathematics
Authorization: Token abc123xyz789...

Response: 200 OK
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "name": "Advanced Mathematics",
      "code": "MATH301",
      ...
    }
  ]
}
```

### 6. Get Student Results
```bash
GET http://localhost:8000/api/v1/results/results/my_results/
Authorization: Token <student-token>

Response: 200 OK
{
  "count": 8,
  "results": [
    {
      "id": 1,
      "student_matric": "STU001",
      "course_name": "Introduction to Computer Science",
      "course_code": "CS101",
      "semester": "2023/2024 - Semester 1",
      "status": "published",
      ...
    }
  ]
}
```

### 7. Get Student GPA
```bash
GET http://localhost:8000/api/v1/results/gpa/my_gpa/
Authorization: Token <student-token>

Response: 200 OK
{
  "count": 2,
  "results": [
    {
      "student_matric": "STU001",
      "semester": "2023/2024 - Semester 1",
      "gpa": 3.85,
      "total_credits": 45,
      "quality_points": 173.25
    }
  ]
}
```

### 8. Get Unread Notifications
```bash
GET http://localhost:8000/api/v1/notifications/notifications/unread/
Authorization: Token <user-token>

Response: 200 OK
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "title": "Result Published",
      "message": "Your results for CS101 have been published",
      "notification_type": "result_release",
      "read": false,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

## Filtering Examples

### By Status
```bash
GET /api/v1/results/results/?status=published
```

### By Semester
```bash
GET /api/v1/academics/courses/?program=1&semester=1
```

### By Date Range (using ordering)
```bash
GET /api/v1/results/results/?ordering=-created_at
```

### Multiple Filters
```bash
GET /api/v1/academics/courses/?program=2&is_required=true&ordering=code
```

## Frontend Integration

Update your `apiClient.js` baseURL:

```javascript
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';
```

All frontend service methods will automatically work with these endpoints.

## Common Issues & Solutions

### Issue: "Unsupported media type"
**Solution**: Add `Content-Type: application/json` header to POST/PATCH requests

### Issue: "Not authenticated"
**Solution**: 
1. Claim account or login first to get token
2. Add `Authorization: Token <your-token>` to all requests (except claim-account/login)

### Issue: "Permission denied"
**Solution**:
1. Check user role matches endpoint requirements
2. Students can only access their own data
3. Admins have full access

### Issue: "Database locked"
**Solution**: 
- SQLite has limited concurrent access
- For production: use PostgreSQL
- Check if another process has the database open

### Issue: "CORS Error"
**Solution**:
- Frontend and backend running on same machine: CORS already configured
- Different machines: Add frontend URL to `CORS_ALLOWED_ORIGINS` in settings/base.py

## Performance Tips

1. **Pagination**: Use `page_size` to limit results
2. **Filtering**: Add filters to reduce database load
3. **Search**: Better than full-text when possible
4. **Batch Operations**: Would need custom endpoints (for future enhancement)

## Database Management

### Backup Database
```bash
cp db.sqlite3 db.sqlite3.backup
```

### Reset Database (CAUTION: deletes all data)
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### View Data
```bash
python manage.py dbshell
sqlite> SELECT * FROM accounts_user;
```

## Next Steps

1. ✅ **Start the backend server** (see above)
2. ✅ **Test endpoints** using Swagger UI or Postman
3. ✅ **Verify frontend connects** to backend
4. ✅ **Check role-based access** works correctly
5. ✅ **Deploy to production** when ready

## Files Modified/Created

- ✅ 10+ `serializers.py` files
- ✅ 10+ `views.py` files  
- ✅ Updated all `urls.py` files
- ✅ Enhanced authentication system
- ✅ Added filtering to all viewsets
- ✅ Implemented pagination

## Support

For any issues:
1. Check the error message in response
2. Verify token is included in Authorization header
3. Check user role matches endpoint permissions
4. Review Swagger documentation for correct request format
5. Check database is migrated: `python manage.py migrate`

---

**Status**: ✅ Backend is fully implemented and ready for testing!

Start the server and visit http://localhost:8000/api/docs/ to explore all endpoints.
