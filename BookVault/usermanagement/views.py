from django.shortcuts import get_object_or_404, render, redirect
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import qrcode
from django.core.exceptions import PermissionDenied
from io import BytesIO
from book.models import Author,Genre,Book,Tag
from .models import BookIssueTransaction, BookReservation, MemberSubscriptionLog, User, Address, MemberProfile, Subscription , Reviews,Suggestion
from django.contrib.auth import authenticate, login, logout
from datetime import date
from django.shortcuts import render, get_object_or_404
from .models import User


from django.shortcuts import get_object_or_404, redirect
from django.utils.timezone import now
from .models import BookIssueTransaction


def about(request):
    return render(request, 'client/about.html')


def error403(request):
    return render(request, 'error403.html')


def baseindex(request):
    return render(request, 'admindasboard/baseindex.html')


def librarianbaseindex(request):
    return render(request, 'librairian/baseindex.html')


def baseindexmember(request):
    return render(request, 'client/baseindexmember.html')


def home(request):
    author_count = Author.objects.filter(status=True).count()
    genre_count = Genre.objects.filter(status=True).count()
    book_count = Book.objects.filter(status=False).count()
    tag_count = Tag.objects.filter(status=True).count()
    context = {
        'author_count': author_count,
        'genre_count': genre_count,
        'book_count': book_count,
        'tag_count': tag_count,
    }
    return render(request, 'client/index.html', context)


def add_subscription(request):
    if request.user.role != "Admin":
        return redirect("error403")
    if request.method == "POST":
        plan_name = request.POST.get("plan_name")
        price = request.POST.get("price")
        time_period = request.POST.get("time_period")
        book_reservation_count = request.POST.get("book_reservation_count")
        issue_book_count = request.POST.get("issue_book_count")
        external_library_access = request.POST.get("external_library_access") == "True"
        Subscription.objects.create(
            plan_name=plan_name,
            price=price,
            time_period=time_period,
            book_reservation_count=book_reservation_count,
            issue_book_count=issue_book_count,
            external_library_access=external_library_access,
        )
        messages.success(request, "Subscription plan added successfully!")
        return redirect("add_subscription")  
    return render(request, 'admindashboard/add_subscription.html')


def register_librarian(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        addressline = request.POST.get("addressline")
        city = request.POST.get("city")
        state = request.POST.get("state")
        country = request.POST.get("country")
        gender = request.POST.get("gender")
        postal_code = request.POST.get("postal_code")
        password = request.POST.get("password")
        notifications_preferences = request.POST.get("iAgree") == "on"  
        address = Address.objects.create(
            addressline=addressline,
            city=city,
            state=state,
            country=country,
            postal_code=postal_code,
        )
        try:
            user = User.objects.create(
                name=name,
                email=email,
                phone=phone,
                address=address,
                role="Librarian",
                notifications_preferences=notifications_preferences,
            )
            user.set_password(password)  
            user.save()
            messages.success(request, "User registered successfully!")
            return redirect("home")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    return render(request, 'client/register_librarian.html')


def register_membercategory(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone = request.POST.get("phone")
        addressline = request.POST.get("addressline")
        city = request.POST.get("city")
        state = request.POST.get("state")
        country = request.POST.get("country")
        gender = request.POST.get("gender")
        postal_code = request.POST.get("postal_code")
        membership_type = request.POST.get("membership_type")
        notifications_preferences = request.POST.get("iAgree") == "on"  
        print("Name:", name)
        print("Email:", email)
        print("Password:", password)
        print("Phone:", phone)
        print("Address Line:", addressline)
        print("City:", city)
        print("State:", state)
        print("Country:", country)
        print("Postal Code:", postal_code)
        print("Membership Type:", membership_type)
        address = Address.objects.create(
            addressline=addressline,
            city=city,
            state=state,
            country=country,
            postal_code=postal_code,
        )
        user = User.objects.create_user(
            name=name,
            email=email,
            password=password,
            phone=phone,
            address=address,
            gender=gender,
            role="Member",
            is_active=False,
            notifications_preferences=notifications_preferences,
        )
        MemberProfile.objects.create(
            user=user,
            membership_type=membership_type,
        )
        return redirect('login')
    return render(request, 'client/register_membercategory.html')


def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            if not user.is_active:
                messages.error(request, "Your account is not approved by the librarian yet.")
                return redirect('login')  
            login(request, user)
            if user.role == 'Admin':
                return redirect('admindashboard')  
            elif user.role == 'Librarian':
                return redirect('librarian_dashboard') 
            elif user.role == 'Member':
                return redirect('home')  
            else:
                return redirect('home')  
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('login')  
    return render(request, 'client/login.html')


def admin_dashboard(request):
    return render(request, 'client/admin_dashboard.html')


def librarian_dashboard(request):
    return render(request, 'libriarian/index.html')


def member_dashboard(request):
    return render(request, 'client/member_dashboard.html')


def admindashboard(request):
    return render(request, 'admindashboard/index.html')


def custom_logout(request):
    logout(request)
    return redirect('http://127.0.0.1:8000/')


def access_denied(request):
    return render(request, 'client/access_denied.html', status=403)


@login_required
def profile(request):   
    user = request.user  
    if user.role != "Member":
        raise PermissionDenied  
    member_profile = MemberProfile.objects.get(user=user)  
    address = user.address  
    subscription_log = MemberSubscriptionLog.objects.filter(member=user).last()  
    is_active_subscription = subscription_log and subscription_log.end_date >= date.today()
    return render(request, "client/profile.html", {
        'user': user,
        'member_profile': member_profile,
        'address': address,
        'subscription_log': subscription_log,
        'is_active_subscription': is_active_subscription,  
    })


def calculate_days_left(subscription_log):
    if subscription_log and subscription_log.end_date >= date.today():
        return (subscription_log.end_date - date.today()).days
    return 0


@login_required
def generate_qr_code(request):
    user = request.user  
    address = user.address  
    member_profile = MemberProfile.objects.get(user=user)  
    subscription_log = MemberSubscriptionLog.objects.filter(member=user).last()  
    is_active_subscription = subscription_log and subscription_log.end_date >= date.today()
    days_left = calculate_days_left(subscription_log)
    user_data = f"""
    Name: {user.name}
    Email: {user.email}
    Phone: {user.phone}
    Gender: {user.gender}
    Role: {user.role}
    Status: {'Active' if user.is_active else 'Inactive'}
    Date Joined: {user.date_joined.strftime('%F')}   
    Address:
    Street: {address.addressline}
    City: {address.city}
    State: {address.state}
    Country: {address.country}
    Postal Code: {address.postal_code}
    Membership:
    Membership Type: {member_profile.membership_type}
    Borrowing Limit: {member_profile.borrowing_limit}
    Outstanding Fines: ${member_profile.outstanding_fines}
    Reserved Books Count: {member_profile.reserved_books_count}
    Subscription:
    Plan Name: {subscription_log.subscription.plan_name }
    Price: ${subscription_log.subscription.price }
    Period: {subscription_log.subscription.time_period } days
    External Library Access: {'Yes' if subscription_log and subscription_log.subscription.external_library_access else 'No'}
    Active Subscription: {'Yes' if is_active_subscription else 'No'}
    Days Left: {days_left} days
    """
    print("qr now data")
    print(user_data)
    qr = qrcode.make(user_data)
    qr_image = BytesIO()
    qr.save(qr_image, 'PNG')
    qr_image.seek(0)
    return HttpResponse(qr_image, content_type='image/png')


def borrow_book(request, book_id):
    if request.user.role != "Member":
        return redirect("error403")
    book = get_object_or_404(Book, id=book_id)
    user = request.user
    member_profile = get_object_or_404(MemberProfile, user=user)
    if book.available_copies > 0:
        transaction = BookIssueTransaction.objects.create(
            book=book,
            user=user,
            status='Requested',
        )
        book.available_copies -= 1
        book.availability = 'checked_out'
        book.save()
        print("Book issued successfully.")
    else:
        print("No available copies left.")
    return redirect('viewbooks')  


def return_book(request, transaction_id):
    transaction = get_object_or_404(BookIssueTransaction, id=transaction_id)
    if transaction.status == 'ISSUED':  
        transaction.return_date = now().date()  
        transaction.bookreturn = True
        if transaction.return_date > transaction.due_date:
            overdue_days = (transaction.return_date - transaction.due_date).days
            transaction.penalties = overdue_days * 1.5  
        transaction.save()  
        messages.success(request, f"The book '{transaction.book.title}' has been successfully returned.")
    else:
        messages.error(request, "This book cannot be returned.")
    return redirect('userviewprofile')  


def lost_book(request, transaction_id):
    transaction = get_object_or_404(BookIssueTransaction, id=transaction_id)
    if transaction.status == 'ISSUED':  
        transaction.reportlostbook = True
        transaction.penalties = 500
        transaction.save()  
    else:
        messages.error(request, "This book cannot be returned.")
    return redirect('userviewprofile')  


def reserve_book(request, book_id):
    if request.user.role != "Member":
       return redirect("error403")
    book = get_object_or_404(Book, id=book_id)
    if book.available_copies == 0 and book.reserved_copies < book.total_copies:
        reservation, created = BookReservation.objects.get_or_create(
            book=book,
            user=request.user,  
            defaults={'status': 'pending'}
        )
        if created:
            book.reserved_copies += 1
            book.save()
            member_profile = MemberProfile.objects.all()
            print(member_profile) 
            print("Done")
            messages.success(request, f"Book '{book.title}' has been reserved successfully!")
        else:
            messages.info(request, f"You have already reserved the book '{book.title}'.")
    else:
        messages.error(request, f"The book '{book.title}' cannot be reserved at the moment.")
    return redirect('book_list')  


@login_required
def book_description(request, book_id):
    if request.user.role != "Member":
        return redirect("error403")
    book = get_object_or_404(Book, id=book_id)
    user_has_borrowed = BookIssueTransaction.objects.filter(book=book, user=request.user).exists()
    related_books = book.related_titles.all()
    if request.method == "POST" and user_has_borrowed:
        rating = request.POST.get('rating')
        review_text = request.POST.get('review')
        existing_review = Reviews.objects.filter(book=book, user=request.user).first()
        if existing_review:
            messages.warning(request, "You have already reviewed this book.")
        else:
            Reviews.objects.create(
                book=book,
                user=request.user,
                rating=rating,
                review_text=review_text                
            )
            messages.success(request, "Your review has been submitted successfully.")
        return redirect('book_description', book_id=book_id)
    reviews = Reviews.objects.filter(book=book).order_by('-created_at')
    return render(request, 'client/bookdescription.html', {
        'book': book,
        'reviews': reviews,
        'user_has_borrowed': user_has_borrowed,
        'related_books': related_books
    })


def memberview(request):
    if request.user.role != "Admin":
        return redirect("error403")
    members = MemberProfile.objects.select_related(
        'user', 'subscription', 'user__address'
    ).all()   
    return render(request, 'admindashboard/memberview.html', {'members': members})


from django.http import JsonResponse
import boto3
from django.conf import settings
import base64
from io import BytesIO
from PIL import Image
import json
import uuid
import logging
import boto3
import json
import base64
import uuid
from io import BytesIO
from PIL import Image
from django.http import JsonResponse
from django.conf import settings
import botocore
boto3.set_stream_logger(name='botocore', level=logging.DEBUG)
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from PIL import Image
from io import BytesIO
import base64
import uuid
import json
import logging
import boto3
import botocore
from .models import MemberProfile  


def upload_membership_card(request):
    if request.method == 'POST':
        try:
            if not request.user.is_authenticated:
                return JsonResponse({"error": "User is not authenticated"}, status=401)
            data = json.loads(request.body)
            image_data = data['image']
            try:
                member_profile = MemberProfile.objects.get(user=request.user)
            except ObjectDoesNotExist:
                return JsonResponse({"error": "MemberProfile not found"}, status=404)
            member_id = member_profile.id  
            image_data = image_data.split(',')[1]  
            img = Image.open(BytesIO(base64.b64decode(image_data)))
            s3_client = boto3.client('s3', 
                                     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                     region_name=settings.AWS_REGION,
                                     config=botocore.client.Config(signature_version='s3v4')) 
            folder_name = "membershipcards"  
            file_name = f"{folder_name}/{member_id}.png"
            buffer = BytesIO()
            img.save(buffer, "PNG")
            buffer.seek(0)
            s3_client.upload_fileobj(buffer, settings.AWS_STORAGE_BUCKET_NAME, file_name, ExtraArgs={'ACL': 'public-read'})
            image_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_name}"
            member_profile.membership_card_url = image_url  
            member_profile.save()

            return JsonResponse({"imageUrl": image_url})
        except Exception as e:
            logging.error(f"Error occurred while uploading membership card: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def suggestion_view(request):
    if request.method == "POST":
        suggestion_text = request.POST.get('suggestion_text')
        if suggestion_text:
            Suggestion.objects.create(user=request.user, suggestion_text=suggestion_text)
            return redirect('home')  

    return render(request, 'client/suggestions.html')




def librarian_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')  
    if request.user.role != "Librarian":
        return redirect('home')  
    librarian = request.user
    return render(request, 'libriarian/libriarianprofile.html', {
        'librarian': librarian,
    })
