from flask import Blueprint, request, jsonify
from .books import books
from utils import *

bp = Blueprint('loans', __name__)

loans = {}

# Create a loan
@bp.route('/', methods=['POST'])
def create_loan():
    if request.content_type != 'application/json':
        return jsonify('error: Content-Type should be application/json'), 415
    loan_data, error_message = validate_post_loans_data(request, books, loans)
    if not loan_data:
        return jsonify({'error': error_message}), 422
    
    # if a member has borrowed over 2 books, they cannot borrow another
    if len([loan for loan in loans.values() if loan.get('memberName') == loan_data.get('memberName')]) >= 2:
        return jsonify({'error': 'Member has borrowed 2 books already'}), 422

    loan_id = str(len(loans) + 1)
    book_id = [book.get('id') for book in books.values() if book.get('ISBN') == loan_data.get('ISBN')][0]
    title = [book.get('title') for book in books.values() if book.get('ISBN') == loan_data.get('ISBN')][0]
    new_loan = create_new_loan(loan_data, book_id, title, loan_id)
    loans[int(loan_id)] = new_loan

    return jsonify(int(loan_id)), 201

# Retrieve loans with optional query parameters
@bp.route('/', methods=['GET'])
def get_loans():
    query_params = request.args
    if not query_params:
        return jsonify(loans)

    filtered_loans = filter_loans_query(query_params, books)

    return jsonify(filtered_loans)

# Retrieve a specific loan by ID
@bp.route('/<id>', methods=['GET'])
def get_loan_by_id(id):
    loan = loans.get(int(id), None)
    if loan:
        return jsonify(loan), 200
    return jsonify({'message': 'Loan not found'}), 404

# Delete a specific loan by ID
@bp.route('/<id>', methods=['DELETE'])
def delete_loan_by_id(id):
    loan = loans.get(int(id), None)
    if loan:
        title = loan.get('title')
        del loans[int(id)]
        return jsonify({'message': f'Thank you for returning {title}. Hope you had a great time!'}), 200
    return jsonify({'message': 'Loan not found'}), 404