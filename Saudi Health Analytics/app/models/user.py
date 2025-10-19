"""
User Model
Handles user authentication, authorization, and profile management
"""

from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from flask import current_app
from app import db, login
from app.models.base import BaseModel
import jwt
import secrets


class User(UserMixin, BaseModel):
    """User model for authentication and profile management"""
    
    # Basic user information
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    
    # Contact information
    phone = db.Column(db.String(20))
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    
    # Account status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    email_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    email_confirmed_on = db.Column(db.DateTime)
    
    # User preferences
    language = db.Column(db.String(5), default='ar', nullable=False)
    timezone = db.Column(db.String(50), default='Asia/Riyadh', nullable=False)
    
    # Security
    role = db.Column(db.String(50), default='user', nullable=False)
    last_login = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime)
    password_reset_token = db.Column(db.String(255))
    password_reset_expires = db.Column(db.DateTime)
    
    # Relationships
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    region = db.relationship('Region', backref='users')
    
    def __init__(self, **kwargs):
        """Initialize user with default values"""
        super(User, self).__init__(**kwargs)
        if not self.role:
            self.role = 'user'
    
    def set_password(self, password):
        """Set user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches"""
        return check_password_hash(self.password_hash, password)
    
    def get_reset_password_token(self, expires_in=600):
        """Generate password reset token"""
        token = secrets.token_urlsafe(32)
        self.password_reset_token = token
        self.password_reset_expires = datetime.utcnow() + timedelta(seconds=expires_in)
        self.save()
        return token
    
    @staticmethod
    def verify_reset_password_token(token):
        """Verify password reset token"""
        user = User.query.filter_by(password_reset_token=token).first()
        if user and user.password_reset_expires > datetime.utcnow():
            return user
        return None
    
    def generate_confirmation_token(self, expiration=3600):
        """Generate email confirmation token"""
        return jwt.encode(
            {
                'confirm': self.id,
                'exp': datetime.utcnow() + timedelta(seconds=expiration)
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    
    def confirm_email(self, token):
        """Confirm email address"""
        try:
            data = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
        except:
            return False
        
        if data.get('confirm') != self.id:
            return False
        
        self.email_confirmed = True
        self.email_confirmed_on = datetime.utcnow()
        self.save()
        return True
    
    def is_account_locked(self):
        """Check if account is locked"""
        if self.account_locked_until:
            return datetime.utcnow() < self.account_locked_until
        return False
    
    def lock_account(self, minutes=30):
        """Lock user account"""
        self.account_locked_until = datetime.utcnow() + timedelta(minutes=minutes)
        self.save()
    
    def unlock_account(self):
        """Unlock user account"""
        self.account_locked_until = None
        self.failed_login_attempts = 0
        self.save()
    
    def record_failed_login(self):
        """Record failed login attempt"""
        self.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.lock_account()
        
        self.save()
    
    def record_successful_login(self):
        """Record successful login"""
        self.last_login = datetime.utcnow()
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.save()
    
    def has_role(self, role):
        """Check if user has specific role"""
        return self.role == role
    
    def has_permission(self, permission):
        """Check if user has specific permission"""
        role_permissions = {
            'admin': [
                'view_all', 'create_all', 'edit_all', 'delete_all',
                'manage_users', 'system_settings', 'export_data'
            ],
            'manager': [
                'view_all', 'create_workforce', 'edit_workforce',
                'view_analytics', 'export_data'
            ],
            'analyst': [
                'view_all', 'view_analytics', 'create_reports'
            ],
            'user': [
                'view_dashboard', 'view_own_data'
            ]
        }
        
        user_permissions = role_permissions.get(self.role, [])
        return permission in user_permissions
    
    @property
    def full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    @property
    def is_manager(self):
        """Check if user is manager"""
        return self.role in ['admin', 'manager']
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = super().to_dict()
        
        # Remove sensitive information unless explicitly requested
        if not include_sensitive:
            data.pop('password_hash', None)
            data.pop('password_reset_token', None)
            data.pop('password_reset_expires', None)
        
        # Add computed properties
        data['full_name'] = self.full_name
        data['is_admin'] = self.is_admin
        data['is_manager'] = self.is_manager
        data['is_account_locked'] = self.is_account_locked()
        
        return data
    
    def __repr__(self):
        return f'<User {self.email}>'


@login.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.query.get(int(user_id)) 