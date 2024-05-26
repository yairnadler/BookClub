from flask import Blueprint
from .books import bp as books_bp
from .ratings import bp as ratings_bp
from .loans import bp as loans_bp

api_bp = Blueprint('api', __name__)

api_bp.register_blueprint(books_bp, url_prefix='/books')
api_bp.register_blueprint(ratings_bp, url_prefix='/ratings')
api_bp.register_blueprint(loans_bp, url_prefix='/loans')

@api_bp.route('/', methods=['GET'])
def index():
    return "Welcome to the Book Club API!"