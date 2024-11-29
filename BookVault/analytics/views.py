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
