from django.apps import AppConfig


class SystemadminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'systemadmin'
    verbose_name = 'System Administration'

    def ready(self):
        import systemadmin.signals  # noqa
