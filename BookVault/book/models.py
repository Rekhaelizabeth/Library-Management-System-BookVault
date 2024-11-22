from django.db import models

# Model for Author (if you plan to store authors separately)
class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)  # Optional field for bio
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# Model for Genre
class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)


    def __str__(self):
        return self.name

# Model for Book
class Book(models.Model):
    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('checked_out', 'Checked Out'),
        ('damaged', 'Damaged'),
        ('lost', 'Lost'),
    ]
    
    isbn = models.CharField(max_length=13, unique=True)  # ISBN is unique
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    publisher = models.CharField(max_length=255)
    publication_year = models.PositiveIntegerField()
    edition = models.CharField(max_length=100, blank=True, null=True)
    language = models.CharField(max_length=50)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='books')
    tags = models.ManyToManyField('Tag', blank=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    description = models.TextField()
    availability = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default='available'
    )
    related_titles = models.ManyToManyField('self', blank=True, symmetrical=False)

    def __str__(self):
        return self.title

# Model for Tags (used for tagging books with keywords)
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
