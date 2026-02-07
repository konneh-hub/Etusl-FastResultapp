# FastResult Backend - Setup Guide

## Installation

### Prerequisites
- Python 3.9+
- pip
- SQLite (comes with Python)

### Setup Instructions

1. **Clone and Navigate**
```bash
cd fastresult_backend
```

2. **Create Virtual Environment**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements/dev.txt
```

4. **Create .env File**
```bash
cp .env.example .env
```

5. **Apply Migrations**
```bash
python manage.py migrate
```

6. **Create Superuser**
```bash
python manage.py createsuperuser
```

7. **Run Development Server**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`
API Documentation: `http://localhost:8000/api/docs/`
Admin Panel: `http://localhost:8000/admin/`

## Database

SQLite database file: `db.sqlite3`

## Key Apps

- **accounts**: User authentication and management
- **universities**: University and campus management
- **academics**: Faculty, department, program, and course structure
- **students**: Student profiles and enrollment
- **lecturers**: Lecturer management
- **exams**: Exam scheduling and management
- **results**: Result entry and GPA calculation
- **approvals**: Multi-level approval workflows
- **notifications**: User notifications and announcements
- **reports**: Analytics and reporting
- **audit**: Activity tracking and logging

## API Endpoints Overview

### Authentication
- `POST /api/v1/auth/register/` - Register new user
- `POST /api/v1/auth/login/` - Login user
- `POST /api/v1/auth/users/logout/` - Logout user
- `GET /api/v1/auth/users/me/` - Get current user

### Universities
- `GET /api/v1/universities/` - List universities
- `GET /api/v1/universities/academic-years/` - Academic years
- `GET /api/v1/universities/semesters/` - Semesters

### Results
- `GET /api/v1/results/` - List results
- `POST /api/v1/results/` - Create result
- `PUT /api/v1/results/{id}/` - Update result

## Environment Variables

Create a `.env` file in the backend directory:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration (optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Redis (for caching/celery)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Development Tools

- **Django Admin**: http://localhost:8000/admin/
- **API Docs (Swagger)**: http://localhost:8000/api/docs/
- **API Docs (ReDoc)**: http://localhost:8000/api/redoc/

## Running Tests

```bash
pytest
```

## Code Quality

```bash
# Format code
black .

# Check linting
flake8 .

# Sort imports
isort .
```
