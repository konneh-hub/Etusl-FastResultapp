# System Admin Dashboard - Quick Start Guide

## 🚀 Quick Access

The System Admin Dashboard is already fully implemented and ready to use!

### Access the Dashboard
1. Start the Django development server:
   ```bash
   cd c:\SRMS\fastresult_backend
   python manage.py runserver
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8000/admin/
   ```

3. Log in with your admin credentials

4. You'll see the custom System Admin Dashboard with all modules

---

## 📌 8 Core Modules Available

### 1. 🏫 Universities
**Manage all universities in the system**
- URL: `/admin/systemadmin/universityregistry/`
- Actions: Create, Edit, Delete, Activate, Deactivate, Export CSV
- Search: Name, Code, Email, City
- Filters: Status, Accreditation, Country, Date Created

### 2. 👥 System Admins  
**Manage system administrators**
- URL: `/admin/systemadmin/systemadminuser/`
- Actions: Create Admin, Edit, Deactivate, Toggle Superuser
- Search: Email, First Name, Last Name, Username
- Filters: Active Status, Superuser, Role, Last Login
- Track: Last Login, 2FA Status, Password Last Changed

### 3. ⚙️ System Settings
**Global system configurations**
- URL: `/admin/systemadmin/platformsetting/`
- Categories: System, Security, Email, SMS, Payment, File Upload, API, UI
- Search: Label, Key, Value, Description
- Actions: Edit, Toggle Editable/Public, Bulk Update
- Features: Type validation, University overrides

### 4. 📊 Audit Logs
**Track all system admin activity**
- URL: `/admin/systemadmin/auditlog/`
- Search: User, Action, Model, Object ID, IP Address
- Actions: Filter by date, Export CSV, Export JSON
- Features: Immutable (read-only), Date hierarchy, Status tracking
- Track: Who did what, when, where, and result

### 5. 💾 Backup & Restore
**Manage system backups**
- URL: `/admin/systemadmin/backuplog/`
- Search: Backup Name, Initiated By
- Track: Status, File Size, Duration, Data Count
- Types: Full, Incremental, Differential
- Status: Pending, In Progress, Completed, Failed

### 6. 🔌 Integrations
**Manage external service integrations**
- URL: `/admin/systemadmin/integration/`
- Types: Email/SMTP, SMS, Push Notification, Payment, LMS, ERP, Custom
- Features: Test Connections, Configuration Management, Webhook URLs
- Status: Active, Inactive, Error, Maintenance
- Actions: Activate, Deactivate, Test, Edit Configuration

### 7. 🔐 API Keys
**Manage API access**
- URL: `/admin/systemadmin/apikey/`
- Features: Rate limiting, Expiration dates, Usage tracking, IP whitelist
- Security: Keys stored as SHA256 hashes
- Actions: Revoke, Reset Usage, Set Expiration
- Monitor: Last used date, usage count, active status

### 8. 🎯 Roles & Permissions
**Manage system roles and permissions**
- URL: `/admin/systemadmin/roletemplate/`
- Features: Role hierarchy, Permission assignment, Module admin flag
- Search: Name, Description
- View: Assigned permissions, Role type, Hierarchy level

---

## ✨ Dashboard Features

### KPI Cards (at top of dashboard)
- **Universities:** Total, Active, Inactive breakdown
- **System Admins:** Total count + Superuser indicator  
- **Total Users:** Across all universities
- **System Settings:** Quick access link

### Module Cards
8 clickable cards for quick access to each module with descriptions

### Recent Activity
Table showing last 10 admin actions with:
- User who performed action
- Action type (Create, Update, Delete, etc.)
- Object affected
- Status (Success/Failure/Partial)
- Timestamp

---

## 🔍 How to Use Each Module

### Managing Universities
1. Go to: `/admin/systemadmin/universityregistry/`
2. Click "Add University" or search for existing university
3. Fill in: Name, Code, Email, Phone, Address, etc.
4. Click "Save"
5. To deactivate: Select university → Choose "Deactivate universities" → Click "Go"

### Managing System Admins
1. Go to: `/admin/systemadmin/systemadminuser/`
2. Click "Add System Admin User"
3. Select user from dropdown
4. Assign role and permissions
5. Optionally grant superuser status
6. Save

### Configuring System Settings
1. Go to: `/admin/systemadmin/platformsetting/`
2. Search for setting or browse by category
3. Click on setting to edit value
4. Choose setting type (String, Integer, Boolean, JSON, Decimal)
5. Update value and save
6. Changes apply globally to all universities

### Viewing Audit Logs
1. Go to: `/admin/systemadmin/auditlog/`
2. Use filters: Date, Action type, Admin user
3. Search by: User, Model, Object ID
4. Export: Select items → "Export as CSV" or "JSON"

### Managing API Keys
1. Go to: `/admin/systemadmin/apikey/`
2. Create new: Click "Add API Key"
3. Select integration
4. Set: Name, Expiration date, Rate limit, IP whitelist
5. Save
6. To revoke: Select key → "Revoke keys" → "Go"

### Testing Integrations
1. Go to: `/admin/systemadmin/integration/`
2. Select integrations to test
3. Click "Test selected integrations"
4. Check "Last Test Status" for results

---

## 📋 Common Tasks

### Create a System Admin User
```
1. Go to System Admins
2. Click "Add System Admin User"
3. Select user
4. Set role to "System Admin"
5. Save
```

### Export Audit Logs
```
1. Go to Audit Logs
2. Filter by date range if needed
3. Select logs
4. Choose "Export as CSV" or "Export as JSON"
5. Click "Go"
```

### Configure Email Integration
```
1. Go to Integrations
2. Find "Email/SMTP" or create new
3. Edit and fill in:
   - SMTP Server
   - Port
   - Username
   - Password
   - From Email
4. Click "Test selected integrations"
5. Check status
```

### Revoke API Key
```
1. Go to API Keys
2. Find key to revoke
3. Check checkbox
4. Choose "Revoke keys"
5. Click "Go"
```

### View System Activity
```
1. Go to Audit Logs
2. View recent actions
3. Click any action to see:
   - Old values (before change)
   - New values (after change)
   - IP address
   - User agent
   - Error message (if failed)
```

---

## 🔐 Security Features

### Audit Logging
- All admin actions are logged
- Logs cannot be deleted (read-only)
- Track who did what, when, and where
- Export for external audit

### API Key Security
- Keys stored as SHA256 hashes
- Original key shown only once
- Expiration dates supported
- IP whitelisting available
- Usage tracking

### Integration Security
- Configuration stored encrypted
- Sensitive data protected
- Test before activating
- Error logging and monitoring

### Permission Management
- Role-based access control
- Superuser flag for global permissions
- Audit of permission changes
- Override permissions available

---

## 📊 Dashboard Metrics

The dashboard displays real-time metrics:
- Total universities (active + inactive)
- Total system admins (active + superusers)
- Total users across system
- Settings count by category
- Integration status (active/errors)
- Recent backup date
- API key usage

---

## ⚙️ Customization (Advanced)

### Change Dashboard Colors
Edit: `/templates/admin/index.html`
Look for hex colors like `#667eea`, `#3498db`, etc.

### Add More KPI Cards
1. Edit: `/templates/admin/index.html`
2. Add new card in KPI section
3. Update: `systemadmin/admin_customization.py` to provide data

### Create Custom Admin Actions
In `/systemadmin/admin.py`:
```python
def my_custom_action(modeladmin, request, queryset):
    # Your code here
    modeladmin.message_user(request, "Action completed!")
my_custom_action.short_description = "My Custom Action"
```

---

## 🆘 Troubleshooting

### Dashboard Not Loading
- Ensure systemadmin app is in INSTALLED_APPS ✅ (Done)
- Run: `python manage.py migrate` ✅ (Done)
- Clear browser cache

### Can't See New Settings
- Check INSTALLED_APPS in settings
- Run: `python manage.py makemigrations`
- Run: `python manage.py migrate`

### Admin Site Styling Issues
- Check templates/admin/index.html
- Verify static files: `python manage.py collectstatic`

### Integration Test Fails
- Check configuration values
- Verify service is online
- Check firewall/network
- Review error message in Integration details

---

## 📚 More Information

For detailed information about each module, see:
- `systemadmin/SYSTEM_ADMIN_GUIDE.md` - Complete feature documentation
- `SYSTEM_ADMIN_IMPLEMENTATION.md` - Implementation details
- Model docstrings in `systemadmin/models.py`

---

## 🎯 Next Steps

### Immediate (Today)
- [ ] Log into admin: `/admin/`
- [ ] Create system admin users
- [ ] Configure email integration
- [ ] Test integrations

### Short Term (This Week)
- [ ] Configure SMS integration
- [ ] Set up API keys
- [ ] Review audit logs
- [ ] Create backup

### Medium Term (This Month)
- [ ] Set up automated backups
- [ ] Configure all integrations
- [ ] Review and adjust system settings
- [ ] Train admin team on dashboard

---

## 📞 Support

For issues or questions:
1. Check `SYSTEM_ADMIN_GUIDE.md` troubleshooting section
2. Review Django admin documentation
3. Check audit logs for related actions
4. Verify database and file permissions

---

**Dashboard Version:** 1.0  
**Status:** ✅ Ready to Use  
**Last Updated:** February 8, 2026
