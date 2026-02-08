# Frontend Refactoring Guide - Completion Pattern

## Overview
The frontend has been partially refactored from hardcoded data to API-driven architecture. This guide shows patterns to complete the remaining pages.

## Completed Refactorings ✅

### 1. API Infrastructure
- `src/services/apiClient.js` - Axios client with auth interceptor
- `src/services/userService.js` - User CRUD + getRoles
- `src/services/academicService.js` - Faculties, Departments, Programs  
- `src/services/courseService.js` - Course CRUD + enrolled students
- `src/services/resultService.js` - Result CRUD + student results
- `src/services/dashboardService.js` - Dashboard KPIs, stats, charts
- `src/hooks/useApi.js` - Reusable data-fetch hook with { data, loading, error, refresh }

### 2. Pages Fully Refactored
- **Profiles**: `student/profile`, `dean/profile`, `lecturer/profile`, `hod/profile`, `examOfficer/profile`, `universityAdmin/profile` - All fetch current user profile via useApi
- **Management**: `universityAdmin/user-management`, `universityAdmin/student-management`, `universityAdmin/lecturer-management` - All use CRUDTable + useApi + service pagination/CRUD
- **Courses**: `lecturer/my-courses`, `student/courses` - Fetch courses from courseService with role/student filtering
- **Results**: `student/semester-results` - Fetch via resultService.getStudentResults with semester filtering
- **Students**: `lecturer/enrolled-students` - Fetch enrolled students via courseService.getEnrolledStudents
- **Dashboard**: `dean/dashboard` - Fetch totals/stats/KPIs from dashboardService

### 3. Shared Components Updated
- **Form.jsx** - Added `serverErrors` prop to display backend validation errors
- **CRUDTable.jsx** - Supports pagination, loading/empty states, CRUD actions
- **useApi.js** - Standard pattern: `const { data, loading, error, refresh } = useApi(fetchFn, deps[])`

---

## Pattern for Remaining Pages

### Pattern 1: Simple List Page (Read-Only Table)

```jsx
import React, { useCallback } from 'react';
import Table from '../../../../components/Table/Table';
import useApi from '../../../../hooks/useApi';
import * as SERVICE from '../../../../services/SERVICE.js';
import { useAuth } from '../../../../hooks/useAuth';

export default function PageName() {
  const { user } = useAuth();
  
  // Decide which service method to call based on page type
  const fetchData = useCallback(
    () => SERVICE.getMethod({ 
      filters: { faculty: user?.faculty_id }  // Add role-based scoping
    }),
    [user?.faculty_id]
  );
  const { data: resp, loading, error } = useApi(fetchData, [user?.faculty_id]);
  
  const items = resp?.results || resp || [];
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error loading data</div>;
  
  return (
    <div>
      <h1>Page Title</h1>
      {items.length === 0 ? (
        <div>No items found</div>
      ) : (
        <Table data={items} columns={[/*fields*/]} />
      )}
    </div>
  );
}
```

### Pattern 2: CRUD Management Page (Add/Edit/Delete)

```jsx
import CRUDTable from '../../../../components/CRUDTable/CRUDTable';
import Form from '../../../../components/Form/Form';
import useApi from '../../../../hooks/useApi';
import * as SERVICE from '../../../../services/SERVICE.js';
import toast from 'react-hot-toast';

export default function ManagementPage() {
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [serverErrors, setServerErrors] = useState({});
  
  const fetchItems = useCallback(
    () => SERVICE.getItems({ page, pageSize: 20 }),
    [page]
  );
  const { data: resp, loading, refresh } = useApi(fetchItems, [page]);
  
  const handleSave = async (formData) => {
    try {
      if (editingItem?.id) {
        await SERVICE.updateItem(editingItem.id, formData);
      } else {
        await SERVICE.createItem(formData);
      }
      toast.success('Saved');
      setShowForm(false);
      await refresh();
    } catch (err) {
      setServerErrors(err.response?.data || {});
    }
  };
  
  const handleDelete = async (row) => {
    try {
      await SERVICE.deleteItem(row.id);
      toast.success('Deleted');
      await refresh();
    } catch (err) {
      toast.error('Failed to delete');
    }
  };
  
  return (
    <>
      {showForm && <Form {...} serverErrors={serverErrors} />}
      <CRUDTable 
        data={resp?.results || []}
        pagination={{ current: page, total: resp?.count, limit: 20 }}
        onEdit={row => { setEditingItem(row); setShowForm(true); }}
        onDelete={handleDelete}
      />
    </>
  );
}
```

### Pattern 3: Dashboard/KPI Page

```jsx
import useApi from '../../../hooks/useApi';
import * as dashboardService from '../../../services/dashboardService';

export default function RoleDashboard() {
  const scope = { role: 'dean', /* other scope */ };
  
  const fetchTotals = useCallback(() => dashboardService.getTotals(scope), [scope]);
  const fetchStats = useCallback(() => dashboardService.getStatistics(scope), [scope]);
  
  const { data: totals, loading } = useApi(fetchTotals, [scope]);
  const { data: stats } = useApi(fetchStats, [scope]);
  
  return (
    <div>
      {loading ? <div>Loading...</div> : (
        <>
          <StatsCard label="Total" value={totals?.count} />
          <StatsCard label="Pending" value={stats?.pending_count} />
        </>
      )}
    </div>
  );
}
```

---

## Remaining Pages to Refactor

### Communication Pages (18 remaining)
- `dean/communication/Communication.jsx`
- `examOfficer/announcements/Announcements.jsx`
- `hod/communication/Communication.jsx`
- `lecturer/qualification-upload/QualificationUpload.jsx`
- `student/document-upload/DocumentUpload.jsx`
- `universityAdmin/communication/Communication.jsx`
- And 12 more...

**Pattern**: Usually fetch a list + create new items. Use Pattern 1 or 2.

### Report Pages (8 remaining)
- `dean/reports/Reports.jsx`
- `examOfficer/reports/Reports.jsx`
- `hod/reports/Reports.jsx`
- `lecturer/reports/Reports.jsx`
- `universityAdmin/reports/Reports.jsx`
- And 3 more...

**Pattern**: Often dashboard-like. Fetch reports endpoint: `GET /reports/?filters={role, dateRange}`. Use Pattern 3 or 1.

### Oversight/Management Pages (7 remaining)
- `dean/faculty-oversight/FacultyOversight.jsx`
- `examOfficer/academic-lists/AcademicLists.jsx`
- `examOfficer/result-verification/ResultVerification.jsx`
- `hod/academic-lists/AcademicLists.jsx`
- `hod/department-management/DepartmentManagement.jsx`
- `hod/lecturer-assignment/LecturerAssignment.jsx`
- `universityAdmin/academic-structure/AcademicStructure.jsx`
- And 2 more...

**Pattern**: Fetch from academicService or resultService. Use Pattern 1 or 2.

---

## General Rules to Follow

1. **NO hardcoded data** - All data comes from services
2. **All data fetches use useApi** - Never `useState` + `useEffect` manually
3. **Service calls only** - Components never call axios directly
4. **Role-based scoping** - Always filter by user's role/scope
5. **Loading + Empty states** - Every page shows loading and empty messages
6. **Error handling** - Catch errors and display via toast or inline
7. **Server validation** - Pass `serverErrors` to Form component
8. **Pagination** - Implement page state + pagination object for CRUDTable
9. **Refresh on success** - Call `refresh()` hook after create/update/delete

---

## Column Field Mapping

When refactoring pages, map the old field names to actual API response fields:

**Common mappings:**
- `firstName` → `first_name`
- `lastName` → `last_name`
- `email` → `email`
- `studentId`, `matricNumber` → `matric_number`
- `program` → `program_id` or `program.name`
- `department` → `department_id` or `department.name`
- `role` → `role`
- `status` → `status` or `is_active`
- `enrolledStudents` → `student_count`
- `createdAt` → `created_at`

---

## Example Refactor (Before → After)

### Before (Hardcoded)
```jsx
const [items, setItems] = useState([
  { id: 1, name: 'Item 1', status: 'active' }
]);

useEffect(() => {
  // TODO: Load from API
}, []);
```

### After (API-Driven)
```jsx
const fetchItems = useCallback(
  () => courseService.getCourses({ page, pageSize: 20 }),
  [page]
);
const { data: resp, loading } = useApi(fetchItems, [page]);
const items = resp?.results || [];
```

---

## Running the Refactoring

To quickly apply this pattern to all remaining pages:

1. Identify TODO comments: `grep -r "TODO" src/modules --include="*.jsx"`
2. For each file, identify:
   - What data does it need?
   - Which service has that data?
   - Is it a CRUD page or read-only?
3. Apply the appropriate pattern
4. Test: Ensure API endpoints match the service calls
5. Check API responses match field names in columns

---

## Testing

After refactoring each page:
1. Check browser console for errors
2. Verify network calls in DevTools
3. Test pagination (if applicable)
4. Test error handling (stop backend API temporarily)
5. Test empty states
6. Test loading states

---

## Final Checklist

- [ ] No hardcoded arrays or objects
- [ ] useApi used for all data fetches
- [ ] Services used for all API calls
- [ ] Loading states shown
- [ ] Empty states shown
- [ ] Error handling in place
- [ ] Role-based filtering applied
- [ ] Pagination working (if needed)
- [ ] Column names match API response
- [ ] Form validation errors displayed
- [ ] Toast notifications after CRUD operations

