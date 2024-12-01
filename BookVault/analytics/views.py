from django.shortcuts import render
from django.db.models import Count
from book.models import Author, Book, Genre
from usermanagement.models import BookIssueTransaction, Subscription,MemberSubscriptionLog,User
from .utils import fetch_google_books_metadata
from django.core.mail import EmailMessage
from django.conf import settings 
from .models import Notification
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt


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


def search_digital_books(request):
    query = request.GET.get('q', '')
    digital_books = []
    if query:
        digital_books = fetch_google_books_metadata(query)
    return render(request, 'client/digital_books.html', {'books': digital_books})


def send_email_notification_to_users(subject, message):
    users = User.objects.all()
    email_addresses = users.values_list('email', flat=True)  
    email = EmailMessage(
        subject,           
        message,            
        settings.EMAIL_HOST_USER,  
        [settings.EMAIL_HOST_USER],  
        bcc=email_addresses,  
    )
    email.send(fail_silently=False)
    return "Emails sent to users successfully."


def send_notification(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        result = send_email_notification_to_users(subject, message)
        return render(request, 'admindashboard/send_notification.html', {'result': result})
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


def user_notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    return render(request, 'notifications.html', {'notifications': notifications})


def mark_notification_read(request, notification_id):
    notification = Notification.objects.get(id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({"status": "success"})


def membernotifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    return render(request, 'client/membernotifications.html', {'notifications': notifications})


def create_notification(user, message):
    notification = Notification(user=user, message=message)
    notification.save()


def inventory(request):
    books = Book.objects.all()
    return render(request, 'libriarian/inventory.html',{'books': books})


@csrf_exempt  
def update_copies_post(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == "POST":
        count = request.POST.get('count')
        if not count:
            messages.error(request, "Please provide a valid count.")
            return redirect('book_inventory')
        try:
            count = int(count)
            if count < 0 and (book.available_copies + count < 0 or book.total_copies + count < 0):
                book.total_copies = 0
                book.available_copies = 0
                book.save()
                messages.warning(
                    request,
                    f"Cannot subtract {abs(count)} copies as there were not enough. Stock is now reset to zero."
                )
            else:
                book.total_copies += count
                book.available_copies += count
                book.save()
                if count > 0:
                    messages.success(request, f"Successfully added {count} copies to '{book.title}'.")
                elif count < 0:
                    messages.success(request, f"Successfully removed {abs(count)} copies from '{book.title}'.")
        except ValueError as e:
            messages.error(request, f"Error: {e}")
    return redirect('inventory')

from django.db.models import Sum

def penalty(request):
    # Get all transactions for the current user with penalties greater than 0.0
    penalty_transactions = BookIssueTransaction.objects.filter(user=request.user, penalties__gt=0.0)
    
    # Calculate the sum of all penalties for that user
    total_penalty = penalty_transactions.aggregate(Sum('penalties'))['penalties__sum'] or 0.0
    total_penalty_paise=total_penalty*100
    
    # Pass both the penalty transactions and the total penalty to the template
    return render(request, 'client/pay_penalty.html', {
        'penalty': penalty_transactions,
        'total_penalty': total_penalty,
        'total_penalty_paise':total_penalty_paise
    })
import razorpay
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse

def pay_penalty(request):
    # Get all penalty transactions for the user with penalties greater than 0.0
    penalty_transactions = BookIssueTransaction.objects.filter(user=request.user, penalties__gt=0.0)
    
    # Calculate the sum of all penalties
    total_penalty = penalty_transactions.aggregate(Sum('penalties'))['penalties__sum'] or 0.0
    
    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

    # Create a Razorpay order (this could be based on the total penalty)
    if total_penalty > 0:
        order_amount = int(total_penalty * 100)  # Amount in paise (1 INR = 100 paise)
        order_currency = 'INR'
        
        order = client.order.create(dict(
            amount=order_amount,
            currency=order_currency,
            payment_capture='1'  # Capture the payment automatically
        ))
        BookIssueTransaction.objects.filter(user=request.user, penalties__gt=0.0).update(penalty_paid=True)
        # Pass the Razorpay order ID to the template
        razorpay_key = settings.RAZOR_KEY_ID
        return render(request, 'client/pay_penalty.html', {
            'penalty': penalty_transactions,
            'total_penalty': total_penalty,
            'razorpay_key': razorpay_key,
            'order_id': order['id']
        })
    else:
        return render(request, 'client/pay_penalty.html', {'penalty': penalty_transactions, 'total_penalty': total_penalty})
