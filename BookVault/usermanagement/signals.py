from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MemberProfile, User, LibrarianProfile


@receiver(post_save, sender=User)
def create_librarian_profile(sender, instance, created, **kwargs):
    if created and instance.role == "Librarian":
        LibrarianProfile.objects.create(user=instance)


