# SRMS Architecture Consolidation Plan

## Backend Structure Consolidation

### KEEP (Core Responsibility Apps)
✅ `accounts/` → User model, roles, permissions (keep as-is)
✅ `universities/` → University, academic year, semester data (keep as-is)
✅ `academics/` → Faculty, department, program, course (keep as-is)
✅ `students/` → Student profile, enrollments (keep as-is)
✅ `lecturers/` → Lecturer profile, qualifications (keep as-is)
✅ `results/` → Result entry and storage (keep as-is)
✅ `audit/` → Audit logging (keep as-is)
✅ `notifications/` → User notifications (keep as-is)
✅ `reports/` → Analytics and reporting (keep as-is)
✅ `systemadmin/` → Platform administration (keep as-is)

### RENAME
🔄 `approvals/` → `result_workflow/` (approval workflow only, no result models)

### REMOVE / NOT CREATED
❌ `exams/` → Move exam models to `results/` or keep exam operations in `result_workflow/`
❌ `files/` → Consolidate into student documents in `students/`
❌ `core/` → Keep for constants, mixins, permissions (it's meta-infrastructure)

### NOT YET CREATED (Future)
⏳ `course_management/` → Merge with `academics/`
⏳ `enrollment/` → Merge with `students/`
⏳ `gpa_engine/` → Create as standalone (GPA math only)
⏳ `transcripts/` → Create as standalone (transcript generation)
⏳ `system_settings/` → Create as standalone (platform config)

**FINAL BACKEND APPS (Using what exists):**
```
platform → systemadmin/ (platform admin)
accounts/ (user, roles, permissions)
universities/ (university registry)
academics/ (academic structure: faculty, department, program, course)
students/ (enrollments, profiles, documents)
lecturers/ (lecturer profiles, qualifications)
results/ (result entry & storage — includes exam logic)
result_workflow/ (approvals only — rename from approvals/)
audit/ (audit logging)
notifications/ (notifications)
reports/ (analytics)
core/ (constants, mixins, permissions)
```

---

## Frontend Structure Consolidation

### KEEP (Official Structure)
✅ `src/layouts/` → Layout components (DashboardLayout, Sidebar, Header)
✅ `src/routes/` → Route definitions
✅ `src/services/` → API service layer
✅ `src/components/` → Reusable UI (Table, Form, Button, etc.)
✅ `src/hooks/` → State logic (useAuth, useTable, etc.)
✅ `src/store/` → Global state (Zustand/Redux)
✅ `src/utils/` → Helpers and validators
✅ `src/auth/` → Auth context (if exists) or merge into hooks

### DELETE
❌ `src/layout/` → Duplicate of layouts/ (I created this by mistake)
❌ `src/router/` → Duplicate of routes/ (I created this by mistake)
❌ `src/app/` → Unclear purpose (if it's main App component, move to src/App.jsx)
❌ `src/modules/` → Unclear purpose (possibly deprecated)

### CREATE (Official)
🆕 `src/dashboards/` → Role-specific dashboards
  - `systemAdmin/` → Platform administration pages
  - `universityAdmin/` → University admin CRUD pages
  - `dean/` → Dean read-only analytics
  - `hod/` → HOD department management
  - `examOfficer/` → Exam officer verification & scheduling
  - `lecturer/` → Lecturer result entry
  - `student/` → Student view-only pages

### MOVE MY PLACEHOLDERS
🔄 `src/pages/admin/` → `src/dashboards/universityAdmin/`
🔄 `src/pages/dean/` → `src/dashboards/dean/`
🔄 `src/pages/hod/` → `src/dashboards/hod/`
🔄 `src/pages/exam-officer/` → `src/dashboards/examOfficer/`
🔄 `src/pages/lecturer/` → `src/dashboards/lecturer/`
🔄 `src/pages/student/` → `src/dashboards/student/`

**FINAL FRONTEND STRUCTURE:**
```
src/
  api/           → axios clients
  auth/          → auth context + login form (if separate)
  layouts/       → DashboardLayout, Sidebar, Header
  components/    → Table, Form, Button, Badge, Spinner, ResultGrid, Chart
  hooks/         → useAuth, useTable, useNotifications, useForm
  services/      → API service layer (auth, admin, dean, hod, etc.)
  dashboards/    → Role dashboards
    systemAdmin/
    universityAdmin/
    dean/
    hod/
    examOfficer/
    lecturer/
    student/
  pages/         → (keep for non-dashboard pages like login, forgot-password, 404)
  routes/        → route definitions
  store/         → state management
  utils/         → validators, helpers
```

---

## Action Plan

### Backend
1. Rename `approvals/` → `result_workflow/` (or keep approvals and add result_workflow as symlink if needed)
2. Document that exam services are in `exams/` temporarily (can consolidate later)

### Frontend
1. Delete `src/layout/` (duplicate)
2. Delete `src/router/` (if it exists separately from routes/)
3. Delete `src/app/` folder if it's just metadata
4. Delete `src/modules/` if unclear
5. Create `src/dashboards/` folder structure
6. Move placeholder pages I created from `src/pages/{role}/` → `src/dashboards/{role}/`
7. Update router imports
8. Update ProtectedRoute to use dashboards

### Verification Post-Consolidation
- [ ] No duplicate folders (layout vs layouts, router vs routes)
- [ ] No synonym app names (results vs grades, workflow vs approvalFlow)
- [ ] Each responsibility in ONE app only
- [ ] All role dashboards under `src/dashboards/`
- [ ] All API calls in `src/services/` only
- [ ] No cross-responsibility leaks

