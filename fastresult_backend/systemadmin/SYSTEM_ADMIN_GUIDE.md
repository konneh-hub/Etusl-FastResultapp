# System Admin Dashboard - Complete Guide

## Overview

The System Admin Dashboard is a comprehensive management interface for system administrators to manage the entire SRMS system at a global level without touching individual university data.

## Features & Modules

### 1. Universities Management

Manage all universities in the system globally.

**Features:**
- View list of all universities
- Search by: Name, Code
- Filter by: Status (Active/Inactive), Accreditation Status
- Add, Edit, Delete universities
- Activate/Deactivate universities bulk actions
- Export universities to CSV

**Table Columns:**
- University Name
- Code
- Accreditation Status (badge: Green=Accredited, Yellow=Provisional, Blue=Pending, Red=Revoked)
- Status (Active/Inactive)
- Created At
- Actions (Edit, Delete)

**Access URL:** `/admin/systemadmin/universityregistry/`

---

### 2. System Admin Users

Manage system-level administrators (your peers).

**Features:**
- View list of system admins
- Search by: Email, Name
- Filter by: Active/Inactive, Superuser Status, Role, Date Created, Last Login
- Add new system admin
- Edit admin details
- Toggle superuser status (batch action)
- Activate/Deactivate admins (batch actions)
- View: Email, Role, Active Status, Superuser Status, Last Login, 2FA Status

**Bulk Actions:**
- `Activate selected admins` - Activate multiple admins at once
- `Deactivate selected admins` - Deactivate multiple admins
- `Toggle superuser status` - Grant/remove superuser privileges

**Fields:**
- User (dropdown with email)
- Role (System Admin roles only)
- Is Superuser Flag
- Permissions Override (multi-select)
- 2FA Enabled (checkbox)
- Last Login (read-only)
- Password Last Changed (read-only)
- Notes (text)

**Access URL:** `/admin/systemadmin/systemadminuser/`

---

### 3. System Settings

Global system configurations affecting all universities.

**Features:**
- View list of all system settings
- Search by: Label, Key, Value, Description
- Filter by: Category, Setting Type, Editable, Public, University
- Edit setting values with type validation
- Make settings editable/read-only (batch actions)
- Make settings public/private (batch actions)

**Categories:**
- System (default academic year, etc.)
- Security (password policies, etc.)
- Email (SMTP settings)
- SMS (SMS gateway settings)
- Payment (payment processor settings)
- File Upload (upload limits, etc.)
- API (API default limits)
- UI/UX (UI configurations)

**Setting Types:**
- String
- Integer
- Boolean
- JSON
- Decimal

**Access URL:** `/admin/systemadmin/platformsetting/`

---

### 4. Audit Logs

Track all system-level activity for accountability.

**Features:**
- View all audit logs
- Search by: User, Model Name, Object ID, IP Address, Error Message
- Filter by: Action, Status, Model Name, Date Range, University
- Export logs to CSV
- Export logs to JSON
- View detailed log information
- Date-based hierarchy navigation

**Log Information:**
- User (who performed the action)
- Action (Create, Update, Delete, View, Approve, Reject, Export, Import, Login, Logout)
- Model Name (what was changed)
- Object ID (which object)
- Status (Success, Failure, Partial)
- Old Values (previous state - JSON)
- New Values (new state - JSON)
- IP Address
- User Agent
- Error Message (if failed)
- Timestamp

**Read-Only:** All logs are read-only and cannot be modified or deleted

**Access URL:** `/admin/systemadmin/auditlog/`

---

### 5. Backup & Restore

Manage system backups for disaster recovery.

**Features:**
- View list of backups
- Search by: Backup Name, Initiated By
- Filter by: Backup Type, Status, Date Range
- View backup details (file size in MB, duration, data count)
- Track backup progress (Pending → In Progress → Completed/Failed)

**Backup Types:**
- Full Backup (complete database)
- Incremental Backup (only changes since last backup)
- Differential Backup (changes since last full backup)

**Status:**
- Pending (awaiting execution)
- In Progress (currently backing up)
- Completed (successful)
- Failed (encountered error)

**Details Captured:**
- Backup Name
- Backup Type
- Status with Badge (color-coded)
- File Size (display in MB)
- Started At / Completed At
- Duration (automatically calculated)
- Initiated By (admin user)
- Error Message (if failed)
- Data Count (JSON object count)

**Access URL:** `/admin/systemadmin/backuplog/`

---

### 6. Integrations

Manage external service integrations (Email, SMS, Payment, etc.)

**Features:**
- View active integrations
- Search by: Name, Description
- Filter by: Integration Type, Status, Last Test Status, Date Range
- Test integrations (batch action)
- Activate/Deactivate integrations (batch actions)
- Edit configuration
- Set webhooks

**Integration Types:**
- Email/SMTP
- SMS Gateway
- Push Notification Service
- Payment Gateway
- LMS Integration
- ERP Integration
- Custom Integration

**Status:**
- Active (functioning)
- Inactive (disabled)
- Error (failed)
- Maintenance (under maintenance)

**Test Results:**
- Success (✓ Green)
- Failed (✗ Red)
- Pending (? Gray)

**Configuration:**
- Service credentials (encrypted in database)
- Webhook URL for incoming events
- Last test timestamp
- Last test status

**Access URL:** `/admin/systemadmin/integration/`

---

### 7. API Keys & Access

Manage API keys for external integrations.

**Features:**
- View all API keys
- Search by: Key Name, Integration Name, Created By
- Filter by: Status, Integration, Creation Date, Expiration Date
- Generate new key
- Revoke keys (batch action)
- Reset usage counters (batch action)
- View usage metrics

**Key Information:**
- Name
- Integration (which service)
- Status (Active, Revoked, Expired - with badges)
- Created By
- Expires At
- Last Used At
- Usage Count
- Rate Limit (requests per hour)
- IP Whitelist (JSON array)

**Actions:**
- Revoke Key (deactivate immediately)
- Reset Usage Counter
- View Key Details
- Download Key (one-time)

**Security:**
- Keys are stored as SHA256 hashes
- Display only hash, not actual key
- Track usage per key
- Set expiration dates
- IP whitelisting support

**Access URL:** `/admin/systemadmin/apikey/`

---

### 8. Roles & Permissions

Manage system-level roles and permissions.

**Features:**
- View all system roles
- Search by: Name, Description
- Filter by: Role Type, Hierarchy Level, Active Status
- Assign permissions to roles
- Create custom roles
- Set role hierarchy

**Role Types:**
- System Admin (highest level)
- University Admin
- Head of Department
- Dean
- Lecturer
- Exam Officer
- Student
- Support Staff

**Hierarchy Levels:**
- 0: System Admin (highest)
- 1: University Admin
- ...
- 10: Student (lowest)

**Permissions:**
- View resources
- Create resources
- Edit resources
- Delete resources
- Approve workflows
- Export data
- Import data
- Manage resources

**Access URL:** `/admin/systemadmin/roletemplate/`

---

## Dashboard Overview

The System Admin Dashboard home page displays:

### KPI Cards (Top Section)
- **Universities:** Total count with Active/Inactive breakdown
- **System Admins:** Total count with Superuser indication
- **Total Users:** Across all universities
- **System Settings:** Quick link to configurations

### Module Cards (Middle Section)
Eight main module cards:
1. 🏫 Universities - Manage all universities
2. 👥 System Admins - Manage system administrators
3. ⚙️ System Settings - Global configurations
4. 📊 Audit Logs - System activity tracking
5. 💾 Backups - Backup management
6. 🔌 Integrations - External service integrations
7. 🔐 API Keys - API access management
8. 🎯 Roles & Permissions - Role and permission management

### Recent Activity Section
Table showing last 10 actions:
- User who performed action
- Action type (color-coded badges)
- Object/Model affected
- Status (Success/Failure/Partial)
- Timestamp

---

## Common Tasks

### Managing Universities

1. Go to Universities section
2. Click "Add University" or search for existing
3. Fill in details:
   - Name (unique)
   - Code (unique)
   - Contact info
   - Address
   - Accreditation status
4. Save
5. To deactivate: Select university, choose "Deactivate selected universities" action

### Managing System Admins

1. Go to System Admins section
2. Click "Add System Admin"
3. Select user from dropdown
4. Assign role
5. Optionally grant superuser status
6. Press Save

### Viewing Audit Logs

1. Go to Audit Logs
2. Use filters: Date range, action type, admin user
3. Click on log entry for details
4. Use "Export logs as CSV" or "Export logs as JSON" to download

### Testing Integrations

1. Go to Integrations
2. Select integrations to test
3. Click "Test selected integrations" action
4. Check "Last Test Status" for results

### Generating Backups

1. Use external backup management tool
2. Go to Backups to view status
3. Filter by date, status, backup type
4. View file size and duration

### Managing API Keys

1. Go to API Keys
2. View active keys
3. To revoke: Select key, click "Revoke selected keys"
4. To reset usage: Select key, click "Reset usage counters"
5. Monitor last used date and usage count

---

## Filters & Search Tips

### Using Search
- Search works on multiple fields
- Case-insensitive
- Partial matches supported
- Search across: names, codes, emails, IDs

### Using Filters
- Multiple filters can be combined
- Filters narrow down results progressively
- Date range filters: Use date hierarchy or select range
- Status filters: Use color badges to understand meanings
- Reset filters: Click filter name to toggle off

### Using Date Hierarchy
- Some lists (Audit Logs, Backups) support date hierarchy
- Navigate by: Year → Month → Day
- Back button to go to previous level

---

## Bulk Actions

Bulk actions appear when selecting multiple items:

1. Select items using checkboxes
2. A "Go" button appears
3. Choose action from dropdown
4. Click "Go" to execute

**Available Bulk Actions:**

**Universities:**
- Activate selected universities
- Deactivate selected universities
- Export as CSV

**System Admins:**
- Activate selected admins
- Deactivate selected admins
- Toggle superuser status

**Platform Settings:**
- Make editable
- Make read-only
- Make public
- Make private

**Integrations:**
- Activate integrations
- Deactivate integrations
- Test connections

**API Keys:**
- Revoke keys
- Reset usage counters

**Audit Logs:**
- Export as CSV
- Export as JSON

---

## Security Considerations

1. **Audit Logs:** All admin actions are logged and cannot be deleted
2. **API Keys:** Stored as hashes, original key shown only once
3. **Encrypted Configuration:** Integration configs are encrypted in database
4. **IP Whitelisting:** API keys can be restricted to specific IPs
5. **Read-Only:** Sensitive items (logs, backups) are read-only
6. **2FA:** System admins should enable two-factor authentication

---

## Export & Reporting

### CSV Export
Available for:
- Universities list
- Audit logs

Format: UTF-8, comma-delimited
Columns included: Primary data fields

### JSON Export
Available for:
- Audit logs (complete data)

Format: Pretty-printed JSON with all nested objects

### Reports Available
- System metrics (KPIs on dashboard)
- Audit activity logs
- Integration status
- Backup history
- User activity

---

## Troubleshooting

### Integration Test Failed
1. Check configuration (URL, credentials)
2. Verify service is online
3. Check firewall/network settings
4. Review error message in Integration detail

### Cannot Activate University
1. Check if all required fields are filled
2. Verify code/name are unique
3. Check university not referenced by active data

### Audit Log Searches Slow
1. Use date range filters
2. Filter by specific action type
3. Archive old logs if database is large

### API Key Expired
1. Delete expired key
2. Generate new key
3. Update external service with new key

---

## Best Practices

1. **Regular Backups:** Schedule automated daily backups
2. **Audit Review:** Review audit logs weekly
3. **Permission Audit:** Review admin permissions quarterly
4. **API Key Rotation:** Rotate API keys every 6 months
5. **Integration Testing:** Test integrations after configuration changes
6. **Settings Documentation:** Document why each setting was changed
7. **Backup Testing:** Periodically test backup restore procedures

---

## Support

For issues with the System Admin Dashboard:
1. Check audit logs for related actions
2. Review integration test results
3. Verify database backup status
4. Contact system support with timestamp and action details

---

**Dashboard Version:** 1.0  
**Last Updated:** February 8, 2026  
**System:** FastResult SRMS
