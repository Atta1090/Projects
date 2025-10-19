"""
Dashboard Routes
Main dashboard interface with workforce analytics
"""

from flask import render_template_string, jsonify, request
from flask_login import login_required
from app.dashboard import bp
from app.models.workforce import WorkforceStock
from app.models.region import Region
from app.models.healthcare_worker import HealthcareWorkerCategory
from app.services.workforce_calculator import WorkforceCalculatorService
from app import db
import os


@bp.route('/')
@bp.route('/dashboard')
def dashboard():
    """Main dashboard interface"""
    try:
        # Serve the dashboard HTML page
        with open('dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        # Fallback dashboard if HTML file not found
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dashboard - Saudi Health Workforce Planning</title>
            <style>
                body { font-family: Arial; margin: 0; padding: 20px; background: #f5f5f5; }
                .dashboard { max-width: 1200px; margin: 0 auto; }
                .card { background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
                .metric { text-align: center; }
                .metric h3 { color: #10b981; margin: 0; font-size: 2em; }
                .metric p { color: #666; margin: 5px 0 0 0; }
                .nav { background: #1e293b; padding: 15px 0; margin: -20px -20px 20px -20px; }
                .nav a { color: white; text-decoration: none; margin: 0 15px; }
            </style>
        </head>
        <body>
            <div class="dashboard">
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/dashboard">Dashboard</a>
                    <a href="/workforce">Workforce</a>
                    <a href="/projections">Projections</a>
                    <a href="/reports">Reports</a>
                    <a href="/csv">CSV Analysis</a>
                </div>
                
                <h1>Saudi Health Workforce Dashboard</h1>
                
                <div class="card">
                    <h2>Key Metrics</h2>
                    <div class="metrics">
                        <div class="metric">
                            <h3 id="total-workforce">245,000+</h3>
                            <p>Total Healthcare Workers</p>
                        </div>
                        <div class="metric">
                            <h3 id="regions">13</h3>
                            <p>Regions Covered</p>
                        </div>
                        <div class="metric">
                            <h3 id="hospitals">1,200+</h3>
                            <p>Healthcare Facilities</p>
                        </div>
                        <div class="metric">
                            <h3 id="specialties">50+</h3>
                            <p>Medical Specialties</p>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h2>Regional Overview</h2>
                    <p>Interactive map and regional statistics will be displayed here.</p>
                    <div id="regional-data">Loading regional data...</div>
                </div>
                
                <div class="card">
                    <h2>Workforce Gaps</h2>
                    <p>Critical shortage analysis and recommendations.</p>
                    <div id="gap-analysis">Loading gap analysis...</div>
                </div>
            </div>
            
            <script>
                // Load dashboard data
                fetch('/api/v1/reports/executive-dashboard')
                    .then(response => response.json())
                    .then(data => {
                        console.log('Dashboard data loaded:', data);
                        // Update dashboard with real data
                    })
                    .catch(error => console.log('Demo mode - using static data'));
            </script>
        </body>
        </html>
        """)


@bp.route('/api/dashboard-data')
def dashboard_data():
    """Get dashboard data for the frontend"""
    try:
        # Get summary statistics
        workforce_summary = WorkforceStock.get_national_summary()
        regional_data = WorkforceStock.get_regional_comparison()
        
        # Get region count
        region_count = Region.query.count()
        
        # Get category count
        category_count = HealthcareWorkerCategory.query.count()
        
        return jsonify({
            'success': True,
            'data': {
                'national_summary': workforce_summary,
                'regional_data': regional_data,
                'metrics': {
                    'total_regions': region_count,
                    'total_categories': category_count,
                    'total_workforce': workforce_summary.get('total_workforce', 0),
                    'vacancy_rate': workforce_summary.get('vacancy_rate', 0)
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'data': {
                'metrics': {
                    'total_regions': 13,
                    'total_categories': 8,
                    'total_workforce': 245000,
                    'vacancy_rate': 12.5
                }
            }
        })


@bp.route('/workforce')
def workforce_module():
    """Workforce analysis module"""
    try:
        with open('pages/modules/workforce.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return jsonify({'error': 'Workforce module page not found'}), 404


@bp.route('/projections')
def projections_module():
    """Projections module"""
    try:
        with open('pages/modules/projections.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return jsonify({'error': 'Projections module page not found'}), 404


@bp.route('/scenarios')
def scenarios_module():
    """Scenarios planning module"""
    try:
        with open('pages/modules/scenarios.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return jsonify({'error': 'Scenarios module page not found'}), 404


@bp.route('/reports')
def reports_module():
    """Reports module"""
    try:
        with open('pages/modules/reports.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return jsonify({'error': 'Reports module page not found'}), 404 