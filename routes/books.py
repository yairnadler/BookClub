from flask import Blueprint, jsonify, request
import requests
from utils import *

bp = Blueprint('books', __name__)

# Dummy data (replace with database)
books = {}
ratings = {}

# Create a book
@bp.route('/', methods=['POST'])
def create_book():
    # Check if the request is JSON
    if request.content_type != 'application/json':
        return jsonify('error: Content-Type should be application/json'), 415
    # Validate the request JSON data
    book_data, error_message = validate_post_json_data(request, books)
    if not book_data:
        return jsonify({'error': error_message}), 422
    # Extract book details from the request JSON data
    book_title = book_data.get('title', '')
    book_genre = book_data.get('genre', '')
    isbn_num = book_data.get('ISBN', '')
    book_id = str(len(books) + 1)
    # Fetch book details from Google Books API
    book_info = fecth_details_googleAPI(isbn_num)
    if book_info:
        new_book, new_book_rating = create_new_book(book_info, book_id, book_title, isbn_num, book_genre)
        books[int(book_id)] = new_book
        ratings[int(book_id)] = new_book_rating

        return jsonify(int(book_id)), 201
    else:
        return jsonify({'error': f'Unable to connect to external server'}), 500

# Retrieve books with optional query parameters
@bp.route('/', methods=['GET'])
def get_books():
    query_params = request.args
    if not query_params:
        return jsonify(books)
    
    filtered_books = filter_books_query(query_params, books)
    if filtered_books[0] == 422:
        return filtered_books[1], 422
    
    return jsonify(filtered_books)
        
# Retrieve a specific book by ID
@bp.route('/books/<id>', methods=['GET'])
def get_book_by_id(id):
    book = books.get(int(id), None)
    if book:
        return jsonify(book), 200
    return jsonify({'message': 'Book not found'}), 404

# Delete a specific book by ID
@bp.route('/<id>', methods=['DELETE'])
def delete_book_by_id(id):
    book = books.get(int(id), None)
    if book:
        del books[int(id)]
        return jsonify({'message': 'Book deleted successfully'}), 200
    
    return jsonify({'message': 'Book not found'}), 404

# Putting a book with all its fields
@bp.route('/<id>', methods=['PUT'])
def update_book_by_id(id):
    # Check if the request is JSON
    if request.content_type != 'application/json':
        return jsonify('error: Content-Type should be application/json'), 415
    # Check if the book exists
    book_exists = False
    for book in books.values():
        if book['id'] == id:
            book_exists = True
            break

    if not book_exists:
        return jsonify({'message': 'Attempting to update a book that does not exist'}), 404
    
    book_json = request.get_json()
    updated_book = update_book(book_json)
    if updated_book.get('id') != id:
        return jsonify({'message': 'Error updating book, check that the ID is correct'}), 422
    
    if updated_book:
        books[int(id)] = updated_book

        return jsonify(int(id)), 200
    
    return jsonify({'message': 'Error creating book, check that all fields are correct'}), 422
