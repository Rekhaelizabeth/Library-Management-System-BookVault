from django.shortcuts import render,redirect
from .models import Book
from .models import Author, Genre, Book, Tag
from django.contrib import messages

def book_list(request):
    books = Book.objects.all()
    return render(request, 'book/book_list.html', {'books': books})

def add_tag(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Tag.objects.create(name=name)
            messages.success(request, 'Tag added successfully!')
            return redirect('add_tag')
    return render(request, 'book/add_tag.html')

def add_genre(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Genre.objects.create(name=name)
            messages.success(request, 'Genre added successfully!')
            return redirect('add_genre')
    return render(request, 'book/add_genre.html')

def add_author(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        bio = request.POST.get('bio')
        if first_name and last_name:
            Author.objects.create(first_name=first_name, last_name=last_name, bio=bio)
            messages.success(request, 'Author added successfully!')
            return redirect('add_author')
    return render(request, 'book/add_author.html')

def add_book(request):
    authors = Author.objects.all()
    genres = Genre.objects.all()
    tags = Tag.objects.all()
    
    if request.method == 'POST':
        isbn = request.POST.get('isbn')
        title = request.POST.get('title')
        author_id = request.POST.get('author')
        publisher = request.POST.get('publisher')
        publication_year = request.POST.get('publication_year')
        edition = request.POST.get('edition')
        language = request.POST.get('language')
        genre_id = request.POST.get('genre')
        description = request.POST.get('description')
        availability = request.POST.get('availability')
        
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
            availability=availability
        )
        
        # Add tags
        selected_tags = request.POST.getlist('tags')
        for tag_id in selected_tags:
            tag = Tag.objects.get(id=tag_id)
            book.tags.add(tag)
        
        messages.success(request, 'Book added successfully!')
        return redirect('add_book')
    
    return render(request, 'book/add_book.html', {'authors': authors, 'genres': genres, 'tags': tags})