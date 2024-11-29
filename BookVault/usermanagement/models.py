from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from book.models import Genre,Book
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import now

class Address(models.Model):
    id = models.AutoField(primary_key=True)
    addressline = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    def str(self):
        return f"{self.street}, {self.city}, {self.state}, {self.country} - {self.postal_code}"
    
    
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.OneToOneField("Address", on_delete=models.SET_NULL, null=True, blank=True)
    notifications_preferences = models.BooleanField(default=False)
    gender = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(
        max_length=50,
        choices=[
            ("Admin", "Admin"),
            ("Librarian", "Librarian"),
            ("Member", "Member"),
        ],
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    status=models.BooleanField(default=False)

    # Custom manager
    objects = UserManager()

    # Required fields for Django user model
    USERNAME_FIELD = "email"  # Use email for authentication
    REQUIRED_FIELDS = ["name"]  # Fields required when creating a superuser

    def __str__(self):
        return f"{self.name} ({self.role})"


    
class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def str(self):
        return f"Admin: {self.user.name}"
    

class LibrarianProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    assigned_branch = models.CharField(max_length=255, blank=True, null=True)  # For multi-branch LMS
    specialization = models.CharField(max_length=255, blank=True, null=True)  # Expertise in genres/subjects
    issued_books_count = models.IntegerField(default=0)  # Count of books managed by this librarian
    damaged_books_count = models.IntegerField(default=0)  # Count of books managed by this librarian
    digital_library_access = models.BooleanField(default=False)  # Access to manage eBooks or digital content
    contact_preferences = models.JSONField(default=dict)  # e.g., preferred email/SMS for notifications
    performance_rating = models.FloatField(default=0.0)  # Aggregate rating from feedback
    issue_resolution_count = models.IntegerField(default=0)  # Number of resolved member issues
    last_login_time = models.DateTimeField(blank=True, null=True)  # To track active participation


    def str(self):
        return f"Librarian: {self.user.name}"
    
    
class Subscription(models.Model):
    plan_name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Example: 999.99
    time_period = models.IntegerField(help_text="Duration of the subscription in days")  # Example: 30 days
    book_reservation_count = models.IntegerField(default=0, help_text="Number of books a user can reserve")
    issue_book_count = models.IntegerField(default=0, help_text="Number of books a user can issue at a time")
    external_library_access = models.BooleanField(default=False, help_text="Whether the subscription includes external library access")
    status=models.BooleanField(default=False)

    def __str__(self):
        return f"{self.plan_name} Plan"

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"

class MemberSubscriptionLog(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
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
        return f"{self.subscription.plan_name}"

class MemberProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    membership_type = models.CharField(
        max_length=50,
        choices=[
            ('Student', 'Student'),
            ('Faculty', 'Faculty'),
            ('General', 'General'),
        ]
    )
    membership_expiry = models.DateField(null=True)
    borrowing_limit = models.IntegerField(default=5)
    outstanding_fines = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    reserved_books_count = models.IntegerField(default=0)
    favorite_genres = models.CharField(max_length=255, blank=True, null=True)
    libriarian_approved = models.BooleanField(default=False)
    subscription = models.ForeignKey(
        MemberSubscriptionLog, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="members"
    )  # ForeignKey allows multiple members to share the same subscription.



    def str(self):
        return f"Member: {self.user.name}"
    

class BookIssueTransaction(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    issue_date = models.DateField(default=timezone.now)
    return_date = models.DateField(null=True, blank=True)
    returnExtensionDate = models.IntegerField(null=True)
    penalties = models.FloatField(default=0.0)


    due_date = models.DateField(default=timezone.now() + timedelta(days=14))  # Assuming 2-week loan period
    status_choices = [
        ('ISSUED', 'Issued'),
        ('RETURNED', 'Returned'),
        ('LOST', 'Issued'),
        ('DAMAGED', 'Damaged'),
        ('REQUESTED','Requested')
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='ISSUED')
    issuedby = models.ForeignKey(
        LibrarianProfile, 
        on_delete=models.CASCADE, 
        blank=True,  # Allow this field to be left blank in forms
        null=True     # Allow this field to be NULL in the database
    )

    def str(self):
        return f"Book: {self.book.title}, Issued to: {self.user.username}, Due: {self.due_date}"
    
class BookReservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who is reserving the book
    reserved_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    def str(self):
        return f"Reservation by {self.user.username} for {self.book.title}"

    class Meta:
        unique_together = ('book', 'user')  # Ensures a user can reserve a specific book only once


class Reviews(models.Model):
    book = models.ForeignKey(Book,on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()  # Rating from 1-5
    review_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.book.title}"
    

class Suggestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    suggestion_text = models.TextField()
    submitted_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Suggestion by {self.user.username} on {self.submitted_at}"
