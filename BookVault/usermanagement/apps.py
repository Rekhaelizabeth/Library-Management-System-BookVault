
from django.apps import AppConfig

class UserManagementConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "usermanagement"

    def ready(self):
        import usermanagement.signals  # Import signals here
