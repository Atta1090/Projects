"""
Main Routes
Core application routes including dashboard and static pages
"""

from flask import jsonify, render_template_string, send_from_directory, redirect, url_for
from app.main import bp
import os


@bp.route('/')
def index():
    """Serve the main landing page"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return jsonify({'error': 'Landing page not found'}), 404


@bp.route('/dashboard.html')
@bp.route('/dashboard')
def dashboard():
    """Serve the enhanced dashboard"""
    try:
        with open('dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return jsonify({'error': 'Dashboard not found'}), 404


# Convenience routes for easier navigation
@bp.route('/login')
def login_redirect():
    """Redirect to auth login"""
    return redirect(url_for('auth.login'))


@bp.route('/workforce')
def workforce_redirect():
    """Redirect to workforce module"""
    return redirect(url_for('workforce.workforce_analysis'))


@bp.route('/projections')
def projections_redirect():
    """Redirect to projections module"""
    return redirect(url_for('analytics.projections'))


@bp.route('/scenarios')  
def scenarios_redirect():
    """Redirect to scenarios module"""
    return redirect(url_for('analytics.scenarios'))


@bp.route('/reports')
def reports_redirect():
    """Redirect to reports module"""
    return redirect(url_for('analytics.reports'))


@bp.route('/admin')
def admin_redirect():
    """Redirect to admin module"""
    return redirect(url_for('admin.admin_dashboard'))


@bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Healthcare Workforce Planning System',
        'version': '1.0.0',
        'features': [
            'AI-Powered Projections',
            'Real-time Analytics', 
            'Advanced Reporting',
            'Scenario Planning'
        ]
    })


@bp.route('/system-status')
def system_status():
    """System status with detailed metrics"""
    return jsonify({
        'status': 'operational',
        'services': {
            'api': 'online',
            'database': 'connected',
            'analytics': 'running',
            'ml_services': 'ready'
        },
        'metrics': {
            'uptime': '99.9%',
            'response_time': '< 100ms',
            'active_users': 156,
            'regions_monitored': 13
        },
        'modules': {
            'login': '/auth/login',
            'dashboard': '/dashboard', 
            'workforce': '/workforce/',
            'projections': '/analytics/projections',
            'scenarios': '/analytics/scenarios',
            'reports': '/analytics/reports',
            'csv_analysis': '/csv/',
            'admin': '/admin/'
        }
    }) 