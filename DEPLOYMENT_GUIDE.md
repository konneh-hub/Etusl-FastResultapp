# FastResult - Complete Deployment & Development Guide

## Quick Start (All-in-One)

### Option 1: Docker Compose (Recommended)
```bash
docker-compose up
```

Then access:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8000/admin
- API Docs: http://localhost:8000/api/docs/

### Option 2: Manual Setup

#### Backend Setup
```bash
cd fastresult_backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/dev.txt

# Create .env file
cp .env.example .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
```

#### Frontend Setup
```bash
cd fastresult_frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env.local

# Start dev server
npm run dev
```

## Project Overview

FastResult is a comprehensive student result management system with:

### Key Features
- **Multi-role access control** (6 user roles)
- **Academic structure management**
- **Result entry & validation**
- **GPA/CGPA calculation engine**
- **Multi-level approval workflows**
- **Transcript generation**
- **Comprehensive reporting**
- **Audit logging**
- **Notification system**

### Architecture
```
Frontend (React + Redux)
    ↓ (Axios API calls)
Backend (Django REST API)
    ↓
Database (SQLite/PostgreSQL)
```

## Directory Structure

```
fastresult/
├── fastresult_backend/        # Django REST API
│   ├── accounts/              # User authentication
│   ├── universities/          # University structure
│   ├── academics/             # Faculty/Department/Courses
│   ├── students/              # Student management
│   ├── lecturers/             # Lecturer management
│   ├── results/               # Result management
│   ├── approvals/             # Approval workflows
│   ├── reports/               # Analytics
│   ├── notifications/         # Messaging
│   └── audit/                 # Logging
│
├── fastresult_frontend/       # React SPA
│   ├── src/
│   │   ├── modules/           # Feature modules by role
│   │   ├── components/        # Reusable components
│   │   ├── services/          # API clients
│   │   ├── store/             # Redux slices
│   │   ├── hooks/             # Custom hooks
│   │   └── utils/             # Helpers
│   └── index.html             # Entry point
│
├── docker-compose.yml         # Multi-container setup
└── README.md                  # This file
```

## API Endpoints

### Authentication
```
POST   /api/v1/auth/claim-account/      Activate preloaded account
POST   /api/v1/auth/bulk-preload/       Bulk preload users (admin)
POST   /api/v1/auth/login/              Email-based login
POST   /api/v1/auth/users/logout/       Logout
GET    /api/v1/auth/users/me/           Current user
```

### Universities & Academic
```
GET    /api/v1/universities/            List universities
GET    /api/v1/universities/academic-years/
GET    /api/v1/universities/semesters/
GET    /api/v1/academics/faculties/
GET    /api/v1/academics/departments/
GET    /api/v1/academics/courses/
```

### Results
```
GET    /api/v1/results/                 List results
POST   /api/v1/results/                 Create result
GET    /api/v1/results/{id}/            Get result detail
PUT    /api/v1/results/{id}/            Update result
GET    /api/v1/results/transcript/{sid}/ Student transcript
```

### Approvals
```
GET    /api/v1/approvals/               List submissions
POST   /api/v1/approvals/               Submit for approval
GET    /api/v1/approvals/{id}/          Get submission
POST   /api/v1/approvals/{id}/approve/  Approve
POST   /api/v1/approvals/{id}/reject/   Reject
```

## Database Schema (Key Models)

### Authentication & User Management
- **User** - Extended user model with roles

### Academic Structure
- **University** - University master
- **Faculty** - Faculty within university
- **Department** - Department within faculty
- **Program** - Study program
- **Course** - Individual courses

### People
- **StudentProfile** - Student information
- **Lecturer** - Lecturer information

### Academic Records
- **StudentEnrollment** - Course enrollments
- **Exam** - Exam definitions
- **Result** - Student results
- **Grade** - Grade assignments
- **GPARecord** - Semester GPA
- **CGPARecord** - Cumulative GPA

### Workflows
- **ResultSubmission** - Result submission
- **ApprovalStage** - Approval levels
- **ApprovalAction** - Individual approvals

### Support
- **Notification** - User notifications
- **ActivityLog** - Audit trail
- **LoginLog** - Login tracking

## User Roles & Permissions

| Role | Can View Results | Can Enter Results | Can Approve | Can Manage |
|------|-----------------|------------------|-------------|-----------|
| **Student** | Own ✓ | ✗ | ✗ | Profile |
| **Lecturer** | All ✓ | Course ✓ | ✗ | Courses |
| **HOD** | Dept ✓ | ✗ | Dept ✓ | Department |
| **Dean** | Faculty ✓ | ✗ | Faculty ✓ | Faculty |
| **Exam Officer** | All ✓ | All ✓ | ✗ | Exams |
| **Admin** | All ✓ | ✗ | All ✓ | System |

## Configuration

### Backend (.env)
```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_URL=sqlite:///db.sqlite3
# or for production:
# DATABASE_URL=postgresql://user:password@localhost/fastresult

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
CELERY_BROKER_URL=redis://localhost:6379/0
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### Frontend (.env.local)
```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_NAME=FastResult
```

## Development Workflow

### Backend Development
```bash
cd fastresult_backend

# Start server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Access admin panel
# http://localhost:8000/admin/

# Run tests
pytest

# Code quality
black .
flake8 .
isort .
```

### Frontend Development
```bash
cd fastresult_frontend

# Start dev server
npm run dev

# Build
npm run build

# Run tests
npm test

# Code quality
npm run lint
npm run format
```

## Deployment

### Production Backend
1. Change settings to `prod.py`
2. Set `DEBUG=False`
3. Configure secret key
4. Use PostgreSQL database
5. Configure static/media storage
6. Set up HTTPS
7. Configure email service
8. Deploy with Gunicorn/uWSGI

### Production Frontend
```bash
npm run build
# Deploy dist/ folder to CDN or web server
```

## Docker Deployment

### Build Images
```bash
docker build -t fastresult-backend ./fastresult_backend
docker build -t fastresult-frontend ./fastresult_frontend
```

### Run with Docker Compose
```bash
docker-compose up -d
```

### Access Services
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Database: localhost:5432
- Redis: localhost:6379

## Troubleshooting

### Backend Issues

**Migration errors**
```bash
python manage.py migrate --fake-initial
python manage.py migrate
```

**Database issues**
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

**CORS errors**
- Check `CORS_ALLOWED_ORIGINS` in settings
- Ensure frontend URL matches

### Frontend Issues

**API connection errors**
- Check `VITE_API_URL` environment variable
- Ensure backend is running on correct port
- Check browser console for errors

**Build errors**
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

## Performance Optimization

### Backend
- Enable query optimization with Django Debug Toolbar
- Use database indexing
- Cache frequently accessed data with Redis
- Use async tasks with Celery

### Frontend
- Code splitting with React lazy loading
- Image optimization
- CSS minification
- Bundle analysis

## Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Set DEBUG=False
- [ ] Configure HTTPS
- [ ] Use strong database passwords
- [ ] Configure CORS properly
- [ ] Enable CSRF protection
- [ ] Validate all inputs
- [ ] Use environment variables for secrets
- [ ] Keep dependencies updated
- [ ] Enable security headers

## Support & Documentation

- API Documentation: http://localhost:8000/api/docs/
- Django: https://docs.djangoproject.com/
- React: https://react.dev/
- React Router: https://reactrouter.com/

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

**FastResult v1.0.0** - Complete Student Result Management System
