from django.db import models
from usermanagement.models import User

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    message = models.CharField(max_length=255)  
    is_read = models.BooleanField(default=False)  
    created_at = models.DateTimeField(auto_now_add=True)  
    def str(self):
        return f"Notification for {self.user.username}"