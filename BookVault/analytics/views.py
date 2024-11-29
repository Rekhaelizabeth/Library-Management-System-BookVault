from django.shortcuts import render
from django.db.models import Count
from usermanagement.models import Subscription,MemberSubscriptionLog

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
