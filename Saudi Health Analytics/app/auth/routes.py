"""
Authentication Routes
User authentication and authorization functionality
"""

from flask import render_template_string, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.auth import bp
from app.models.user import User
from app import db
import os


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login route - serves login page and handles authentication"""
    if request.method == 'GET':
        # Serve the login HTML page
        try:
            with open('pages/auth/login.html', 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except FileNotFoundError:
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head><title>Login - Saudi Health System</title></head>
            <body>
                <h1>Login</h1>
                <form method="post">
                    <input type="email" name="email" placeholder="Email" required>
                    <input type="password" name="password" placeholder="Password" required>
                    <button type="submit">Login</button>
                </form>
            </body>
            </html>
            """)
    
    elif request.method == 'POST':
        # Handle login form submission
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
        else:
            email = request.form.get('email')
            password = request.form.get('password')
        
        if email and password:
            # For demo purposes, accept demo credentials
            if email == 'demo@health.gov.sa' and password == 'demo123456':
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'redirect': '/dashboard'
                })
            
            # Check against database users
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                login_user(user)
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'redirect': '/dashboard'
                })
        
        return jsonify({
            'success': False,
            'message': 'Invalid email or password'
        }), 401


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'GET':
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head><title>Register - Saudi Health System</title></head>
        <body style="font-family: Arial; padding: 40px; background: #f5f5f5;">
            <div style="max-width: 400px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px;">
                <h2>Register for Saudi Health System</h2>
                <form method="post">
                    <p><input type="text" name="first_name" placeholder="First Name" required style="width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px;"></p>
                    <p><input type="text" name="last_name" placeholder="Last Name" required style="width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px;"></p>
                    <p><input type="email" name="email" placeholder="Email" required style="width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px;"></p>
                    <p><input type="password" name="password" placeholder="Password" required style="width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px;"></p>
                    <p><input type="text" name="department" placeholder="Department" style="width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px;"></p>
                    <p><button type="submit" style="width: 100%; padding: 12px; background: #10b981; color: white; border: none; border-radius: 4px; cursor: pointer;">Register</button></p>
                </form>
                <p><a href="/auth/login">Already have an account? Login here</a></p>
            </div>
        </body>
        </html>
        """)
    
    elif request.method == 'POST':
        # Handle registration
        data = request.form
        
        # Create new user
        user = User(
            email=data.get('email'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            department=data.get('department', 'General'),
            role='user',
            is_active=True,
            email_confirmed=True
        )
        user.set_password(data.get('password'))
        
        try:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('auth.login'))
        except Exception as e:
            return jsonify({'error': 'Registration failed', 'details': str(e)}), 400


@bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return jsonify({
        'user': current_user.to_dict(),
        'message': 'User profile data'
    }) 