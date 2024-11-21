from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime, timedelta
from django.http import HttpResponse
from .models import User, Address, MemberProfile
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def home(request):
    return render(request, 'client/index.html')

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

        return HttpResponse("Member registered successfully!")
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
                return redirect('member_dashboard')  # Replace with your Member dashboard URL
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


