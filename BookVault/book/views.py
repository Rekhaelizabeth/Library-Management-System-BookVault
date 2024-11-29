from datetime import timedelta
from django.shortcuts import render,redirect,get_object_or_404
from django.db.models import Q
from usermanagement.models import BookIssueTransaction, MemberProfile, User
from .models import Book
from .models import Author, Genre, Book, Tag
from django.contrib import messages
from barcode import Code128
from barcode.writer import ImageWriter
from io import BytesIO
import base64
from django.forms.models import model_to_dict
from .models import Book
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from usermanagement.models import LibrarianProfile


def book_list(request):
    books = Book.objects.exclude(availability='removed')
    return render(request, 'libriarian/book_list.html', {'books': books})

def member_list(request):
    user = User.objects.exclude(is_active=True)
    return render(request, 'libriarian/member.html', {'users': user})

def issue_book(request):
    issue = BookIssueTransaction.objects.filter(status='Requested')
    print(issue)
    return render(request, 'libriarian/issue_book.html', {'issue': issue})

def approve_book_request(request, transaction_id):
    transaction = get_object_or_404(BookIssueTransaction, id=transaction_id)
    member_profile = get_object_or_404(MemberProfile, user=transaction.user)
    
    # Get the borrowing limit for that user
    borrowing_limit = member_profile.borrowing_limit
    return_date = timezone.now() + timedelta(days=borrowing_limit)
    print(borrowing_limit)
    print(f"Transaction ID: {transaction_id}")
    print(f"User: {transaction.user.name}, Borrowing Limit: {borrowing_limit}, status: {transaction.status}")
    if transaction.status == 'Requested':
        # Update the status to 'ISSUED'
        transaction.status = 'ISSUED'
        transaction.issue_date = timezone.now() 
        transaction.return_date = return_date
    
        transaction.issuedby = LibrarianProfile.objects.get(user=request.user)
        print(f"User: {transaction.issuedby.user.name}, Borrowing Limit: {borrowing_limit}")
        
    
        transaction.save()
        

        return redirect('issue_book')
    return redirect('issue_book')  # Or show an error message if necess

def approve_member(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    return redirect('member_list')


def add_tag(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Tag.objects.create(name=name)
            messages.success(request, 'Tag added successfully!')
            return redirect('add_tag')
    return render(request, 'libriarian/add_tag.html')

def add_genre(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Genre.objects.create(name=name)
            messages.success(request, 'Genre added successfully!')
            return redirect('add_genre')
    return render(request, 'libriarian/add_genre.html')

def add_author(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        bio = request.POST.get('bio')
        if first_name and last_name:
            Author.objects.create(first_name=first_name, last_name=last_name, bio=bio)
            messages.success(request, 'Author added successfully!')
            return redirect('add_author')
    return render(request, 'libriarian/add_author.html')

def add_book(request):
    if request.method == "POST":
        isbn = request.POST.get('isbn')
        title = request.POST.get('title')
        author_id = request.POST.get('author')
        publisher = request.POST.get('publisher')
        publication_year = request.POST.get('publication_year')
        edition = request.POST.get('edition', None)
        language = request.POST.get('language')
        genre_id = request.POST.get('genre')
        description = request.POST.get('description')
        availability = request.POST.get('availability')
        tags_ids = request.POST.getlist('tags')  # Collect all checked tag IDs
        related_titles_ids = request.POST.getlist('related_titles')  # Collect all related titles IDs
        cover_image = request.FILES.get('cover_image', None)

        try:
            author = Author.objects.get(id=author_id)
            genre = Genre.objects.get(id=genre_id)
            book = Book.objects.create(
                isbn=isbn,
                title=title,
                author=author,
                publisher=publisher,
                publication_year=publication_year,
                edition=edition,
                language=language,
                genre=genre,
                description=description,
                availability=availability,
                cover_image=cover_image,
            )
            # Add tags to the book
            tags = Tag.objects.filter(id__in=tags_ids)
            book.tags.set(tags)
            
            related_books = Book.objects.filter(id__in=related_titles_ids)
            book.related_titles.set(related_books)

            messages.success(request, "Book added successfully!")
            return redirect('add_book')  # Redirect to the same page or another page
        except Exception as e:
            messages.error(request, f"Error adding book: {e}")

    authors = Author.objects.all()
    genres = Genre.objects.all()
    tags = Tag.objects.all()
    books = Book.objects.all()
    return render(request, 'libriarian/add_book.html', {
        'authors': authors,
        'genres': genres,
        'tags': tags,
        'books': books,
    })

def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == "POST":
        # Update the book details
        isbn = request.POST.get('isbn')
        title = request.POST.get('title')
        author_id = request.POST.get('author')  # Assuming author_id is passed
        publisher = request.POST.get('publisher')
        publication_year = request.POST.get('publication_year')
        language = request.POST.get('language')
        genre_id = request.POST.get('genre')  # Assuming genre_id is passed
        description = request.POST.get('description')
        total_copies = int(request.POST.get('total_copies', 1))
        available_copies = book.total_copies  # Reset available copies

        book.isbn = isbn
        book.title = title
        book.author_id = author_id  # Ensure this is a valid Author ID
        book.publisher = publisher
        book.publication_year = publication_year
        book.language = language
        book.genre_id = genre_id  # Ensure this is a valid Genre ID
        book.description = description
        book.total_copies = total_copies
        book.available_copies = available_copies
        
        # Save the updated book instance
        book.save()
        return redirect('book_list')  # Redirect after editing
    return render(request, 'libriarian/edit_book.html', {'book': book})

def remove_book(request, book_id):
    """
    View to set a book's availability to 'Removed'.
    """
    book = get_object_or_404(Book, id=book_id)
    
    # Update the availability status
    book.availability = 'removed'
    book.save()
    
    # Redirect or return a response
   
    
    # For non-AJAX requests, redirect to a book list or detail page
    return redirect('book_list')  # Replace 'book_list' with the appropriate URL name

def inventory(request):
    return render(request, 'book/inventory.html')


def generate_barcode(data):
    print(data)
    buffer = BytesIO()
    writer = ImageWriter()
    sanitized_data = "".join(c if c.isalnum() or c in " |:,-" else "_" for c in data)  # Clean up data
    Code128(sanitized_data, writer=writer).write(buffer, options={"write_text": False})
    # print(base64.b64encode(buffer.getvalue()).decode('utf-8'))
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def viewbooks(request):
    query = request.GET.get('q', '')  # Search query
    availability = request.GET.get('availability', '')  # Availability filter
    genre = request.GET.get('genre', '')  # Genre filter
    year = request.GET.get('year', '')  # Year filter
    language = request.GET.get('language', '')  # Language filter

    books = Book.objects.all()  # Default: fetch all books

    # Apply search query
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__first_name__icontains=query) |
            Q(author__last_name__icontains=query) |
            Q(isbn__icontains=query) |
            Q(tags__name__icontains=query) |
            Q(description__icontains=query)
        ).distinct()

    # Apply filters
    if availability:
        books = books.filter(status=(availability == 'available'))
    if genre:
        books = books.filter(genre__id=genre)
    if year:
        books = books.filter(publication_year=year)
    if language:
        books = books.filter(language__iexact=language)
    for book in books:
        barcode_data = f"Book: {book.id}, Available copies:{book.available_copies}"
        book.barcode = generate_barcode(barcode_data)

    member_profile = get_object_or_404(MemberProfile, user=request.user)
    has_subscription = member_profile.subscription  # Assuming this field exists in MemberProfile

    # Pass filters and books to the template
    genres = Genre.objects.all()
    return render(request, 'client/viewbooks.html', {
        'books': books,
        'query': query,
        'availability': availability,
        'genre': genre,
        'year': year,
        'language': language,
        'genres': genres,
        'has_subscription': has_subscription,
    })


def book_transaction_list(request):
    # Fetch all BookIssueTransaction entries
    transactions = BookIssueTransaction.objects.filter(user=request.user)

    # Pass the transactions to the template
    return render(request, 'client/book_transaction_list.html', {'transactions': transactions})

def tag_list(request):
    tags = Tag.objects.all()  # Retrieve all tags from the database
    return render(request, 'libriarian/tag_list.html', {'tags': tags})

def genre_list(request):
    genres = Genre.objects.all()  # Fetch all genres from the database
    return render(request, 'libriarian/genre_list.html', {'genres': genres})

def author_list(request):
    authors = Author.objects.all()  # Fetch all authors from the database
    return render(request, 'libriarian/author_list.html', {'authors': authors})

# View to display genres as buttons
def genre_categorization(request):
    genres = Genre.objects.all()  # Fetch all genres
    return render(request, 'client/genre_categorization.html', {'genres': genres})

# View to display books under a specific genre
def books_by_genre(request, genre_id):
    genre = get_object_or_404(Genre, id=genre_id)  # Fetch the specific genre
    books = Book.objects.filter(genre=genre)  # Get books under this genre
    return render(request, 'client/books_by_genre.html', {'genre': genre, 'books': books})


def tag_categorization(request):
    tags = Tag.objects.all()  # Fetch all tags
    return render(request, 'client/tag_categorization.html', {'tags': tags})

def books_by_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    books = Book.objects.filter(tags=tag)  # Fetch all books under the selected tag
    return render(request, 'client/books_by_tag.html', {'tag': tag, 'books': books})


def author_categorization(request):
    """Display a list of all authors with buttons."""
    authors = Author.objects.all()
    return render(request, 'client/author_categorization.html', {'authors': authors})

def books_by_author(request, author_id):
    """Display all books by a specific author."""
    author = get_object_or_404(Author, id=author_id)
    books = Book.objects.filter(author=author)
    return render(request, 'client/books_by_author.html', {'author': author, 'books': books})
