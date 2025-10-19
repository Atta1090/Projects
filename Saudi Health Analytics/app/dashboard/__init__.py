"""
Dashboard Blueprint
Handles dashboard functionality and overview statistics
"""

from flask import Blueprint

bp = Blueprint('dashboard', __name__)

from app.dashboard import routes 