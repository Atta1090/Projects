"""
Main Blueprint
Handles main application routes and general functionality
"""

from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes 