from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from datetime import datetime, timedelta, timezone
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import qrcode
from io import BytesIO
from book.models import Author,Genre,Book,Tag
from .models import BookIssueTransaction, BookReservation, User, Address, MemberProfile, Subscription , Reviews
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def baseindex(request):
    return render(request, 'admindasboard/baseindex.html')

def librarianbaseindex(request):
    return render(request, 'librairian/baseindex.html')

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
                return redirect('admin_dashboard')  # Replace with your Admin dashboard URL
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

@login_required
def profile(request):
    # Fetch the logged-in user and their profile
    user = request.user  # Automatically gets the current logged-in user
    member_profile = MemberProfile.objects.get(user=user)  # Get associated profile
    address = user.address  # Assuming the address is a related model to user

    # Pass data to template
    return render(request, "client/profile.html", {
        'user': user,
        'member_profile': member_profile,
        'address': address,  # Include the address object
    })

def generate_qr_code(request):
    user = request.user  # Assuming you're using the logged-in user
    # Fetch related models
    address = user.address  # Address of the user
    member_profile = MemberProfile.objects.get(user=user)  # MemberProfile of the user
    subscription = member_profile.subscription  # Subscription of the user (if exists)

    # Format the user data into a string
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
    Expiry Date: {member_profile.membership_expiry.strftime('%F')}
    Borrowing Limit: {member_profile.borrowing_limit}
    Outstanding Fines: ${member_profile.outstanding_fines}
    Reserved Books Count: {member_profile.reserved_books_count}
    
    Subscription:
    Plan Name: {subscription.plan_name if subscription else 'None'}
    Price: ${subscription.price if subscription else 'N/A'}
    Period: {subscription.time_period if subscription else 'N/A'} days
    External Library Access: {'Yes' if subscription.external_library_access else 'No'}
    """

    # Generate QR code from user data
    qr = qrcode.make(user_data)
    
    # Create a BytesIO stream to save the QR code image in memory
    qr_image = BytesIO()
    qr.save(qr_image, 'PNG')
    qr_image.seek(0)
    
    # Create an HTTP response with the QR code image
    return HttpResponse(qr_image, content_type='image/png')

def borrow_book(request, book_id):
    print("Haiiii")
    try:
        # Fetch the book by its ID
        book = get_object_or_404(Book, id=book_id)
        
        # Assuming you have a current user and that user can borrow books
        user = request.user
        
        # Fetch the MemberProfile for the current user
        member_profile = get_object_or_404(MemberProfile, user=user)
        
        # Get the borrowing limit for that user
        borrowing_limit = member_profile.borrowing_limit
        return_date = timezone.now() + timedelta(days=borrowing_limit)
        print(borrowing_limit)
        print("helloo")
        print(book)
        print(user)
        # Check if there are available copies of the book
        if book.available_copies > 0:
            # Create an issue transaction
            transaction = BookIssueTransaction.objects.create(
                book=book,
                user=user,
                issue_date=timezone.now(),  # Automatically set issue_date
                return_date=return_date
            )
            
            # Reduce the available copies by 1
            print("hai")
            print(book.available_copies)
            book.available_copies -= 1
            print(book.available_copies)

            
            
            # Optionally, you can set the book status to "checked out"
            book.availability = 'checked_out'
            book.save()

            print("Book issued successfully.")
        else:
            print("No available copies left.")
    
    except Exception as e:
        print(f"Error: {e}")
    
    return redirect('home')  # Redirect to the book list or another page

def reserve_book(request, book_id):
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
    book = get_object_or_404(Book, id=book_id)
    user_has_borrowed = BookIssueTransaction.objects.filter(book=book, user=request.user).exists()

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
    })