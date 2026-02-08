# Quick Reference: Immediate Action Items

## ⚡ Run These Commands NOW (in terminal at project root)

```bash
# From C:\SRMS\fastresult_frontend

# DELETE duplicate folders I created:
rm -r src/layout
rm -r src/routes
rm -r src/pages/admin
rm -r src/pages/dean
rm -r src/pages/hod
rm -r src/pages/exam-officer
rm -r src/pages/lecturer
rm -r src/pages/student

# Keep src/pages for: Login, NotFound, AccessDenied, ForgotPassword

# Verify cleanup:
ls src/  # Should NOT show layout, routes, or role-specific pages
```

---

## 📋 Files to Check/Update

### 1. Verify `src/router/index.jsx` imports from `modules/`
```javascript
// ❌ WRONG (my old code):
import AdminDashboard from '../pages/admin/Dashboard'

// ✅ CORRECT (should be):
import AdminDashboard from '../modules/admin/dashboard'
```

### 2. Verify `src/app/App.jsx` has AuthProvider
```javascript
// Should have this:
import { AuthProvider } from '../hooks/useAuth'

// And wrap Router:
<AuthProvider>
  <BrowserRouter>
    <Router />
  </BrowserRouter>
</AuthProvider>
```

### 3. Check that `src/layouts/` has these files:
- `DashboardLayout.jsx`
- `Sidebar.jsx`
- `Header.jsx`

If not, use my versions from `src/layout/` (before deleting that folder)

---

## 🎯 Next Priority Tasks

### TASK 1: Complete Service Layer (4 files, 30 min)
📁 **Location**: `src/services/`

Create these files following this template:

```javascript
// src/services/{role}.service.js
import apiClient from './apiClient'

export default {
  // Each service file has 3-5 API-calling methods
  // Example for dean.service.js:
  getFacultyOverview() {
    return apiClient.get('/dean/faculty/overview/')
  },
  getDepartments() {
    return apiClient.get('/dean/departments/')
  },
  getPerformanceReport(semesterId) {
    return apiClient.get(`/dean/performance/?semester=${semesterId}`)
  }
}
```

**Files to create:**
1. `dean.service.js` - 3 methods
2. `hod.service.js` - 4 methods
3. `examOfficer.service.js` - 5 methods
4. `lecturer.service.js` - 6 methods
5. `student.service.js` - 5 methods

---

### TASK 2: Wire Services to Dashboards (1 hour)
📁 **Location**: `src/modules/{role}/dashboard/`

Example transformation:

**BEFORE** (hardcoded data):
```javascript
const fetchDashboardData = async () => {
  setStats({ faculties: 3, departments: 15, staff: 200 })
}
```

**AFTER** (using service):
```javascript
import deanService from '../../../services/dean.service'

const fetchDashboardData = async () => {
  try {
    const data = await deanService.getFacultyOverview()
    setStats(data)
  } catch(error) {
    console.error('Error fetching faculty overview:', error)
    // Show error toast/notification
  }
}
```

**Apply to:**
- `src/modules/admin/dashboard/index.jsx` (use admin.service)
- `src/modules/dean/dashboard/DeanDashboard.jsx` (use dean.service)
- `src/modules/hod/dashboard/index.jsx` (use hod.service)
- `src/modules/examOfficer/dashboard/index.jsx` (use examOfficer.service)
- `src/modules/lecturer/dashboard/LecturerDashboard.jsx` (use lecturer.service)
- `src/modules/student/dashboard/StudentDashboard.jsx` (use student.service)

---

### TASK 3: Build ResultGrid Component (2 hours)
📁 **Location**: `src/components/ResultGrid/ResultGrid.jsx`

Transform the placeholder into a working spreadsheet:

```javascript
// Features needed:
✓ Display course enrollment data in table format
✓ Inline editing for mark inputs
✓ Auto-calculate total score (CA weight + exam weight)
✓ Copy/paste support from Excel
✓ Validation (marks ≤ total_marks)
✓ Draft save button
✓ Submit button → calls lecturer.service
✓ Bulk select rows
✓ Status badges (draft, submitted, approved)
```

---

## 🔄 Workflow

```
1. ✅ CLEANUP (this session) → Delete duplicate folders
2. ⏳ VERIFY (you) → Check router imports from modules/
3. ⏳ SERVICES (you) → Create 5 service files
4. ⏳ WIRE (you) → Connect services to dashboard pages
5. ⏳ GRID (you) → Build ResultGrid spreadsheet
6. ⏳ TEST → Login with test accounts, verify role access
7. ⏳ CRUD → Add user management, faculty CRUD, etc.
8. ⏳ DEPLOY → Build for production
```

---

## 📞 Reference Docs

| Purpose | File |
|---------|------|
| Full Architecture | `FINAL_ARCHITECTURE_SUMMARY.md` |
| Backend mapping | `fastresult_backend/ARCHITECTURE_CONSOLIDATION.md` |
| Frontend mapping | `fastresult_frontend/FRONTEND_CONSOLIDATION_FINAL.md` |
| Dashboard design rules | `fastresult_frontend/DASHBOARD_DESIGN.md` |
| Folder tree canonical | `fastresult_frontend/src/structure.txt` |

---

## ✅ Preq Checklist Before Starting

- [ ] Cleanup: deleted duplicate folders
- [ ] Verified: router imports from modules/
- [ ] Verified: App.jsx has AuthProvider
- [ ] Verified: src/layouts/ has DashboardLayout, Sidebar, Header
- [ ] Backend: running at http://localhost:8000/api/v1
- [ ] Frontend: running at http://localhost:5173 (npm run dev)

---

**NEXT ACTION**: Run the cleanup commands above, then ping me for service layer scaffolding ✨

