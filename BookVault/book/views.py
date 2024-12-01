from datetime import timedelta
from django.shortcuts import render,redirect,get_object_or_404
from django.db.models import Q
from analytics.views import create_notification
from usermanagement.models import BookIssueTransaction, MemberProfile, User,BookReservation
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
from django.utils.timezone import now


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


def librairianlost_book(request):
    issue = BookIssueTransaction.objects.filter(reportlostbook=True)
    print(issue)
    return render(request, 'libriarian/librairianlost_book.html', {'issue': issue})


def librairianreturn_book(request):
    returnbook = BookIssueTransaction.objects.filter(bookreturn=True)
    print(returnbook)
    return render(request, 'libriarian/return_book.html', {'returnbook': returnbook})


@login_required
def userviewprofile(request):
    issue = BookIssueTransaction.objects.filter(user=request.user)
    reserve = BookReservation.objects.filter(user=request.user)
    context = {
        'issue': issue,
        'reserve': reserve,
        'today': now().date(),  
    }
    return render(request, 'client/userviewprofile.html', context)


def approve_book_request(request, transaction_id):
    transaction = get_object_or_404(BookIssueTransaction, id=transaction_id)
    member_profile = get_object_or_404(MemberProfile, user=transaction.user)
    borrowing_limit = member_profile.borrowing_limit   
    print(f"Transaction ID: {transaction_id}")
    print(f"User: {transaction.user.name}, Borrowing Limit: {borrowing_limit}, status: {transaction.status}")
    if transaction.status == 'Requested':
        transaction.status = 'ISSUED'
        transaction.issue_date = timezone.now() 
        transaction.issuedby = LibrarianProfile.objects.get(user=request.user)
        print(f"User: {transaction.issuedby.user.name}, Borrowing Limit: {borrowing_limit}")
        transaction.save()
        return redirect('issue_book')
    return redirect('issue_book')  


def approve_lostbook_request(request, transaction_id):
    transaction = get_object_or_404(BookIssueTransaction, id=transaction_id)
    if transaction.status == 'ISSUED':
        transaction.status = 'LOST'
        transaction.reportlostbook = None
        transaction.penalties = 500.0
        transaction.save()
        return redirect('librairianlost_book')
    return redirect('librairianlost_book')  


def approve_bookreturn_request(request, transaction_id):
    transaction = get_object_or_404(BookIssueTransaction, id=transaction_id)
    if transaction.bookreturn:
        if request.method == 'POST':
            new_status = request.POST.get('status')
            if new_status in ['DAMAGED',  'RETURNED']:
                transaction.status = new_status
                transaction.bookreturn = None
                if new_status == 'DAMAGED':
                    transaction.penalties = 250.0
                    create_notification(
                        transaction.user,
                        f"Your book '{transaction.book.title}' has been marked as DAMAGED. A penalty of $250 has been applied."
                    )
                else:
                    transaction.penalties = 0.0  
                    book = transaction.book
                    book.available_copies += 1 
                    book.save()
                    create_notification(
                        transaction.user,
                        f"Your book '{transaction.book.title}' has been successfully returned. Thank you!"
                    )
                transaction.save()
                messages.success(request, "Book return processed successfully.")
                return redirect('return_book') 
            else:
                messages.error(request, "Invalid status selected.")
        else:
            return render(request, 'libriarian/approve_return.html', {'transaction': transaction})
    messages.error(request, "This book has not been marked for return.")
    return redirect('issue_book')


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
        tags_ids = request.POST.getlist('tags')  
        related_titles_ids = request.POST.getlist('related_titles')  
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
            tags = Tag.objects.filter(id__in=tags_ids)
            book.tags.set(tags)
            related_books = Book.objects.filter(id__in=related_titles_ids)
            book.related_titles.set(related_books)
            messages.success(request, "Book added successfully!")
            return redirect('add_book')  
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
        isbn = request.POST.get('isbn')
        title = request.POST.get('title')
        author_id = request.POST.get('author')  
        publisher = request.POST.get('publisher')
        publication_year = request.POST.get('publication_year')
        language = request.POST.get('language')
        genre_id = request.POST.get('genre') 
        description = request.POST.get('description')
        total_copies = int(request.POST.get('total_copies', 1))
        available_copies = book.total_copies  
        cover_image = request.FILES.get('cover_image')
        print("Cover Image:", request.FILES.get('cover_image'))
        if cover_image:
            book.cover_image = cover_image
        book.isbn = isbn
        book.title = title
        book.author_id = author_id  
        book.publisher = publisher
        book.publication_year = publication_year
        book.language = language
        book.genre_id = genre_id  
        book.description = description
        book.total_copies = total_copies
        book.available_copies = available_copies
        book.save()
        return redirect('book_list')  
    return render(request, 'libriarian/edit_book.html', {'book': book})


def remove_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.availability = 'removed'
    book.save()
    return redirect('book_list')  


def generate_barcode(data):
    print(data)
    buffer = BytesIO()
    writer = ImageWriter()
    sanitized_data = "".join(c if c.isalnum() or c in " |:,-" else "_" for c in data)  # Clean up data
    Code128(sanitized_data, writer=writer).write(buffer, options={"write_text": False})
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def viewbooks(request):
    query = request.GET.get('q', '')  
    availability = request.GET.get('availability', '') 
    genre = request.GET.get('genre', '')  
    year = request.GET.get('year', '')  
    language = request.GET.get('language', '')  
    books = Book.objects.exclude(availability='removed')  
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__first_name__icontains=query) |
            Q(author__last_name__icontains=query) |
            Q(isbn__icontains=query) |
            Q(tags__name__icontains=query) |
            Q(description__icontains=query)
        ).distinct()
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
    has_subscription = member_profile.subscription  
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
    transactions = BookIssueTransaction.objects.filter(user=request.user)
    return render(request, 'client/book_transaction_list.html', {'transactions': transactions})


def tag_list(request):
    tags = Tag.objects.all() 
    return render(request, 'libriarian/tag_list.html', {'tags': tags})


def genre_list(request):
    genres = Genre.objects.all()  
    return render(request, 'libriarian/genre_list.html', {'genres': genres})


def author_list(request):
    authors = Author.objects.all()  
    return render(request, 'libriarian/author_list.html', {'authors': authors})


def genre_categorization(request):
    genres = Genre.objects.all() 
    return render(request, 'client/genre_categorization.html', {'genres': genres})


def books_by_genre(request, genre_id):
    genre = get_object_or_404(Genre, id=genre_id)  
    books = Book.objects.filter(genre=genre) 
    return render(request, 'client/books_by_genre.html', {'genre': genre, 'books': books})


def tag_categorization(request):
    tags = Tag.objects.all()  
    return render(request, 'client/tag_categorization.html', {'tags': tags})


def books_by_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    books = Book.objects.filter(tags=tag) 
    return render(request, 'client/books_by_tag.html', {'tag': tag, 'books': books})


def author_categorization(request):
    authors = Author.objects.all()
    return render(request, 'client/author_categorization.html', {'authors': authors})


def books_by_author(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    books = Book.objects.filter(author=author)
    return render(request, 'client/books_by_author.html', {'author': author, 'books': books})


def tagadmin_list(request):
    tags = Tag.objects.all()  
    return render(request, 'admindashboard/tagadmin_list.html', {'tags': tags})


def genreadmin_list(request):
    genres = Genre.objects.all() 
    return render(request, 'admindashboard/genreadmin_list.html', {'genres': genres})


def authoradmin_list(request):
    authors = Author.objects.all()  
    return render(request, 'admindashboard/authoradmin_list.html', {'authors': authors})


def bookadmin_list(request):
    books = Book.objects.all()
    return render(request, 'admindashboard/bookadmin_list.html', {'books': books})



