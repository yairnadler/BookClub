from flask import Blueprint, jsonify, request
from utils import *
from .books import ratings

bp = Blueprint('ratings', __name__)

# Retrieve all ratings
@bp.route('/', methods=['GET'])
def get_ratings():
    return jsonify(ratings)

# Retrieve ratings for a specific book by ID
@bp.route('/<id>', methods=['GET'])
def get_ratings_by_id(id):
    rating = ratings.get(int(id), None)
    if rating:
        return jsonify(rating), 200
    
    return jsonify({'message': 'Rating not found'}), 404

# Retrieve the top 3 books based on average rating
@bp.route('/top', methods=['GET'])
def get_top_three_books():
    top_books = top_three_books(ratings)
    return jsonify(top_books)

# Add a rating for a specific book by ID
@bp.route('/<id>/values', methods=['POST'])
def add_rating_by_id(id):
    # Check if the request is JSON
    if request.content_type != 'application/json':
        return jsonify('error: Content-Type should be application/json'), 415
    
    rating_value = request.get_json().get('value', None)
    # Check if the rating is between 1 and 5
    if rating_value >= 1 and rating_value <= 5:
        ratings[int(id)]['values'].append(rating_value)
        ratings[int(id)]['average'] = sum(ratings[int(id)]['values']) / len(ratings[int(id)]['values'])
        return jsonify(ratings[int(id)]['average']), 200
    
    return jsonify({'message': 'Error adding rating, check that the value is correct'}), 422
