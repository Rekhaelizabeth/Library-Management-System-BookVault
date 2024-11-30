from django.db import models

# Create your models here.
from usermanagement.models import User

# Create your models here.
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # The user the notification belongs to
    message = models.CharField(max_length=255)  # Notification content
    is_read = models.BooleanField(default=False)  # Track if the notification has been read
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when notification was created

    def str(self):
        return f"Notification for {self.user.username}"