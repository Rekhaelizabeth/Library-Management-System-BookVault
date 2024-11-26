from django.shortcuts import render,redirect
from django.db.models import Q
from usermanagement.models import BookIssueTransaction
from .models import Book
from .models import Author, Genre, Book, Tag
from django.contrib import messages
from barcode import Code128
from barcode.writer import ImageWriter
from io import BytesIO
import base64
from django.forms.models import model_to_dict


def book_list(request):
    books = Book.objects.all()
    return render(request, 'admindashboard/book_list.html', {'books': books})

def add_tag(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Tag.objects.create(name=name)
            messages.success(request, 'Tag added successfully!')
            return redirect('add_tag')
    return render(request, 'admindashboard/add_tag.html')

def add_genre(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Genre.objects.create(name=name)
            messages.success(request, 'Genre added successfully!')
            return redirect('add_genre')
    return render(request, 'admindashboard/add_genre.html')

def add_author(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        bio = request.POST.get('bio')
        if first_name and last_name:
            Author.objects.create(first_name=first_name, last_name=last_name, bio=bio)
            messages.success(request, 'Author added successfully!')
            return redirect('add_author')
    return render(request, 'admindashboard/add_author.html')

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
    return render(request, 'admindashboard/add_book.html', {
        'authors': authors,
        'genres': genres,
        'tags': tags,
        'books': books,
    })

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
    })


def book_transaction_list(request):
    # Fetch all BookIssueTransaction entries
    transactions = BookIssueTransaction.objects.filter(user=request.user)

    # Pass the transactions to the template
    return render(request, 'client/book_transaction_list.html', {'transactions': transactions})