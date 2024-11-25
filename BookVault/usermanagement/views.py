from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import qrcode
from io import BytesIO

from book.models import Author,Genre,Book,Tag
from .models import User, Address, MemberProfile, Subscription
from django.contrib.auth import authenticate, login, logout

# Create your views here.
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


    return render(request, 'member/add_subscription.html')
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
            login(request, user)
            
            # Redirect based on the user role
            if user.role == 'Admin':
                return redirect('admin_dashboard')  # Replace with your Admin dashboard URL
            elif user.role == 'Librarian':
                return redirect('librarian_dashboard')  # Replace with your Librarian dashboard URL
            elif user.role == 'Member':
                return redirect('home')  # Replace with your Member dashboard URL
            else:
                return redirect('home')  # Default fallback
        else:
            messages.error(request, 'Invalid email or password')
            return redirect('login')  # Replace with the URL name of your login page

    return render(request, 'client/login.html')



def admin_dashboard(request):
    return render(request, 'client/admin_dashboard.html')

def librarian_dashboard(request):
    return render(request, 'client/librarian_dashboard.html')

def member_dashboard(request):
    return render(request, 'client/member_dashboard.html')

def admindashboard(request):
    return render(request, 'admin/index.html')
def custom_logout(request):
    # Log out the user
    logout(request)
    
    # Redirect to the desired URL
    return redirect('http://127.0.0.1:8000/')

@login_required
def profile_view(request):
    # Fetch the logged-in user and their profile
    user = request.user  # Automatically gets the current logged-in user
    member_profile = MemberProfile.objects.get(user=user)  # Get associated profile

    # Pass data to template
    return render(request, "client/profile.html", {
        'user': user,
        'member_profile': member_profile,
    })


def generate_qr_code(request):
    user = request.user  # Assuming you're using the logged-in user
    user_data = f"Name: {user.name}\nEmail: {user.email}\nPhone: {user.phone}\nAddress: {user.address}\nGender: {user.gender}\nRole: {user.role}"

    # Generate QR code from user data
    qr = qrcode.make(user_data)
    
    # Create a BytesIO stream to save the QR code image in memory
    qr_image = BytesIO()
    qr.save(qr_image, 'PNG')
    qr_image.seek(0)
    
    # Create an HTTP response with the QR code image
    return HttpResponse(qr_image, content_type='image/png')