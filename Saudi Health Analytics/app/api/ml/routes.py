from flask import jsonify
from app.api.ml import bp

@bp.route('/')
def ml_api_info():
    return jsonify({'message': 'ML API endpoints - To be implemented'}) 