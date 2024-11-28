import razorpay
from django.conf import settings
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from usermanagement.models import Subscription, MemberProfile
from django.contrib.auth.decorators import login_required
from .models import SubscriptionLog
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse



@login_required
def list_subscriptions(request):
    subscriptions = Subscription.objects.all()
    return render(request, "member/list_subscriptions.html", {"subscriptions": subscriptions})
@login_required
def subscription_success(request):
    return render(request, "member/subscription_success.html")


client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

@login_required
def subscribe_to_plan(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id)
    member_profile = MemberProfile.objects.get(user=request.user)

    if request.method == "POST":
        try:
            # Step 1: Create a Razorpay Order
            order_amount = int(subscription.price * 100)  # Razorpay expects amount in paise
            order_currency = "INR"
            order_receipt = f"order_rcptid_{subscription.id}"
            razorpay_order = client.order.create(
                {
                    "amount": order_amount,
                    "currency": order_currency,
                    "receipt": order_receipt,
                }
            )
            print("haii")

            # Step 2: Save the order details in SubscriptionLog
            start_date = timezone.now()
            end_date = start_date + timezone.timedelta(days=subscription.time_period)
            SubscriptionLog.objects.create(
                member=member_profile,
                subscription=subscription,
                start_date=start_date,
                end_date=end_date,
                payment_status="Completed",
                payment_id=razorpay_order["id"],
                status = True,
            )
            print("hello")


            # Step 3: Render the payment page
            return render(
                request,
                "member/payment_page.html",
                {
                    "razorpay_key_id": settings.RAZOR_KEY_ID,
                    "order_id": razorpay_order["id"],
                    "amount": order_amount,
                    "subscription": subscription,
                },
            )
        except Exception as e:
            # Log the error (optional) and redirect to the error page
            print(f"Error occurred: {e}")
            return redirect("home")  # Replace 'error_page' with the name of your error page's URL

    # Render the subscription selection page for GET requests
    return render(request, "member/subscribe_to_plan.html", {"subscription": subscription})


@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        try:
            # Step 1: Get payment details from the request
            payment_id = request.POST.get("razorpay_payment_id")
            order_id = request.POST.get("razorpay_order_id")
            signature = request.POST.get("razorpay_signature")

            # Step 2: Verify the payment signature
            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            params_dict = {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }

            # Razorpay utility to verify the payment signature
            client.utility.verify_payment_signature(params_dict)

            # Step 3: Update the payment status in the database
            subscription_log = SubscriptionLog.objects.get(payment_id=order_id)
            subscription_log.payment_status = "Completed"
            subscription_log.status = True
            subscription_log.save()

            # Step 4: Redirect to a success page
            return redirect("subscription_success")

        except razorpay.errors.SignatureVerificationError as e:
            # Log error and redirect to an error page
            print(f"Signature verification failed: {e}")
            return JsonResponse({"status": "failure", "reason": "Invalid signature"}, status=400)

        except Exception as e:
            # Handle other unexpected errors
            print(f"Error occurred: {e}")
            return JsonResponse({"status": "failure", "reason": "Payment verification failed"}, status=400)
    else:
        return JsonResponse({"status": "failure", "reason": "Invalid request method"}, status=405)
