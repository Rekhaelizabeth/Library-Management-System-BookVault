from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
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

# Create your views here.
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
    # Get the total number of entries in each model with status=True
    author_count = Author.objects.filter(status=True).count()
    genre_count = Genre.objects.filter(status=True).count()
    book_count = Book.objects.filter(status=False).count()
    tag_count = Tag.objects.filter(status=True).count()

    # Prepare the context to pass to the template
    context = {
        'author_count': author_count,
        'genre_count': genre_count,
        'book_count': book_count,
        'tag_count': tag_count,
    }

    return render(request, 'client/index.html', context)
def add_subscription(request):
    if request.user.role != "Admin":
        return redirect("error403")# If not, raise PermissionDenied
    if request.method == "POST":
        plan_name = request.POST.get("plan_name")
        price = request.POST.get("price")
        time_period = request.POST.get("time_period")
        book_reservation_count = request.POST.get("book_reservation_count")
        issue_book_count = request.POST.get("issue_book_count")
        external_library_access = request.POST.get("external_library_access") == "True"

        # Create a new Subscription object
        Subscription.objects.create(
            plan_name=plan_name,
            price=price,
            time_period=time_period,
            book_reservation_count=book_reservation_count,
            issue_book_count=issue_book_count,
            external_library_access=external_library_access,
        )

        messages.success(request, "Subscription plan added successfully!")
        return redirect("add_subscription")  # Redirect to the same page or another


    return render(request, 'admindashboard/add_subscription.html')
# def login(request):
#     return render(request, 'client/login.html')

def register_librarian(request):
    if request.method == "POST":
        # Fetch data from the form
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
        notifications_preferences = request.POST.get("iAgree") == "on"  # Checkbox value

        # Save the address
        address = Address.objects.create(
            addressline=addressline,
            city=city,
            state=state,
            country=country,
            postal_code=postal_code,
        )

        # Save the user
        try:
            user = User.objects.create(
                name=name,
                email=email,
                phone=phone,
                address=address,
                role="Librarian",
                notifications_preferences=notifications_preferences,
            )
            user.set_password(password)  # Hash the password
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
        notifications_preferences = request.POST.get("iAgree") == "on"  # Checkbox value

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

        # Create the Address instance
        address = Address.objects.create(
            addressline=addressline,
            city=city,
            state=state,
            country=country,
            postal_code=postal_code,
        )

        # Create the User instance
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

        # Calculate membership expiry date (1 year from today)
        # membership_expiry = datetime.now().date() + timedelta(days=365)

        # Create the MemberProfile instance
        MemberProfile.objects.create(
            user=user,
            membership_type=membership_type,
            # membership_expiry=membership_expiry,
        )
       
        # return HttpResponse("Member registered successfully!")
        return redirect('login')
    return render(request, 'client/register_membercategory.html')



def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate the user using the email and password
        user = authenticate(request, email=email, password=password)

        if user is not None:
            if not user.is_active:
                # User is not active; display a message
                messages.error(request, "Your account is not approved by the librarian yet.")
                return redirect('login')  # Redirect back to the login page
            login(request, user)
            
            # Redirect based on the user role
            if user.role == 'Admin':
                return redirect('admindashboard')  # Replace with your Admin dashboard URL
            elif user.role == 'Librarian':
                return redirect('librarian_dashboard')  # Replace with your Librarian dashboard URL
            elif user.role == 'Member':
                return redirect('home')  # Replace with your Member dashboard URL
            else:
                return redirect('home')  # Default fallback
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('login')  # Replace with the URL name of your login page

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
    # Log out the user
    logout(request)
    
    # Redirect to the desired URL
    return redirect('http://127.0.0.1:8000/')
def access_denied(request):
    return render(request, 'client/access_denied.html', status=403)
from datetime import date

@login_required
def profile(request):
    # Fetch the logged-in user and their profile
    user = request.user  # Automatically gets the current logged-in user
    if user.role != "Member":
        raise PermissionDenied  # If not, raise PermissionDenied
    member_profile = MemberProfile.objects.get(user=user)  # Get associated profile
    address = user.address  # Assuming the address is a related model to user

    # Get the active subscription for the user
    subscription_log = MemberSubscriptionLog.objects.filter(member=user).last()  # Get the last subscription log

    # Check if the subscription is active (not expired)
    is_active_subscription = subscription_log and subscription_log.end_date >= date.today()

    # Pass data to template
    return render(request, "client/profile.html", {
        'user': user,
        'member_profile': member_profile,
        'address': address,
        'subscription_log': subscription_log,
        'is_active_subscription': is_active_subscription,  # Pass this flag to the template
    })
def calculate_days_left(subscription_log):
    if subscription_log and subscription_log.end_date >= date.today():
        return (subscription_log.end_date - date.today()).days
    return 0
@login_required
def generate_qr_code(request):
    user = request.user  # Get the logged-in user
    address = user.address  # Get address related to the user
    member_profile = MemberProfile.objects.get(user=user)  # Fetch the member profile
    subscription_log = MemberSubscriptionLog.objects.filter(member=user).last()  # Get the last subscription log

    # Check if subscription is active
    is_active_subscription = subscription_log and subscription_log.end_date >= date.today()
    days_left = calculate_days_left(subscription_log)
    # Format user data into a string for QR code
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
    # Generate QR code from the formatted user data
    qr = qrcode.make(user_data)
    
    # Create a BytesIO stream to save the QR code image in memory
    qr_image = BytesIO()
    qr.save(qr_image, 'PNG')
    qr_image.seek(0)
    
    # Return the QR code image as an HTTP response
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
    
    return redirect('viewbooks')  # Redirect to the book list or another page

from django.shortcuts import get_object_or_404, redirect
from django.utils.timezone import now
from django.contrib import messages
from .models import BookIssueTransaction

def return_book(request, transaction_id):
    # Fetch the specific transaction
    transaction = get_object_or_404(BookIssueTransaction, id=transaction_id)
    
    if transaction.status == 'ISSUED':  # Ensure the book is issued
        transaction.return_date = now().date()  # Set the return date to today
        # transaction.status = 'RETURNED'  # Update status
        transaction.bookreturn = True
        
        # Calculate penalties if applicable
        if transaction.return_date > transaction.due_date:
            overdue_days = (transaction.return_date - transaction.due_date).days
            transaction.penalties = overdue_days * 1.5  # Example penalty: $1.5/day
        
        transaction.save()  # Save changes
        
        messages.success(request, f"The book '{transaction.book.title}' has been successfully returned.")
    else:
        messages.error(request, "This book cannot be returned.")
    
    return redirect('userviewprofile')  # Redirect to the borrowing list page

#lost_book

def lost_book(request, transaction_id):
    # Fetch the specific transaction
    transaction = get_object_or_404(BookIssueTransaction, id=transaction_id)
    
    if transaction.status == 'ISSUED':  # Ensure the book is issued

        transaction.reportlostbook = True
        transaction.penalties = 500
        
        transaction.save()  
    else:
        messages.error(request, "This book cannot be returned.")
    
    return redirect('userviewprofile')  # Redirect to the borrowing list page
def reserve_book(request, book_id):
    if request.user.role != "Member":
       return redirect("error403")
    # Fetch the book instance
    book = get_object_or_404(Book, id=book_id)

    # Check if the book is reservable
    if book.available_copies == 0 and book.reserved_copies < book.total_copies:
        # Create a reservation entry
        reservation, created = BookReservation.objects.get_or_create(
            book=book,
            user=request.user,  # The currently logged-in user
            defaults={'status': 'pending'}
        )

        if created:
            # Increment the reserved copies count in the Book model
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

    return redirect('book_list')  # Redirect to the book list page


@login_required
def book_description(request, book_id):
    if request.user.role != "Member":
        return redirect("error403")
    book = get_object_or_404(Book, id=book_id)
    user_has_borrowed = BookIssueTransaction.objects.filter(book=book, user=request.user).exists()

    related_books = book.related_titles.all()

    if request.method == "POST" and user_has_borrowed:
        # Get the rating and review from the form
        rating = request.POST.get('rating')
        review_text = request.POST.get('review')

        # Ensure the user has not already reviewed this book
        existing_review = Reviews.objects.filter(book=book, user=request.user).first()
        if existing_review:
            messages.warning(request, "You have already reviewed this book.")
        else:
            # Save the review and rating
            Reviews.objects.create(
                book=book,
                user=request.user,
                rating=rating,
                review_text=review_text
                
            )
            messages.success(request, "Your review has been submitted successfully.")

        return redirect('book_description', book_id=book_id)

    # Fetch all reviews for the book
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
    # Fetch all member profiles along with their related user, subscription, and address details
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
# Enable debug logging for boto3 and botocore
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
from .models import MemberProfile  # Import your model for MemberProfile

def upload_membership_card(request):
    if request.method == 'POST':
        try:
            # Ensure the user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse({"error": "User is not authenticated"}, status=401)
            
            # Extract the image from the POST request
            data = json.loads(request.body)
            image_data = data['image']
            
            # Retrieve member_profile from the logged-in user
            try:
                member_profile = MemberProfile.objects.get(user=request.user)
            except ObjectDoesNotExist:
                return JsonResponse({"error": "MemberProfile not found"}, status=404)
            
            member_id = member_profile.id  # Get the member_id from the MemberProfile
            
            # Decode the base64 image
            image_data = image_data.split(',')[1]  # Remove the base64 header part
            img = Image.open(BytesIO(base64.b64decode(image_data)))
            
            # Initialize S3 client with Signature Version 4 enabled
            s3_client = boto3.client('s3', 
                                     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                     region_name=settings.AWS_REGION,
                                     config=botocore.client.Config(signature_version='s3v4'))  # Signature Version 4

            # Generate a unique file name for the image
            folder_name = "membershipcards"  # The folder inside the bucket
            file_name = f"{folder_name}/{member_id}.png"
            buffer = BytesIO()
            img.save(buffer, "PNG")
            buffer.seek(0)
            
            # Upload the image to S3
            s3_client.upload_fileobj(buffer, settings.AWS_STORAGE_BUCKET_NAME, file_name, ExtraArgs={'ACL': 'public-read'})
            
            # Get the image URL
            image_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_name}"

            # Save the image URL to the MemberProfile model associated with the logged-in user
            member_profile.membership_card_url = image_url  # Assuming the field is 'membership_card_url'
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
            return redirect('home')  # Redirect to a success page or back to the form

    return render(request, 'client/suggestions.html')




#forgot password
# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib import messages
from django.template.loader import render_to_string


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            # User = get_user_model()
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(str(user.pk).encode())

            # Send reset email
            reset_link = f'http://{get_current_site(request).domain}/reset-password/{uid}/{token}/'
            message = render_to_string('client/password_reset_email.html', {
                'user': user,
                'reset_link': reset_link,
            })
            send_mail(
                'Password Reset Request',
                message,
                'bookvault3@gmail.com',
                [email],
                fail_silently=False,
            )

            # Success message and redirect to login page
            messages.success(request, "We've sent you an email with a link to reset your password. Please check your inbox.")
            return redirect('login')  # Redirect to login page
        except User.DoesNotExist:
            messages.error(request, "No user found with this email.")
            return redirect('forgot_password')
    return render(request, 'client/forgot_password.html')


# from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.forms import SetPasswordForm
from django.shortcuts import render, redirect

def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        # user = get_user_model().objects.get(pk=uid)
        
        # Check if the token is valid
        # if default_token_generator.check_token(user, token):
        #     if request.method == 'POST':
        #         form = SetPasswordForm(user, request.POST)
        #         if form.is_valid():
        #             form.save()
        #             messages.success(request, "Your password has been reset successfully.")
        #             return redirect('login')  # Redirect to login page after password reset
        #     else:
        #         form = SetPasswordForm(user)
        #     return render(request, 'client/reset_password.html', {'form': form})

        # else:
        #     messages.error(request, "This link has expired or is invalid.")
        return redirect('forgot_password')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, "Invalid reset link.")
        return redirect('forgot_password')
    

from django.shortcuts import render, get_object_or_404
from .models import User

def librarian_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if not authenticated

    # Ensure the logged-in user is a librarian
    if request.user.role != "Librarian":
        return redirect('home')  # Redirect to home or appropriate page

    # Fetch the librarian's details
    librarian = request.user

    return render(request, 'libriarian/libriarianprofile.html', {
        'librarian': librarian,
    })
