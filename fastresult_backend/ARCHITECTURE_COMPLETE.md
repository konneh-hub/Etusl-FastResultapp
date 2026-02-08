# SRMS - Complete Django Project Structure & Architecture

**Project Scope**: Multi-university Student Result Management System  
**Architecture**: Modular Django + DRF with Service Layer Pattern  
**Status**: Architecture & Design (Structure Only - No Implementation Code)

---

## I. PROJECT FOLDER STRUCTURE

```
fastresult_backend/
├── manage.py
├── pytest.ini
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── backend/                          # Project settings
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                   # Shared settings
│   │   ├── dev.py                    # Development overrides
│   │   ├── prod.py                   # Production overrides
│   │   └── test.py                   # Test overrides
│   ├── urls.py                       # Root URL router
│   ├── wsgi.py
│   └── asgi.py
│
├── core/                             # Shared utilities
│   ├── __init__.py
│   ├── constants.py                  # App-wide constants
│   ├── utils/
│   ├── validators/
│   ├── exceptions.py                 # Custom exceptions
│   ├── mixins/                       # Reusable mixins
│   ├── pagination/
│   └── permissions/
│
├── apps/
│   ├── platform_accounts/            # [APP 1]
│   ├── platform_roles/               # [APP 2]
│   ├── university_registry/          # [APP 3]
│   ├── university_users/             # [APP 4]
│   ├── academic_structure/           # [APP 5]
│   ├── course_management/            # [APP 6]
│   ├── enrollment/                   # [APP 7]
│   ├── results/                      # [APP 8]
│   ├── result_workflow/              # [APP 9]
│   ├── gpa_engine/                   # [APP 10]
│   ├── transcripts/                  # [APP 11]
│   ├── reports/                      # [APP 12]
│   ├── audit_logs/                   # [APP 13]
│   ├── notifications/                # [APP 14]
│   └── system_settings/              # [APP 15]
│
├── tests/                            # Test suite
│   ├── conftest.py
│   ├── factories/
│   ├── fixtures/
│   └── [tests by app]
│
└── docs/
    ├── API_DESIGN.md
    ├── ARCHITECTURE.md
    ├── DATA_MODELS.md
    └── PERMISSIONS.md
```

---

## II. DJANGO APPS - RESPONSIBILITIES & STRUCTURE

### **APP 1: platform_accounts**
**Purpose**: Platform-level authentication and session management  
**Scope**: Works across all universities  
**Does NOT**: User role assignment (see platform_roles)

```
platform_accounts/
├── models.py
│   └── PlatformUser (email, password, is_active, created_at)
├── serializers.py
│   └── LoginSerializer, ChangePasswordSerializer
├── views.py
│   └── LoginViewSet, LogoutViewSet, ProfileViewSet
├── services/
│   └── AuthenticationService
├── tokens/
│   ├── __init__.py
│   └── jwt_handler.py
├── middleware/
│   └── AuthenticationMiddleware
├── urls.py
└── tests/
    └── test_auth.py
```

**Responsibilities**:
- User login/logout
- Password management
- Session/token issuance
- Basic authentication

---

### **APP 2: platform_roles**
**Purpose**: Role definitions and permission templates  
**Scope**: Platform-level role configuration  

```
platform_roles/
├── models.py
│   ├── Role (name, unique, description)
│   ├── Permission (code, name, description)
│   └── RolePermissionMapping (role FK, permission FK)
├── serializers.py
│   ├── RoleSerializer
│   ├── PermissionSerializer
│   └── RolePermissionSerializer
├── views.py
│   └── RoleViewSet (list only - no create/edit for production)
├── services/
│   └── RoleService
│       ├── get_role_permissions(role_id)
│       ├── check_permission(role, permission_code)
│       └── list_roles_with_permissions()
├── constants.py
│   └── ROLE_CHOICES = ['student', 'lecturer', 'hod', 'dean', 'exam_officer', 'university_admin']
│   └── PERMISSION_CODES = ['view_results', 'enter_results', 'approve_results', ...]
└── tests/
    └── test_roles.py
```

**Responsibilities**:
- Define platform roles
- Define permissions per role
- Assign permissions to roles (immutable after setup)

---

### **APP 3: university_registry**
**Purpose**: University master data and configuration  
**Scope**: Multi-university management  

```
university_registry/
├── models.py
│   ├── University (name, code, country, timezone, logo, email, phone)
│   ├── Campus (university FK, name, location, is_main)
│   ├── UniversitySettings (university 1-to-1, config settings)
│   └── UniversityAcademicConfig (university 1-to-1, academic rules)
├── serializers.py
│   ├── UniversitySerializer
│   ├── CampusSerializer
│   └── UniversitySettingsSerializer
├── views.py
│   └── UniversityViewSet (university_admin only)
├── services/
│   └── UniversityService
│       ├── create_university()
│       ├── get_university_config()
│       └── update_settings()
├── admin.py
│   └── UniversityAdmin, CampusAdmin
└── tests/
    └── test_university.py
```

**Responsibilities**:
- Register universities
- University configuration
- Campus management
- Academic settings per university

---

### **APP 4: university_users**
**Purpose**: User roles within a specific university  
**Scope**: University-scoped user assignment  

```
university_users/
├── models.py
│   ├── UniversityUser (platform_user FK, university FK, role FK, is_active)
│   ├── UserRoleAssignment (user FK, role FK, assigned_at, assigned_by)
│   └── UserDepartmentAssignment (user FK, department FK - optional for HOD)
├── serializers.py
│   ├── UniversityUserSerializer
│   ├── UserRoleAssignmentSerializer
│   └── UserDepartmentAssignmentSerializer
├── views.py
│   └── UniversityUserViewSet (university_admin only)
├── services/
│   ├── UserOnboardingService
│   │   ├── create_user(email, role, university)
│   │   ├── assign_role(user, role, university)
│   │   └── suspend_user(user)
│   └── UserPermissionService
│       ├── get_user_permissions(user, university)
│       ├── check_role(user, role, university)
│       └── get_university_users(university, role_filter)
├── admin.py
│   └── UniversityUserAdmin
├── urls.py
└── tests/
    └── test_university_users.py
```

**Responsibilities**:
- Assign platform roles to universities
- Department assignments (HOD links)
- User activation/suspension
- Permission inheritance from role

---

### **APP 5: academic_structure**
**Purpose**: University academic hierarchy - Faculties, Departments, Programs  
**Scope**: University Admin only  
**Does NOT**: Create courses (see course_management)

```
academic_structure/
├── models.py
│   ├── Faculty (university FK, name, code, head FK, created_at)
│   ├── Department (faculty FK, name, code, head FK, created_at)
│   ├── Program (department FK, name, code, level, duration_years, created_at)
│   ├── AcademicYear (university FK, year, start_date, end_date, is_active)
│   ├── Semester (academic_year FK, number, start_date, end_date, is_active)
│   └── CreditUnitRule (university 1-to-1, min_per_semester, max_per_semester, min_gpa)
├── serializers.py
│   ├── FacultySerializer
│   ├── DepartmentSerializer
│   ├── ProgramSerializer
│   ├── AcademicYearSerializer
│   ├── SemesterSerializer
│   └── CreditUnitRuleSerializer
├── views.py
│   ├── FacultyViewSet
│   ├── DepartmentViewSet
│   ├── ProgramViewSet
│   ├── AcademicYearViewSet
│   ├── SemesterViewSet
│   └── CreditUnitRuleViewSet
├── services/
│   ├── AcademicStructureService
│   │   ├── create_faculty()
│   │   ├── create_department()
│   │   ├── create_program()
│   │   ├── activate_academic_year()
│   │   └── activate_semester()
│   └── StructureValidationService
│       ├── validate_hierarchy()
│       └── check_no_duplicate_codes()
├── admin.py
└── tests/
    └── test_academic_structure.py
```

**Constraints**:
- Faculty.code unique per university
- Department.code unique per faculty
- Program.code unique per department
- One active academic year per university
- One active semester per academic year

---

### **APP 6: course_management**
**Purpose**: Course definitions and lecturer assignments  
**Scope**: Created by University Admin, assigned by HOD  
**Does NOT**: Manage student enrollments (see enrollment)

```
course_management/
├── models.py
│   ├── Course (program FK, name, code, credit_units, description, created_by)
│   ├── Subject (course FK, name, code - optional)
│   ├── CourseLecturer (course FK, lecturer FK, semester FK, assigned_by)
│   ├── CourseClass (course FK, semester FK, class_code, max_capacity)
│   └── GradingScale (university FK, grade_letter, min_score, max_score, grade_point)
├── serializers.py
│   ├── CourseSerializer
│   ├── SubjectSerializer
│   ├── CourseLecturerSerializer
│   ├── CourseClassSerializer
│   └── GradingScaleSerializer
├── views.py
│   ├── CourseViewSet (university_admin create, lecturer read)
│   ├── CourseLecturerViewSet (hod assign, lecturer read)
│   ├── GradingScaleViewSet (university_admin only)
│   └── CourseClassViewSet
├── services/
│   ├── CourseManagementService
│   │   ├── create_course()
│   │   ├── assign_lecturer()
│   │   ├── create_course_class()
│   │   └── get_lecturer_courses(lecturer, semester)
│   └── GradingService
│       ├── get_grading_scale(university, score)
│       └── calculate_grade_point(score, university)
├── admin.py
└── tests/
    └── test_courses.py
```

**Responsibilities**:
- Course registration
- Lecturer assignment to courses
- Course class creation
- Grading scale management

---

### **APP 7: enrollment**
**Purpose**: Student course enrollment and linking  
**Scope**: Created by University Admin or HOD, viewed by all roles  
**Does NOT**: Track results (see results)

```
enrollment/
├── models.py
│   ├── StudentProfile (user 1-to-1, matric_number unique, program FK, enrollment_year)
│   ├── StudentSemesterEnrollment (student FK, semester FK, status, enrollment_date)
│   ├── StudentEnrolledCourse (student_semester_enrollment FK, course FK, grade_mark)
│   └── CourseDropout (student_enrolled_course FK, dropped_date, reason)
├── serializers.py
│   ├── StudentProfileSerializer
│   ├── StudentSemesterEnrollmentSerializer
│   ├── StudentEnrolledCourseSerializer
│   └── CourseDropoutSerializer
├── views.py
│   ├── StudentProfileViewSet (university_admin, lecturer read)
│   ├── StudentEnrollmentViewSet
│   └── StudentEnrolledCourseViewSet
├── services/
│   ├── EnrollmentService
│   │   ├── enroll_student(student, semester)
│   │   ├── enroll_student_in_course(student, course)
│   │   ├── drop_course(student_course, reason)
│   │   └── get_student_courses(student, semester)
│   └── EnrollmentValidationService
│       ├── check_credit_limits()
│       ├── check_prerequisite()
│       └── check_duplicate_enrollment()
├── admin.py
└── tests/
    └── test_enrollment.py
```

**Constraints**:
- Student matric_number unique per university
- Can't enroll twice in same course per semester
- Must respect credit unit limits per semester

---

### **APP 8: results**
**Purpose**: Result storage and scores  
**Scope**: Lecturer enters, HOD reviews, Exam Officer approves  
**Does NOT**: Manage workflow (see result_workflow)

```
results/
├── models.py
│   ├── AssessmentComponent (course FK, component_type: CA/Exam/Practical, weight, total_marks)
│   ├── ResultRecord (enrolled_course FK, lecturer FK, status, created_at, updated_at)
│   ├── ResultComponentScore (result_record FK, component FK, score_obtained, lecturer_comments)
│   ├── ResultVersion (result_record FK, version_number, snapshot_data, changed_by, changed_at)
│   └── ResultStatus (draft, submitted, under_review, approved, rejected, released)
├── serializers.py
│   ├── AssessmentComponentSerializer
│   ├── ResultRecordSerializer
│   ├── ResultComponentScoreSerializer
│   └── ResultVersionSerializer
├── views.py
│   ├── AssessmentComponentViewSet (lecturer read, hod/admin create)
│   ├── ResultRecordViewSet
│   ├── ResultComponentScoreViewSet
│   └── ResultHistoryViewSet (read-only)
├── services/
│   ├── ResultEntryService
│   │   ├── create_result_record()
│   │   ├── add_component_score()
│   │   ├── update_component_score()
│   │   ├── calculate_total_score()
│   │   └── create_version_snapshot()
│   └── ResultCalculationService
│       ├── calculate_weighted_score()
│       └── determine_grade()
├── admin.py
└── tests/
    └── test_results.py
```

**Constraints**:
- ResultComponentScore can only be added/edited if status='draft'
- Version created on every status change
- Total score = Σ(component_score × component_weight)

---

### **APP 9: result_workflow**
**Purpose**: Multi-stage approval workflow  
**Scope**: Orchestrates result movement through stages  

```
result_workflow/
├── models.py
│   ├── WorkflowDefinition (university FK, name: "Standard Lecturer→HOD→Exam Officer→Admin")
│   ├── WorkflowStage (workflow FK, stage_sequence: 1-4, role_required, stage_name)
│   ├── ResultApprovalInstance (result_record FK, workflow_definition FK, current_stage)
│   ├── ApprovalActionLog (approval_instance FK, stage FK, actor, action: approve/reject/return, timestamp)
│   └── CorrectionRequest (result_record FK, requested_by, reason, created_at)
├── serializers.py
│   ├── WorkflowDefinitionSerializer
│   ├── WorkflowStageSerializer
│   ├── ResultApprovalInstanceSerializer
│   └── ApprovalActionLogSerializer
├── views.py
│   ├── WorkflowDefinitionViewSet (read-only)
│   ├── ResultApprovalInstanceViewSet (state machine operations)
│   └── ApprovalActionLogViewSet (audit read-only)
├── services/
│   ├── ApprovalWorkflowService
│   │   ├── get_pending_approvals(user, role)
│   │   ├── submit_to_next_stage()
│   │   ├── approve_at_stage()
│   │   ├── reject_at_stage(reason)
│   │   ├── request_correction(reason)
│   │   └── can_user_approve_at_stage(user, approval_instance)
│   └── WorkflowStateService
│       ├── get_current_stage()
│       ├── get_next_stage()
│       ├── check_can_skip_stage()
│       └── log_action()
├── admin.py
└── tests/
    └── test_workflow.py
```

**Workflow Sequence (Immutable)**:
```
Stage 1: draft (Lecturer entry)
    ↓ [Lecturer Submit]
Stage 2: submitted (Awaiting HOD review)
    ↓ [HOD Approve]
Stage 3: under_review (Exam Officer verification)
    ↓ [Exam Officer Approve]
Stage 4: approved (Ready for release)
    ↓ [University Admin Release]
Stage 5: released (Published to students)
```

**Rejections/Corrections**:
- At any stage, can reject → back to Stage 1 (draft)
- Reason logged in CorrectionRequest

---

### **APP 10: gpa_engine**
**Purpose**: GPA and CGPA calculation  
**Scope**: Works for all students, all semesters  

```
gpa_engine/
├── models.py
│   ├── SemesterGPA (student FK, semester FK, total_gpa, credits_earned, failed_credits)
│   ├── CumulativeGPA (student FK, cgpa, total_credits_earned, last_updated)
│   └── GPACalculationLog (student FK, semester FK, calculation_date, result_count)
├── serializers.py
│   ├── SemesterGPASerializer
│   └── CumulativeGPASerializer
├── views.py
│   ├── SemesterGPAViewSet (student read own, admin read all)
│   └── CumulativeGPAViewSet
├── services/
│   ├── GPACalculationService
│   │   ├── calculate_semester_gpa(student, semester)
│   │   │   ├── Get all released results for semester
│   │   │   ├── Filter withdrawn courses
│   │   │   ├── Σ(credit_units × grade_point) / Σ(credit_units)
│   │   │   └── Save SemesterGPA
│   │   ├── calculate_cgpa(student)
│   │   │   ├── Get all SemesterGPA records
│   │   │   ├── Σ(credit_units × gpa) / Σ(credit_units)
│   │   │   └── Update CumulativeGPA
│   │   ├── recalculate_all_gpa(university, semester)
│   │   └── get_failed_credits(student, up_to_semester)
│   └── GradeHandlingService
│       ├── handle_repeated_course()
│       ├── handle_incomplete_grade()
│       └── handle_withdrawn_course()
├── admin.py
└── tests/
    └── test_gpa.py
```

**Calculation Rules**:
- GPA = Σ(credit_units × grade_point) / Σ(credit_units)
- Withdrawn courses excluded
- Repeated courses: use best grade
- Incomplete grades: placeholder 0.0 until finalized

---

### **APP 11: transcripts**
**Purpose**: Official transcript generation and versioning  
**Scope**: Generated from results + GPA engine  

```
transcripts/
├── models.py
│   ├── TranscriptTemplate (university FK, format_type: PDF/HTML, template_design)
│   ├── TranscriptRecord (student FK, generated_at, locked, version_number)
│   ├── TranscriptSnapshot (transcript_record FK, snapshot_data_json)
│   └── TranscriptAdjustment (transcript FK, adjustment_type, reason, made_by)
├── serializers.py
│   ├── TranscriptRecordSerializer
│   └── TranscriptSnapshotSerializer
├── views.py
│   ├── TranscriptViewSet (student read own, admin read all)
│   └── TranscriptGeneratorViewSet (admin trigger generation)
├── services/
│   ├── TranscriptGenerationService
│   │   ├── generate_transcript(student)
│   │   │   ├── Fetch all released results
│   │   │   ├── Fetch SemesterGPA + CGPA
│   │   │   ├── Calculate classification (1st/2nd/3rd/Pass)
│   │   │   ├── Build JSON snapshot
│   │   │   ├── Lock transcript
│   │   │   └── Return TranscriptRecord
│   │   ├── regenerate_transcript(transcript_record)
│   │   ├── lock_transcript(transcript)
│   │   └── get_transcript_classification(cgpa)
│   ├── TranscriptSnapshotService
│   │   ├── create_snapshot(transcript, data)
│   │   ├── get_snapshot_by_version()
│   │   └── immutable snapshot (no update)
│   └── TranscriptExportService
│       ├── export_as_pdf()
│       ├── export_as_html()
│       └── get_digital_signature()
├── admin.py
└── tests/
    └── test_transcripts.py
```

**Classification Rules** (Configurable per university):
- CGPA 3.5-4.0: First Class
- CGPA 3.0-3.49: Second Class Upper
- CGPA 2.0-2.99: Second Class Lower
- CGPA 1.0-1.99: Third Class
- CGPA <1.0: Fail (no graduation)

---

### **APP 12: reports**
**Purpose**: Analytics and reporting dashboards  
**Scope**: Class summary, department analytics, university-wide reports  

```
reports/
├── models.py
│   ├── ReportSchedule (report_type, frequency, owner, last_run)
│   └── ReportCache (report_type, data_json, generated_at, valid_until)
├── serializers.py
│   ├── ClassSummarySerializer
│   ├── DepartmentAnalyticsSerializer
│   └── UniversityReportSerializer
├── views.py
│   ├── ClassSummaryViewSet (lecturer, hod read)
│   ├── DepartmentAnalyticsViewSet (hod, dean read)
│   ├── UniversityAnalyticsViewSet (admin read)
│   └── ReportDownloadViewSet
├── services/
│   ├── ClassReportService
│   │   ├── get_class_summary(course, semester)
│   │   │   ├── Pass/fail counts
│   │   │   ├── Grade distribution
│   │   │   ├── Average score
│   │   │   └── Performance vs. university mean
│   │   └── get_student_performance_in_class(student, course)
│   ├── DepartmentReportService
│   │   ├── get_department_performance(department, semester)
│   │   ├── get_course_performance_ranking()
│   │   └── get_lecturer_performance()
│   ├── UniversityReportService
│   │   ├── get_university_statistics(semester)
│   │   ├── get_admission_analysis()
│   │   ├── get_graduation_rates()
│   │   └── get_equity_analysis()
│   └── ReportCacheService
│       ├── cache_report()
│       └── invalidate_cache()
├── admin.py
└── tests/
    └── test_reports.py
```

---

### **APP 13: audit_logs**
**Purpose**: Comprehensive audit trail for compliance  
**Scope**: Log all result changes, approvals, user actions  

```
audit_logs/
├── models.py
│   ├── AuditLog (
│   │     actor FK to User,
│   │     actor_role,
│   │     university FK,
│   │     action_type: create/update/delete/approve/reject/release,
│   │     target_model,
│   │     target_object_id,
│   │     before_values_json,
│   │     after_values_json,
│   │     timestamp,
│   │     ip_address,
│   │     user_agent
│   │   )
│   └── AuditLogArchive (monthly archive of old logs)
├── serializers.py
│   └── AuditLogSerializer (read-only)
├── views.py
│   └── AuditLogViewSet (admin read-only)
├── services/
│   ├── AuditLoggingService
│   │   ├── log_action(actor, action_type, target_model, target_id, before/after)
│   │   ├── log_result_entry()
│   │   ├── log_approval()
│   │   ├── log_user_created()
│   │   ├── log_role_changed()
│   │   └── log_result_released()
│   └── AuditQueryService
│       ├── get_logs_for_object()
│       ├── get_logs_by_actor()
│       ├── get_logs_by_action()
│       └── export_audit_report()
├── middleware/
│   └── AuditMiddleware (capture IP, user_agent)
├── admin.py
└── tests/
    └── test_audit.py
```

**Immutable**: Audit logs cannot be deleted (enforcement at model level)

---

### **APP 14: notifications**
**Purpose**: In-app and email notifications  
**Scope**: Result status changes, approvals, releases  

```
notifications/
├── models.py
│   ├── Notification (user FK, type: result_submitted/approved/released/returned, content, created_at, read_at)
│   ├── EmailTemplate (template_name, subject, body_html)
│   └── NotificationPreference (user FK, email_on_approval, email_on_release)
├── serializers.py
│   └── NotificationSerializer
├── views.py
│   └── NotificationViewSet (user read own only)
├── services/
│   ├── NotificationService
│   │   ├── notify_result_submitted()
│   │   ├── notify_result_approved()
│   │   ├── notify_result_returned(reason)
│   │   ├── notify_result_released()
│   │   └── notify_result_rejected(reason)
│   └── EmailService
│       ├── send_result_notification()
│       ├── send_bulk_notification()
│       └── use_celery_for_async()
├── admin.py
└── tests/
    └── test_notifications.py
```

---

### **APP 15: system_settings**
**Purpose**: Global system configuration  
**Scope**: Platform-level and university-level settings  

```
system_settings/
├── models.py
│   ├── PlatformSetting (setting_key, setting_value_json, updated_at)
│   ├── UniversitySetting (university FK, setting_key, setting_value_json)
│   └── FeatureFlag (feature_name, is_enabled, university FK optional)
├── serializers.py
│   ├── PlatformSettingSerializer
│   └── UniversitySettingSerializer
├── views.py
│   └── SystemSettingViewSet (admin only)
├── services/
│   ├── SystemSettingService
│   │   ├── get_platform_setting()
│   │   ├── set_platform_setting()
│   │   ├── get_university_setting()
│   │   └── set_university_setting()
│   └── FeatureFlagService
│       ├── is_feature_enabled()
│       └── toggle_feature()
├── admin.py
└── tests/
    └── test_settings.py
```

---

## III. DATABASE RELATIONSHIPS DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────┐
│                      PLATFORM LEVEL                                  │
├─────────────────────────────────────────────────────────────────────┤
│
│  PlatformUser (1) ──FK── UniversityUser (many)
│     │
│     ├── email, password, is_active
│     └── [Auth only - no role here]
│
│  Role (Many) ──M2M── Permission (Many)
│     │                   via RolePermissionMapping
│     └── Used only for role definition
│
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    UNIVERSITY LEVEL (Scoped)                         │
├─────────────────────────────────────────────────────────────────────┤
│
│  University (1) ──FK── [All other models]
│     │
│     ├── UniversityUser (many)
│     │       │
│     │       └── role: student/lecturer/hod/dean/exam_officer/admin
│     │
│     ├── Faculty (many)
│     │     │
│     │     └── Department (many)
│     │           │
│     │           ├── Program (many)
│     │           │     │
│     │           │     └── Course (many)
│     │           │           │
│     │           │           ├── Subject (many)
│     │           │           ├── CourseLecturer (semester-specific)
│     │           │           │
│     │           │           └── StudentEnrolledCourse (many)
│     │           │                   │
│     │           │                   └── ResultRecord (per semester)
│     │           │                         │
│     │           │                         ├── ResultComponentScore (many)
│     │           │                         ├── ResultVersion (history)
│     │           │                         └── ResultApprovalInstance
│     │           │                               └── ApprovalActionLog
│     │           │
│     │           └── (HOD = head of Department)
│     │
│     ├── AcademicYear (many)
│     │     └── Semester (many)
│     │           ├── StudentSemesterEnrollment (many)
│     │           ├── CourseLecturer.semester (FK)
│     │           └── SemesterGPA (per student per semester)
│     │
│     ├── GradingScale (many: A/B/C/D/F)
│     ├── CreditUnitRule (1 per university)
│     ├── UniversitySettings
│     └── CumulativeGPA (per student)
│
│  StudentProfile (per student)
│     │
│     ├── matric_number (unique per university)
│     ├── program FK
│     └── enrollment_year
│
│  Notification (user-specific)
│  AuditLog (university-scoped)
│  ReportCache (university-scoped)
│  WorkflowDefinition (per university)
│
└─────────────────────────────────────────────────────────────────────┘
```

---

## IV. DATA SCOPING RULES (CRITICAL)

Every query MUST filter by university to ensure multi-tenancy:

```python
# PATTERN: Scoped Query
Model.objects.filter(
    field1__field2__university_id=user.university_id
)

# Example queries:
Faculty.objects.filter(university_id=user.university_id)
Course.objects.filter(program__department__faculty__university_id=user.university_id)
Result.objects.filter(enrolled_course__course__program__department__faculty__university_id=user.university_id)
```

---

## V. MODULE INTERACTIONS

```
INPUT FLOW (Result Entry):
  platform_accounts (auth)
    ↓
  university_users (role check)
    ↓
  enrollment (get student courses)
    ↓
  course_management (get course details, grading scale)
    ↓
  results (enter scores via ResultEntryService)
    ↓
  result_workflow (submit through stages)

CALCULATION FLOW (After Release):
  result_workflow (release approval)
    ↓
  results (get all released results)
    ↓
  gpa_engine (calculate GPA/CGPA)
    ↓
  transcripts (generate transcript from GPA + results)
    ↓
  reports (update cached analytics)

NOTIFICATION FLOW (Status Changes):
  result_workflow (stage transition)
    ↓
  notifications (create notification)
    ↓
  EmailService (async send via notifications)

AUDIT FLOW (Every Write):
  [Any service] (perform action)
    ↓
  audit_logs.AuditLoggingService (log_action)
    ↓
  AuditLog (persistent record)
```

---

## VI. SERVICE LAYER ORGANIZATION

**Pattern**: Each app has a `services/` directory

```python
# Example: apps/results/services/__init__.py

from .result_entry import ResultEntryService
from .result_calculation import ResultCalculationService

__all__ = ['ResultEntryService', 'ResultCalculationService']

# Usage in views:
from apps.results.services import ResultEntryService
result = ResultEntryService.create_result_record(...)
```

---

## VII. API LAYER ORGANIZATION

**Pattern**: DRF ViewSets per model, permissions per role

```
apps/[app_name]/
├── views.py
│   ├── [Model]ViewSet (Django REST Framework)
│   │   ├── permission_classes = [BasePermission]
│   │   ├── queryset filtered by university
│   │   └── all operations via services
│   └── [Custom]ViewSet
│
└── urls.py
    └── router.register(viewset) → /api/v1/[model]/
```

---

## VIII. TESTING ORGANIZATION

```
tests/
├── conftest.py (pytest fixtures)
│   ├── university_factory
│   ├── user_factory (by role)
│   ├── result_factory
│   └── semester_factory
│
├── unit/
│   ├── test_services.py
│   ├── test_models.py
│   └── test_serializers.py
│
├── integration/
│   ├── test_workflow.py
│   ├── test_result_entry_to_gpa.py
│   └── test_cross_app.py
│
└── api/
    ├── test_result_entry_api.py
    ├── test_approval_api.py
    └── test_read_api.py
```

---

## IX. DEPLOYMENT CONSIDERATIONS

### **Settings Structure**
```
backend/settings/
├── base.py (shared)
├── dev.py (DEBUG=True, EMAIL_BACKEND='console')
├── prod.py (DEBUG=False, redis cache, email smtp)
└── test.py (in-memory db, disable migrations)
```

### **Environment Variables** (`.env` not in git)
```
DEBUG=False
DATABASE_URL=postgresql://user:pass@host:5432/srms
REDIS_URL=redis://localhost:6379
SECRET_KEY=...
ALLOWED_HOSTS=...
EMAIL_HOST_PASSWORD=...
```

### **Background Tasks**
```python
# apps/notifications/tasks.py
from celery import shared_task

@shared_task
def send_result_notification(result_id, user_id):
    # Async send email
    pass

# Triggered by:
# notification_service.notify_result_released(result)
#   → tasks.send_result_notification.delay(result_id, user_id)
```

---

## X. SUMMARY TABLE

| App # | App Name | Primary Role | Models | Key Service |
|-------|----------|--------------|--------|-------------|
| 1 | platform_accounts | Platform | PlatformUser | AuthenticationService |
| 2 | platform_roles | Platform | Role, Permission | RoleService |
| 3 | university_registry | Admin | University, Campus, UniversitySettings | UniversityService |
| 4 | university_users | Admin | UniversityUser, UserRoleAssignment | UserOnboardingService |
| 5 | academic_structure | Admin | Faculty, Department, Program, AcademicYear, Semester | AcademicStructureService |
| 6 | course_management | Admin/HOD | Course, Subject, CourseLecturer, GradingScale | CourseManagementService |
| 7 | enrollment | Admin | StudentProfile, StudentEnrolledCourse | EnrollmentService |
| 8 | results | Lecturer | ResultRecord, ResultComponentScore | ResultEntryService |
| 9 | result_workflow | Multi-role | ResultApprovalInstance, ApprovalActionLog | ApprovalWorkflowService |
| 10 | gpa_engine | System | SemesterGPA, CumulativeGPA | GPACalculationService |
| 11 | transcripts | Admin/Student | TranscriptRecord, TranscriptSnapshot | TranscriptGenerationService |
| 12 | reports | Multi-role | ReportCache | ClassReportService, DepartmentReportService |
| 13 | audit_logs | System | AuditLog | AuditLoggingService |
| 14 | notifications | System | Notification, EmailTemplate | NotificationService |
| 15 | system_settings | Admin | PlatformSetting, FeatureFlag | SystemSettingService |

---

**Status**: Architecture Complete  
**Next Steps**: Model design per app, then API layer, then frontend  
**Last Updated**: 2026-02-07
