import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_babel import Babel, lazy_gettext as _l
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
mail = Mail()
babel = Babel()
cache = Cache()
cors = CORS()
jwt = JWTManager()
socketio = SocketIO()

# Configure login manager
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page.')
login.login_message_category = 'info'


def create_app(config_name=None):
    """
    Application factory function
    Creates and configures Flask application instance
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG') or 'default'
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    babel.init_app(app)
    cache.init_app(app)
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    jwt.init_app(app)
    socketio.init_app(app, 
                     cors_allowed_origins="*",
                     async_mode='threading')
    
    # Register blueprints
    register_blueprints(app)
    
    # Configure Babel for internationalization
    @babel.localeselector
    def get_locale():
        """Select locale based on user preference or request"""
        # 1. If user is logged in, use their preferred language
        from flask_login import current_user
        if current_user and hasattr(current_user, 'language'):
            return current_user.language
        
        # 2. Check for language in request args
        requested_lang = request.args.get('lang')
        if requested_lang in app.config['LANGUAGES']:
            return requested_lang
        
        # 3. Use browser's accepted languages
        return request.accept_languages.best_match(
            app.config['LANGUAGES'].keys()) or app.config['BABEL_DEFAULT_LOCALE']
    
    # Configure error handlers
    register_error_handlers(app)
    
    # Configure logging
    configure_logging(app)
    
    # Register shell context
    @app.shell_context_processor
    def make_shell_context():
        """Register shell context for flask shell command"""
        from app.models import (
            User, Region, HealthcareWorkerCategory, WorkforceStock,
            PopulationData, HealthCondition, ServiceStandard
        )
        return {
            'db': db,
            'User': User,
            'Region': Region,
            'HealthcareWorkerCategory': HealthcareWorkerCategory,
            'WorkforceStock': WorkforceStock,
            'PopulationData': PopulationData,
            'HealthCondition': HealthCondition,
            'ServiceStandard': ServiceStandard
        }
    
    # Configure CLI commands
    register_cli_commands(app)
    
    return app


def register_blueprints(app):
    """Register all application blueprints"""
    
    # Main blueprint
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    # Authentication blueprint
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Dashboard blueprint
    from app.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    
    # Workforce management blueprint
    from app.workforce import bp as workforce_bp
    app.register_blueprint(workforce_bp, url_prefix='/workforce')
    
    # Analytics blueprint
    from app.analytics import bp as analytics_bp
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    
    # API blueprints
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # ML API blueprint
    from app.api.ml import bp as ml_api_bp
    app.register_blueprint(ml_api_bp, url_prefix='/api/v1/ml')
    
    # Admin blueprint
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Register CSV analysis blueprint
    from app.csv_analysis.routes import csv_bp
    app.register_blueprint(csv_bp)


def register_error_handlers(app):
    """Register error handlers for the application"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template, jsonify
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Not found',
                'message': 'The requested resource was not found'
            }), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template, jsonify
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Internal server error',
                'message': 'An unexpected error occurred'
            }), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template, jsonify
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Forbidden',
                'message': 'You do not have permission to access this resource'
            }), 403
        return render_template('errors/403.html'), 403


def configure_logging(app):
    """Configure logging for the application"""
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/healthcare_workforce.log',
            maxBytes=10240,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Healthcare Workforce application startup')


def register_cli_commands(app):
    """Register CLI commands for the application"""
    
    @app.cli.command()
    def init_db():
        """Initialize the database with sample data"""
        from app.utils.database import init_database
        init_database()
        print('Database initialized with sample data.')
    
    @app.cli.command()
    def create_admin():
        """Create an admin user"""
        from app.models.user import User
        from werkzeug.security import generate_password_hash
        
        email = input('Enter admin email: ')
        password = input('Enter admin password: ')
        
        admin = User(
            email=email,
            password_hash=generate_password_hash(password),
            role='admin',
            is_active=True,
            email_confirmed=True
        )
        
        db.session.add(admin)
        db.session.commit()
        print(f'Admin user {email} created successfully.')
    
    @app.cli.command()
    def translate():
        """Update all language translations"""
        import subprocess
        import os
        
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        if os.system('pybabel update -i messages.pot -d app/translations'):
            raise RuntimeError('update command failed')
        os.remove('messages.pot')
        print('Translation files updated.')
    
    @app.cli.command()
    def compile_translations():
        """Compile all language translations"""
        import subprocess
        
        if os.system('pybabel compile -d app/translations'):
            raise RuntimeError('compile command failed')
        print('Translation files compiled.')


# Import models to ensure they are known to SQLAlchemy
from app.models import user, region, healthcare_worker, workforce, population, health_status, service_standards 