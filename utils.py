from flask import jsonify
import os
import requests

REQUIRED_FIELDS = ["ISBN", "title", "genre"]
GENRES = ['Fiction', 'Children', 'Biography', 'Science', 'Science Fiction', 'Fantasy', 'Other']
GOOGLE_BOOKS_API_BASE_URL = "https://www.googleapis.com/books/v1/volumes"
OPEN_LIBRARY_API_BASE_URL = "https://openlibrary.org/search.json"
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')


def validate_post_json_data(request, books):
    book_data = request.get_json()
    book_title = book_data.get('title', '')
    if not book_title:
        return None, 'error: Title is missing'
    book_genre = book_data.get('genre', '')
    if not book_genre or book_genre not in GENRES:
        return None, 'error: Genre is missing or invalid'
    isbn_num = book_data.get('ISBN', '')
    if not isbn_num or len(isbn_num) != 13 or not isbn_num.isdigit():
        return None, 'error: ISBN is missing or invalid'
    if int(isbn_num) in [book.get('ISBN') for book in books.values()]:
        return None, 'error: Book with the provided ISBN already exists'
    
    return book_data, 'no error found'

def fecth_details_googleAPI(isbn_num):
    try:
        google_books_response = requests.get(f"{GOOGLE_BOOKS_API_BASE_URL}?q=isbn:{isbn_num}")
        if google_books_response.status_code == 200:
            book_info = google_books_response.json()['items'][0]['volumeInfo']
            return book_info
    except:
        if google_books_response.json()['totalItems'] == 0:
            return jsonify({'error': 'No book found with the provided ISBN'}), 404
            

    return None

def create_new_book(book_info, book_id, book_title, isbn_num, book_genre):
    # Turn authors list into a string
    authors = book_info.get('authors', [])
    if len(authors) > 1:
        authors = ', '.join(authors)
        authors = authors.split(', ')
        authors[-1] = 'and ' + authors[-1]
        authors = ', '.join(authors)
    else:
        authors = authors[0]

    new_book = {
        'id': book_id,
        'title': book_title,
        'authors': authors,
        'ISBN': isbn_num,
        'publisher': book_info.get('publisher', ''),
        'publishedDate': book_info.get('publishedDate', ''),
        'genre': book_genre,
    }

    new_book_rating = {
        'values': [],
        'average': 0,
        'title': book_title,
        'id': book_id
    }    
    
    return new_book, new_book_rating

def filter_books_query(query_params, books):
    filtered_books = [book for book in books.values()]
    query_fields = ['title', 'authors', 'ISBN', 'publisher', 'publishedDate', 'genre', 'id']

    # Field based filtering
    for field in query_fields:
        field_query = query_params.get(f'{field}')
        if field_query:
            filtered_books = [book for book in filtered_books if book.get(field) == field_query]

    return filtered_books

def update_book(book_json):

    updated_book = {
        'id': book_json.get('id'),
        'title': book_json.get('title'),
        'authors': book_json.get('authors'),
        'ISBN': book_json.get('ISBN'),
        'publisher': book_json.get('publisher'),
        'publishedDate': book_json.get('publishedDate'),
        'genre': book_json.get('genre')
    }

    return updated_book

def top_three_books(ratings):
    possible_ratings = [rating for rating in ratings.values() if len(rating['values']) > 3]
    sorted_ratings = sorted(possible_ratings, key=lambda x: x['average'], reverse=True)
    top_ratings = []
    for rating in sorted_ratings:
        top_ratings.append({
            'id': rating['id'],
            'title': rating['title'],
            'average': rating['average']
        })
        if len(top_ratings) == 3:
            break

    return top_ratings

    
