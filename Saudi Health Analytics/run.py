#!/usr/bin/env python3
"""
Healthcare Workforce Planning System - Main Entry Point
Flask application runner with SocketIO support
"""

import os
from app import create_app, socketio

# Create Flask application
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

@app.cli.command()
def coverage():
    """Run unit tests with coverage."""
    import coverage
    import unittest
    
    cov = coverage.coverage(branch=True, include='app/*')
    cov.start()
    
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    
    cov.stop()
    cov.save()
    print('Coverage Summary:')
    cov.report()
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    covdir = os.path.join(basedir, 'htmlcov')
    cov.html_report(directory=covdir)
    print(f'HTML version: file://{covdir}/index.html')
    cov.erase()

if __name__ == '__main__':
    # Use SocketIO for development server
    socketio.run(
        app,
        debug=app.config['DEBUG'],
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    ) 