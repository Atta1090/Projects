from flask import Blueprint
bp = Blueprint('ml_api', __name__)
from app.api.ml import routes 