from flask import Blueprint

bp = Blueprint('projections', __name__, url_prefix='/projections')

from app.projections import routes 