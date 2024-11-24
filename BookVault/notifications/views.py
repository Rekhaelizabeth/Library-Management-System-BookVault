from django.shortcuts import render, get_object_or_404, redirect
from usermanagement.models import Subscription, MemberProfile
from django.contrib.auth.decorators import login_required

@login_required
def list_subscriptions(request):
    subscriptions = Subscription.objects.all()
    return render(request, "member/list_subscriptions.html", {"subscriptions": subscriptions})
