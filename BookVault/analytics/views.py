from django.shortcuts import render
from django.db.models import Count
from book.models import Author, Genre
from usermanagement.models import Subscription,MemberSubscriptionLog,User

# Create your views here.
def view_subscription(request):
    subscription = Subscription.objects.all()
    top_subscription = (
        MemberSubscriptionLog.objects.values('subscription__plan_name')
        .annotate(count=Count('subscription'))
        .order_by('-count')
        .first()
    )
    context = {
        'subscription': subscription,
        'top_subscription': top_subscription,
    }
    return render(request, 'admindashboard/view_subscription.html', context)

from django.shortcuts import render
from .utils import fetch_google_books_metadata  # Import the helper function

def search_digital_books(request):
    
    query = request.GET.get('q', '')
    digital_books = []
    
    if query:
        digital_books = fetch_google_books_metadata(query)
    
    return render(request, 'client/digital_books.html', {'books': digital_books})


from django.shortcuts import render
from django.core.mail import EmailMessage
from django.conf import settings  # Import your User model

def send_email_notification_to_users(subject, message):
    """
    Sends an email notification to all users in the User table using BCC.
    
    Parameters:
    - subject: The subject of the email.
    - message: The content of the email body.
    
    Returns:
    - str: A success message indicating the emails were sent.
    """
    # Retrieve all email addresses from the User table
    users = User.objects.all()
    email_addresses = users.values_list('email', flat=True)  # Get a list of email addresses

    # Create the email message
    email = EmailMessage(
        subject,              # Subject of the email
        message,              # Body of the email
        settings.EMAIL_HOST_USER,  # From email (configured in settings.py)
        [settings.EMAIL_HOST_USER],  # To field (can be empty or just sender email)
        bcc=email_addresses,  # Add all users to the BCC field
    )

    # Send the email
    email.send(fail_silently=False)
    
    return "Emails sent to users successfully."

def send_notification(request):
    if request.method == 'POST':
        # Retrieve subject and message from the POST request
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Call the function to send email
        result = send_email_notification_to_users(subject, message)
        
        # Pass the result to the template for feedback
        return render(request, 'admindashboard/send_notification.html', {'result': result})
    
    # If not POST, just render the form
    return render(request, 'admindashboard/send_notification.html')


def adminbook_analytics(request):
    return render(request, 'admindashboard/adminbook_analytics.html')


def books_by_genre_analytics(request):
    books_by_genre = Genre.objects.annotate(book_count=Count('books')).order_by('-book_count')
    
    genre_labels = [genre.name for genre in books_by_genre]
    genre_counts = [genre.book_count for genre in books_by_genre]

    context = {
        'genre_labels': genre_labels,
        'genre_counts': genre_counts,
    }

    return render(request, 'admindashboard/books_by_genre_analytics.html', context)

def books_by_author_analytics(request):
    books_by_genre = Genre.objects.annotate(book_count=Count('books')).order_by('-book_count')
    genre_labels = [genre.name for genre in books_by_genre]
    genre_counts = [genre.book_count for genre in books_by_genre]

    # Data for Books by Author
    books_by_author = Author.objects.annotate(book_count=Count('books')).order_by('-book_count')[:10]
    author_labels = [f"{author.first_name} {author.last_name}" for author in books_by_author]
    author_counts = [author.book_count for author in books_by_author]

    context = {
        'genre_labels': genre_labels,
        'genre_counts': genre_counts,
        'author_labels': author_labels,
        'author_counts': author_counts,
    }

    return render(request, 'admindashboard/books_by_author_analytics.html', context)

from django.shortcuts import render
from .models import Notification

def user_notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    return render(request, 'notifications.html', {'notifications': notifications})
from django.http import JsonResponse
from .models import Notification

def mark_notification_read(request, notification_id):
    notification = Notification.objects.get(id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({"status": "success"})

def membernotifications(request):
    # Get all notifications for the current user that are unread
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    return render(request, 'client/membernotifications.html', {'notifications': notifications})
def create_notification(user, message):
    notification = Notification(user=user, message=message)
    notification.save()
