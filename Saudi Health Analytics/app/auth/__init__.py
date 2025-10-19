"""
Authentication Blueprint
Handles user authentication, registration, and session management
"""

from flask import Blueprint

bp = Blueprint('auth', __name__)

from app.auth import routes 