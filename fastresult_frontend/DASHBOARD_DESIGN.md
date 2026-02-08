SRMS Frontend Dashboard Design (React + Vite)

Purpose
- Provide role-specific dashboards (University Admin, Dean, HOD, Exam Officer, Lecturer, Student)
- Keep shared layout, API service layer, and auth centralized
- Avoid duplicating existing pages; update existing pages where present

High-level Requirements
- Role-based menus and route protection
- Thin pages that call service layer; no direct API calls in components
- Reusable components: Table, Form, Modal, Button, Badge, Spinner, Chart placeholder
- Spreadsheet-style result-entry component for Lecturer
- Standard pagination, error handling, and loading states

Files created/updated by this design
- [fastresult_frontend/DASHBOARD_DESIGN.md](fastresult_frontend/DASHBOARD_DESIGN.md) (this file)
- [fastresult_frontend/src/structure.txt](src/structure.txt)

Folder conventions
- `src/` is the app root
- `src/pages/{role}/` holds pages for each role (admin, dean, hod, exam-officer, lecturer, student)
- `src/components/` shared UI components
- `src/layout/` layout system (DashboardLayout, Sidebar, Header)
- `src/services/` API service layer (axios client, per-module services)
- `src/hooks/` reusable hooks (useAuth, useTable, useNotifications)
- `src/routes/` route definitions and ProtectedRoute
- `src/styles/` global styles and theme

Routing & Nested Routes
- Use nested routes under role base path, e.g. `/admin/*`, `/dean/*`, `/hod/*`, `/exam/*`, `/lecturer/*`, `/student/*`
- Sidebar menu rendered by `role` and `permissions`
- ProtectedRoute enforces both authentication and role membership

Role pages (high-level)
- University Admin (CRUD + controls): KPI dashboard, User management, Approval queue, Faculty/Department/Program/Course/Subject/Academic Year/Semester/Grading/Credit rules, Result control (lock/release), Reports, GPA analytics, Graduation eligibility, Notifications, Announcements, Admin profile
- Dean (read-only analytics): Faculty overview, Departments list, Faculty statistics, Performance reports, Department comparisons, Approval tracking viewer, Announcements, Notifications, Profile
- HOD (dept management): Department overview, Lecturer/course assignment, Students list, Courses list, Lecturer list, Results review, Approve/return results, Lecturer performance, Course outcomes, Message lecturers, Notifications, Profile
- Exam Officer: Verification queue, Approve/reject, Bulk approval, Exam scheduling/calendar/timetable builder, Room/invigilator assignment, Read-only student/course lists, Reports, Pass/fail charts, Announcements, Notifications, Profile
- Lecturer: My courses, Course details, Enrolled students, Enter/edit draft results (spreadsheet), Submit results, Submission status, Course performance, Grade distribution, Qualification upload, Profile, Notifications
- Student: Dashboard summary, GPA cards, Semester results, Full transcript, GPA breakdown, Course history/current courses, Profile editor, Document upload, Notifications, Announcements, Download buttons

UI Patterns
- Tables: `Table` component with columns config, optional action column and bulk-selection support
- Forms: `Form` primitives + formik/react-hook-form adapters; forms live in `src/pages/.../forms` for CRUD
- Charts: Placeholder `Chart` components using chart library (to be added later), data props only
- Spreadsheet result entry: `ResultGrid` component with inline validation, copy/paste support, draft save and submit actions

Accessibility & UX
- Keyboard navigation for result-entry grid
- Confirm dialogs for destructive actions (lock/unlock, bulk approvals)
- Clear success/error toasts

Integration rules
- Do not add platform-level features (platform templates, platform settings)
- University Admin pages must be scoped to the current university only
- Respect existing pages; if a page exists, update that page's folder instead of creating duplicates

API service conventions (brief)
- `src/services/apiClient.ts` → axios client + auth interceptor
- `src/services/{module}.service.ts` → export functions that call apiClient
- Components call service functions only

Testing and Stories
- Each major component should have a Storybook story (optional)
- Unit tests for hooks and services

Deployment notes
- Built with Vite; keep fast builds and code-splitting by route

-- End of design --
