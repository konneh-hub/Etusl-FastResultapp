.# TODO: Update Django Admin for System Admins

## Steps to Complete

- [x] Add 'system_admin' to ROLE_CHOICES in `core/constants/__init__.py`
- [ ] Add new models in `systemadmin/models.py` for Backup, APIKey, GlobalReport
- [ ] Update `systemadmin/admin.py` to register all models with custom admin classes
- [ ] Create custom admin for User model in `accounts/admin.py` filtered for system_admin role
- [ ] Customize admin site with sidebar menu and KPIs/charts in dashboard
- [ ] Test the admin interface
- [ ] Add export/download features if needed
