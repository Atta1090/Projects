"""
CSV Analysis Module
Simple data upload and analysis
Supports both full mode (with pandas) and simple mode (standard library only)
"""

# Try to import full functionality, fall back to simple mode if pandas not available
try:
    from app.csv_analysis.upload_handler import CSVUploadHandler
    from app.csv_analysis.data_analyzer import DataAnalyzer
    PANDAS_AVAILABLE = True
except ImportError:
    # Pandas not available, use simple mode
    from app.csv_analysis.upload_handler_simple import SimpleCSVUploadHandler, SimpleDataAnalyzer
    CSVUploadHandler = SimpleCSVUploadHandler
    DataAnalyzer = SimpleDataAnalyzer
    PANDAS_AVAILABLE = False

__all__ = [
    'CSVUploadHandler',
    'DataAnalyzer', 
    'PANDAS_AVAILABLE'
] 