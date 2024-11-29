# yourapp/utils.py
import requests
from django.conf import settings

def fetch_google_books_metadata(query):
    """Fetches book metadata from the Google Books API."""
    api_key = settings.GOOGLE_BOOKS_API_KEY
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        books = []
        for item in data.get('items', []):
            books.append({
                'title': item['volumeInfo'].get('title', 'No Title'),
                'author': ', '.join(item['volumeInfo'].get('authors', ['Unknown Author'])),
                'isbn': next( 
                    (identifier['identifier'] for identifier in item['volumeInfo'].get('industryIdentifiers', []) 
                     if identifier['type'] == 'ISBN_13'), 'N/A'),
                'publication_year': item['volumeInfo'].get('publishedDate', '')[:4],
                'digital_link': item['volumeInfo'].get('previewLink', '#'),
                'digital_source': 'Google Books'
            })
        return books
    return []
