"""
CSV Upload Handler
Processes uploaded CSV files and validates data
Simple approach without complex AI
"""

import pandas as pd
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from app.csv_analysis.csv_templates import get_csv_template


class CSVUploadHandler:
    """Handles CSV file uploads and basic validation"""
    
    def __init__(self, upload_folder='uploads'):
        self.upload_folder = upload_folder
        self.allowed_extensions = {'csv', 'xlsx', 'xls'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
        # Create upload folder if it doesn't exist
        os.makedirs(upload_folder, exist_ok=True)
    
    def allowed_file(self, filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def upload_file(self, file, data_type):
        """
        Upload and process CSV file
        
        Args:
            file: Uploaded file object
            data_type: Type of data ('workforce', 'population', 'health_conditions', 'training')
        
        Returns:
            dict: Upload result with success status and data
        """
        try:
            # Validate file
            if not file or file.filename == '':
                return {'success': False, 'error': 'No file selected'}
            
            if not self.allowed_file(file.filename):
                return {'success': False, 'error': 'File type not allowed. Please upload CSV or Excel files.'}
            
            # Check file size
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()
            file.seek(0)  # Reset to beginning
            
            if file_size > self.max_file_size:
                return {'success': False, 'error': 'File too large. Maximum size is 10MB.'}
            
            # Save file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(self.upload_folder, unique_filename)
            file.save(file_path)
            
            # Read and validate CSV data
            validation_result = self.validate_csv_data(file_path, data_type)
            
            if validation_result['success']:
                return {
                    'success': True,
                    'filename': unique_filename,
                    'file_path': file_path,
                    'data_type': data_type,
                    'row_count': validation_result['row_count'],
                    'columns': validation_result['columns'],
                    'data_preview': validation_result['data_preview'],
                    'upload_time': datetime.now().isoformat()
                }
            else:
                # Remove invalid file
                os.remove(file_path)
                return validation_result
                
        except Exception as e:
            return {'success': False, 'error': f'Upload failed: {str(e)}'}
    
    def validate_csv_data(self, file_path, data_type):
        """
        Validate CSV data against template requirements
        
        Args:
            file_path: Path to uploaded file
            data_type: Expected data type
        
        Returns:
            dict: Validation result
        """
        try:
            # Get template for data type
            template = get_csv_template(data_type)
            if not template:
                return {'success': False, 'error': f'Unknown data type: {data_type}'}
            
            # Read CSV file
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # Check if file is empty
            if df.empty:
                return {'success': False, 'error': 'File is empty'}
            
            # Check required columns
            required_columns = template['required_columns']
            missing_columns = []
            
            for col in required_columns:
                if col not in df.columns:
                    missing_columns.append(col)
            
            if missing_columns:
                return {
                    'success': False, 
                    'error': f'Missing required columns: {", ".join(missing_columns)}',
                    'required_columns': required_columns,
                    'found_columns': list(df.columns)
                }
            
            # Check for empty required fields
            empty_required = []
            for col in required_columns:
                if df[col].isnull().any():
                    empty_rows = df[df[col].isnull()].index.tolist()
                    empty_required.append(f"{col} (rows: {empty_rows[:5]})")  # Show first 5 empty rows
            
            if empty_required:
                return {
                    'success': False,
                    'error': f'Required fields cannot be empty: {"; ".join(empty_required)}'
                }
            
            # Data type validation
            validation_errors = self.validate_data_types(df, data_type)
            if validation_errors:
                return {
                    'success': False,
                    'error': f'Data validation errors: {"; ".join(validation_errors)}'
                }
            
            # Success - return data preview
            return {
                'success': True,
                'row_count': len(df),
                'columns': list(df.columns),
                'data_preview': df.head(5).to_dict('records'),  # First 5 rows for preview
                'data_summary': self.get_data_summary(df, data_type)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'File validation failed: {str(e)}'}
    
    def validate_data_types(self, df, data_type):
        """Validate data types in specific columns"""
        errors = []
        
        try:
            if data_type == 'workforce':
                # Check numeric columns
                numeric_cols = ['current_count', 'authorized_positions', 'filled_positions']
                for col in numeric_cols:
                    if col in df.columns:
                        if not pd.to_numeric(df[col], errors='coerce').notna().all():
                            errors.append(f"{col} must be numeric")
            
            elif data_type == 'population':
                # Check numeric columns
                numeric_cols = ['total_population', 'age_0_14', 'age_15_64', 'age_65_plus']
                for col in numeric_cols:
                    if col in df.columns:
                        if not pd.to_numeric(df[col], errors='coerce').notna().all():
                            errors.append(f"{col} must be numeric")
            
            elif data_type == 'health_conditions':
                # Check numeric columns
                numeric_cols = ['total_cases', 'prevalence_rate']
                for col in numeric_cols:
                    if col in df.columns:
                        if not pd.to_numeric(df[col], errors='coerce').notna().all():
                            errors.append(f"{col} must be numeric")
            
            elif data_type == 'training':
                # Check numeric columns
                numeric_cols = ['annual_capacity', 'current_enrollment', 'annual_graduates']
                for col in numeric_cols:
                    if col in df.columns:
                        if not pd.to_numeric(df[col], errors='coerce').notna().all():
                            errors.append(f"{col} must be numeric")
        
        except Exception as e:
            errors.append(f"Data type validation error: {str(e)}")
        
        return errors
    
    def get_data_summary(self, df, data_type):
        """Get basic summary statistics for the data"""
        summary = {
            'total_rows': len(df),
            'total_columns': len(df.columns)
        }
        
        try:
            if data_type == 'workforce':
                if 'current_count' in df.columns:
                    summary['total_workers'] = df['current_count'].sum()
                if 'region_name' in df.columns:
                    summary['regions_count'] = df['region_name'].nunique()
                if 'worker_category' in df.columns:
                    summary['categories_count'] = df['worker_category'].nunique()
            
            elif data_type == 'population':
                if 'total_population' in df.columns:
                    summary['total_population'] = df['total_population'].sum()
                if 'region_name' in df.columns:
                    summary['regions_count'] = df['region_name'].nunique()
            
            elif data_type == 'health_conditions':
                if 'total_cases' in df.columns:
                    summary['total_cases'] = df['total_cases'].sum()
                if 'condition_name' in df.columns:
                    summary['conditions_count'] = df['condition_name'].nunique()
            
            elif data_type == 'training':
                if 'annual_graduates' in df.columns:
                    summary['total_graduates'] = df['annual_graduates'].sum()
                if 'institution_name' in df.columns:
                    summary['institutions_count'] = df['institution_name'].nunique()
        
        except Exception as e:
            summary['error'] = f"Summary calculation error: {str(e)}"
        
        return summary
    
    def read_csv_data(self, file_path):
        """Read CSV data and return as DataFrame"""
        try:
            if file_path.endswith('.csv'):
                return pd.read_csv(file_path)
            else:
                return pd.read_excel(file_path)
        except Exception as e:
            raise Exception(f"Failed to read file: {str(e)}")
    
    def clean_uploaded_files(self, days_old=7):
        """Clean up old uploaded files"""
        try:
            current_time = datetime.now()
            for filename in os.listdir(self.upload_folder):
                file_path = os.path.join(self.upload_folder, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                
                if (current_time - file_time).days > days_old:
                    os.remove(file_path)
                    
        except Exception as e:
            print(f"Error cleaning files: {str(e)}")


# Helper functions for web interface
def get_file_info(file_path):
    """Get basic file information"""
    try:
        stat = os.stat(file_path)
        return {
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime)
        }
    except:
        return None 