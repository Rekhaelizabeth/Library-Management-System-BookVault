from django.db import models
from django.utils import timezone
from usermanagement.models import MemberProfile, Subscription

class SubscriptionLog(models.Model):
    member = models.ForeignKey(MemberProfile, on_delete=models.CASCADE, related_name="subscriptions")
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="logs")
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    status=models.BooleanField(default=False)
    payment_status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("Completed", "Completed")],
        default="Pending",
    )
    payment_id = models.CharField(max_length=100, blank=True, null=True)  # Razorpay Payment ID

    def str(self):
        return f"{self.member.user.name} - {self.subscription.plan_name}"

