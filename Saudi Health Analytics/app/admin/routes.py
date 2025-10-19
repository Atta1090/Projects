"""
Admin Routes
System administration and management functionality
"""

from flask import render_template_string, jsonify, request, redirect, url_for
from flask_login import login_required, current_user
from app.admin import bp
from app.models.user import User
from app.models.region import Region
from app.models.healthcare_worker import HealthcareWorkerCategory
from app.models.workforce import WorkforceStock
from app.utils.database import init_database, get_sample_data_summary
from app import db
import os


def admin_required(f):
    """Decorator to require admin role"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.has_role('admin'):
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


@bp.route('/')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Dashboard - Saudi Health System</title>
        <style>
            body { font-family: Arial; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .card { background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .nav { background: #1e293b; padding: 15px 0; margin: -20px -20px 20px -20px; }
            .nav a { color: white; text-decoration: none; margin: 0 15px; }
            .admin-nav { background: #dc2626; padding: 10px 0; margin: -20px -20px 20px -20px; }
            .admin-nav a { color: white; text-decoration: none; margin: 0 15px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .metric { text-align: center; background: #f8f9fa; padding: 20px; border-radius: 8px; }
            .metric h3 { color: #dc2626; margin: 0; font-size: 1.8em; }
            .btn { background: #dc2626; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
            .btn:hover { background: #b91c1c; }
            .btn-success { background: #10b981; }
            .btn-success:hover { background: #059669; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav">
                <a href="/">Home</a>
                <a href="/dashboard">Dashboard</a>
                <a href="/workforce">Workforce</a>
                <a href="/admin">Admin</a>
            </div>
            
            <div class="admin-nav">
                <a href="/admin">Dashboard</a>
                <a href="/admin/users">User Management</a>
                <a href="/admin/system">System Settings</a>
                <a href="/admin/data">Data Management</a>
            </div>
            
            <h1>🛡️ Admin Dashboard</h1>
            
            <div class="card">
                <h2>System Overview</h2>
                <div class="grid">
                    <div class="metric">
                        <h3 id="total-users">0</h3>
                        <p>Registered Users</p>
                    </div>
                    <div class="metric">
                        <h3 id="total-regions">13</h3>
                        <p>Regions</p>
                    </div>
                    <div class="metric">
                        <h3 id="total-records">0</h3>
                        <p>Workforce Records</p>
                    </div>
                    <div class="metric">
                        <h3 id="system-status">Online</h3>
                        <p>System Status</p>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>Quick Actions</h2>
                <div class="grid">
                    <div>
                        <h3>Data Management</h3>
                        <button class="btn btn-success" onclick="initializeDatabase()">Initialize Sample Data</button>
                        <button class="btn" onclick="exportData()">Export All Data</button>
                        <button class="btn" onclick="clearData()">Clear Test Data</button>
                    </div>
                    <div>
                        <h3>User Management</h3>
                        <button class="btn btn-success" onclick="window.location='/admin/users'">Manage Users</button>
                        <button class="btn" onclick="createAdminUser()">Create Admin</button>
                        <button class="btn" onclick="resetPasswords()">Reset Passwords</button>
                    </div>
                    <div>
                        <h3>System Maintenance</h3>
                        <button class="btn" onclick="checkSystemHealth()">Health Check</button>
                        <button class="btn" onclick="viewLogs()">View Logs</button>
                        <button class="btn" onclick="backupSystem()">Backup Data</button>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>Recent Activity</h2>
                <div id="recent-activity">
                    <p>Loading recent system activity...</p>
                </div>
            </div>
        </div>
        
        <script>
            // Load admin dashboard data
            function loadAdminData() {
                fetch('/admin/api/overview')
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            document.getElementById('total-users').textContent = data.users;
                            document.getElementById('total-regions').textContent = data.regions;
                            document.getElementById('total-records').textContent = data.workforce_records;
                        }
                    })
                    .catch(error => console.log('Using default values'));
            }
            
            function initializeDatabase() {
                if (confirm('This will initialize the database with sample data. Continue?')) {
                    fetch('/admin/api/init-database', { method: 'POST' })
                        .then(response => response.json())
                        .then(data => {
                            alert(data.message);
                            loadAdminData();
                        });
                }
            }
            
            function exportData() {
                window.location = '/admin/api/export-data';
            }
            
            function clearData() {
                if (confirm('This will clear all test data. This action cannot be undone. Continue?')) {
                    fetch('/admin/api/clear-data', { method: 'POST' })
                        .then(response => response.json())
                        .then(data => alert(data.message));
                }
            }
            
            function createAdminUser() {
                const email = prompt('Enter admin email:');
                const password = prompt('Enter admin password:');
                if (email && password) {
                    fetch('/admin/api/create-admin', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email, password })
                    })
                    .then(response => response.json())
                    .then(data => alert(data.message));
                }
            }
            
            function checkSystemHealth() {
                fetch('/health')
                    .then(response => response.json())
                    .then(data => {
                        alert('System Status: ' + data.status + '\\nService: ' + data.service);
                    });
            }
            
            function viewLogs() {
                window.open('/admin/logs', '_blank');
            }
            
            function backupSystem() {
                fetch('/admin/api/backup', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => alert(data.message));
            }
            
            loadAdminData();
        </script>
    </body>
    </html>
    """)


@bp.route('/users')
@login_required
@admin_required
def user_management():
    """User management interface"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>User Management - Admin</title>
        <style>
            body { font-family: Arial; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .card { background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
            th { background: #f3f4f6; }
            .btn { background: #dc2626; color: white; padding: 5px 10px; border: none; border-radius: 4px; cursor: pointer; margin: 2px; }
            .btn-sm { padding: 3px 8px; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>👥 User Management</h1>
            <a href="/admin">← Back to Admin Dashboard</a>
            
            <div class="card">
                <h2>All Users</h2>
                <div id="users-table">Loading users...</div>
            </div>
        </div>
        
        <script>
            function loadUsers() {
                fetch('/admin/api/users')
                    .then(response => response.json())
                    .then(data => {
                        const tableDiv = document.getElementById('users-table');
                        if (data.success && data.users.length > 0) {
                            let html = `
                                <table>
                                    <tr>
                                        <th>ID</th>
                                        <th>Email</th>
                                        <th>Name</th>
                                        <th>Role</th>
                                        <th>Status</th>
                                        <th>Actions</th>
                                    </tr>
                            `;
                            
                            data.users.forEach(user => {
                                html += `
                                    <tr>
                                        <td>${user.id}</td>
                                        <td>${user.email}</td>
                                        <td>${user.full_name || 'N/A'}</td>
                                        <td>${user.role}</td>
                                        <td>${user.is_active ? 'Active' : 'Inactive'}</td>
                                        <td>
                                            <button class="btn btn-sm" onclick="editUser(${user.id})">Edit</button>
                                            <button class="btn btn-sm" onclick="deleteUser(${user.id})">Delete</button>
                                        </td>
                                    </tr>
                                `;
                            });
                            
                            html += '</table>';
                            tableDiv.innerHTML = html;
                        } else {
                            tableDiv.innerHTML = '<p>No users found.</p>';
                        }
                    });
            }
            
            function editUser(userId) {
                alert('Edit user functionality would open a form here');
            }
            
            function deleteUser(userId) {
                if (confirm('Delete this user?')) {
                    fetch(`/admin/api/users/${userId}`, { method: 'DELETE' })
                        .then(response => response.json())
                        .then(data => {
                            alert(data.message);
                            loadUsers();
                        });
                }
            }
            
            loadUsers();
        </script>
    </body>
    </html>
    """)


@bp.route('/api/overview')
@login_required
@admin_required
def admin_overview():
    """Get admin overview data"""
    try:
        users_count = User.query.count()
        regions_count = Region.query.count()
        workforce_records = WorkforceStock.query.count()
        categories_count = HealthcareWorkerCategory.query.count()
        
        return jsonify({
            'success': True,
            'users': users_count,
            'regions': regions_count,
            'workforce_records': workforce_records,
            'categories': categories_count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'users': 0,
            'regions': 13,
            'workforce_records': 0,
            'categories': 8
        })


@bp.route('/api/init-database', methods=['POST'])
@login_required
@admin_required
def initialize_database():
    """Initialize database with sample data"""
    try:
        init_database()
        summary = get_sample_data_summary()
        
        return jsonify({
            'success': True,
            'message': 'Database initialized successfully!',
            'summary': summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Database initialization failed: {str(e)}'
        }), 500


@bp.route('/api/users')
@login_required
@admin_required
def get_users():
    """Get all users"""
    try:
        users = User.query.all()
        users_data = [user.to_dict() for user in users]
        
        return jsonify({
            'success': True,
            'users': users_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'users': []
        })


@bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user"""
    try:
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'User deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting user: {str(e)}'
        }), 500


@bp.route('/api/create-admin', methods=['POST'])
@login_required
@admin_required
def create_admin_user():
    """Create admin user"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password required'
            }), 400
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'User already exists'
            }), 400
        
        # Create admin user
        admin_user = User(
            email=email,
            first_name='Admin',
            last_name='User',
            role='admin',
            is_active=True,
            email_confirmed=True
        )
        admin_user.set_password(password)
        
        db.session.add(admin_user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Admin user {email} created successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating admin user: {str(e)}'
        }), 500


@bp.route('/system')
@login_required
@admin_required
def system_settings():
    """System settings interface"""
    return jsonify({
        'message': 'System settings interface',
        'settings': [
            'Database configuration',
            'Security settings',
            'Backup configuration',
            'System monitoring'
        ]
    })


@bp.route('/data')
@login_required
@admin_required
def data_management():
    """Data management interface"""
    return jsonify({
        'message': 'Data management interface',
        'features': [
            'Import/Export data',
            'Data validation',
            'Cleanup tools',
            'Migration utilities'
        ]
    }) 