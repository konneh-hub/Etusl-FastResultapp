# FastResult - Complete Student Result Management System

A comprehensive student result management system built with Django REST Framework and React.

## Overview

FastResult is a full-featured student result management system designed for universities with support for:

- **Multi-user roles** (Admin, Dean, HOD, Exam Officer, Lecturer, Student)
- **Academic structure management** (Universities, Faculties, Departments, Programs, Courses)
- **Result entry and management** with automatic GPA/CGPA calculation
- **Multi-level approval workflows** for results
- **Grade scaling and validation**
- **Transcript generation**
- **Comprehensive reporting and analytics**
- **Notification system**
- **Audit logging**

## System Architecture

### Backend (Django)
- REST API built with Django REST Framework
- SQLite database (SQLite for development, can be configured for PostgreSQL production)
- Role-based access control (RBAC)
- Token-based authentication
- Comprehensive logging and audit trails
- Multi-university support

### Frontend (React + Vite)
- Modern React with Functional components and Hooks
- Redux for state management
- Axios for API communication
- Role-based UI rendering
- Responsive design components

## Project Structure

### Backend
```
fastresult_backend/
├── manage.py
├── backend/              # Django project config
├── core/               # Shared utilities
├── accounts/           # User management
├── universities/       # University structure
├── academics/          # Faculty, Department, Programs
├── students/           # Student management
├── lecturers/          # Lecturer management
├── exams/             # Exam scheduling
├── results/           # Result management & GPA engine
├── approvals/         # Approval workflows
├── reports/           # Analytics & reports
├── notifications/     # Notification system
├── audit/             # Activity logging
└── requirements/      # Python dependencies
```

### Frontend
```
fastresult_frontend/
├── src/
│   ├── app/            # React app entry
│   ├── router/         # Route definitions
│   ├── layouts/        # Layout components
│   ├── services/       # API clients
│   ├── store/          # Redux store
│   ├── hooks/          # Custom hooks
│   ├── utils/          # Utilities
│   ├── components/     # UI components
│   ├── modules/        # Feature modules
│   ├── pages/          # Standalone pages
│   ├── assets/         # Static files
│   └── styles/         # Global styles
├── index.html
├── package.json
└── vite.config.js
```

## Quick Start

### Backend Setup
```bash
cd fastresult_backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements/dev.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Backend runs on: http://localhost:8000

### Frontend Setup
```bash
cd fastresult_frontend
npm install
npm run dev
```

Frontend runs on: http://localhost:5173

## Key Features

### User Management
- Role-based access control (6 roles)
- User registration and authentication
- Profile management
- Permission-based UI rendering

### Academic Management
- Multi-university support
- Faculty and department structure
- Program and course management
- Semester and academic year management

### Student Management
- Student profiles with matric numbers
- Course enrollment
- Academic status tracking
- Document management

### Result Management
- Result entry by lecturers
- Multi-component result scoring (CA, Exam, etc.)
- Automatic grade calculation
- GPA and CGPA calculation
- Result locking and release control

### Approval Workflow
- Configurable multi-level approval stages
- HOD, Dean, and Admin approvals
- Revision requests
- Complete approval history tracking

### GPA Calculation
- Weightage-based component calculation
- Semester GPA calculation
- Cumulative GPA tracking
- Minimum GPA thresholds

### Reporting
- Student transcripts
- Grade distribution reports
- Performance analytics
- Result submission status

### Notifications
- User notifications
- System announcements
- Broadcast messaging
- Email notifications (configured)

### Audit & Logging
- Activity logging
- Login tracking
- Result change history
- Approval workflow logs

## API Documentation

Available at: http://localhost:8000/api/docs/ (Swagger UI)

Or: http://localhost:8000/api/redoc/ (ReDoc)

## Database Schema

### Key Models
- **User**: Extended Django user with roles
- **University, Campus**: Multi-university support
- **Faculty, Department, Program, Course**: Academic structure
- **StudentProfile, StudentEnrollment**: Student data
- **Lecturer, LecturerQualification**: Lecturer data
- **Exam, ExamPeriod, ExamTimetable**: Exam management
- **Result, ResultComponent, Grade**: Result tracking
- **GPARecord, CGPARecord**: GPA calculations
- **ResultSubmission, ApprovalStage**: Approval workflow
- **Notification, Announcement**: Messaging
- **ActivityLog, LoginLog, ResultChangeLog**: Audit trails

## Authentication

- Token-based authentication
- JWT tokens stored in localStorage
- Automatic token refresh
- Session management
- CORS enabled for local development

## Role Permissions

| Entity | Admin | Dean | HOD | Exam Officer | Lecturer | Student |
|--------|-------|------|-----|--------------|----------|---------|
| View Results | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ (own) |
| Enter Results | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| Approve Results | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| Manage Users | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| View Reports | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ |
| Manage Academic | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ |

## Configuration Files

### Backend
- `backend/settings/base.py`: Base configuration
- `backend/settings/dev.py`: Development settings
- `backend/settings/prod.py`: Production settings
- `.env`: Environment variables

### Frontend
- `vite.config.js`: Vite configuration
- `.env.local`: Frontend environment variables
- `package.json`: Dependencies

## Development Commands

### Backend
```bash
# Migrations
python manage.py makemigrations
python manage.py migrate

# Admin
python manage.py createsuperuser

# Testing
pytest

# Code quality
black .
flake8 .
isort .
```

### Frontend
```bash
# Development
npm run dev

# Build
npm run build

# Code quality
npm run lint
npm run format
```

## Production Deployment

### Backend
1. Set DEBUG=False
2. Configure SECRET_KEY
3. Set ALLOWED_HOSTS
4. Use PostgreSQL instead of SQLite
5. Configure static/media files
6. Set up HTTPS
7. Configure email service

### Frontend
1. Run `npm run build`
2. Deploy `dist/` folder to CDN or web server
3. Configure environment variables
4. Set up HTTPS

## Technologies Used

### Backend
- Django 4.2
- Django REST Framework
- SQLite 3 (can use PostgreSQL)
- Python 3.9+
- Celery (for async tasks)
- Redis (for caching)

### Frontend
- React 18
- Redux Toolkit
- Axios
- React Router v6
- Tailwind CSS (recommended)
- Chart.js for analytics

## License

Licensed under MIT License

## Support

For issues and feature requests, please check the documentation or contact the development team.

---

**FastResult v1.0.0** - Student Result Management System
