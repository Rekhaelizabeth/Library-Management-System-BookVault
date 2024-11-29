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
from .models import BookIssueTransaction, BookReservation, MemberSubscriptionLog, User, Address, MemberProfile, Subscription , Reviews
from django.contrib.auth import authenticate, login, logout

# Create your views here.

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
    
    # Fetch the book by its ID
    book = get_object_or_404(Book, id=book_id)
    
    user = request.user
   
    member_profile = get_object_or_404(MemberProfile, user=user)
    
    # Get the borrowing limit for that user
    borrowing_limit = member_profile.borrowing_limit
    return_date = timezone.now() + timedelta(days=borrowing_limit)
    print(borrowing_limit)
    print("helloo")
    print(book)
    print(user)
    
    if book.available_copies > 0:
        transaction = BookIssueTransaction.objects.create(
            book=book,
            user=user,
            return_date=return_date,
            status='Requested',
            

        )
        
        print("hai")
        print(book.available_copies)
        book.available_copies -= 1
        print(book.available_copies)
        
        book.availability = 'checked_out'
        book.save()

        print("Book issued successfully.")
    else:
        print("No available copies left.")
    
    return redirect('home')  # Redirect to the book list or another page

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