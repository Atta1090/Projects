"""
Simplified CSV Upload Handler
Works without pandas - uses only Python standard library
"""

import csv
import os
from datetime import datetime
from werkzeug.utils import secure_filename


class SimpleCSVUploadHandler:
    """Simplified CSV handler using only standard library"""
    
    def __init__(self, upload_folder='uploads'):
        self.upload_folder = upload_folder
        self.allowed_extensions = {'csv'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
        # Create upload folder if it doesn't exist
        os.makedirs(upload_folder, exist_ok=True)
    
    def allowed_file(self, filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def detect_delimiter(self, file_path):
        """Detect CSV delimiter with robust fallback options"""
        common_delimiters = [',', ';', '\t', '|']
        
        try:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                # Read a larger sample for better detection
                sample = csvfile.read(4096)
                
                if not sample.strip():
                    return ','  # Default to comma if file is empty or whitespace
                
                # Try csv.Sniffer first
                try:
                    sniffer = csv.Sniffer()
                    delimiter = sniffer.sniff(sample).delimiter
                    # Validate that the detected delimiter is reasonable
                    if delimiter in common_delimiters or delimiter in sample:
                        return delimiter
                except:
                    pass  # Fall back to manual detection
                
                # Manual detection - count occurrences of common delimiters
                delimiter_counts = {}
                for delimiter in common_delimiters:
                    delimiter_counts[delimiter] = sample.count(delimiter)
                
                # Find the delimiter with the most occurrences
                if any(count > 0 for count in delimiter_counts.values()):
                    best_delimiter = max(delimiter_counts, key=delimiter_counts.get)
                    return best_delimiter
                
                # If no common delimiters found, default to comma
                return ','
                
        except Exception as e:
            print(f"Delimiter detection error: {e}")
            return ','  # Default fallback
    
    def validate_csv_with_delimiter(self, file_path, delimiter, data_type, required_columns):
        """Validate CSV with a specific delimiter"""
        try:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                # Check headers
                headers = reader.fieldnames
                if not headers:
                    return None
                
                # Clean headers (remove whitespace and normalize)
                headers = [header.strip() if header else '' for header in headers]
                
                # Check if we have the required columns
                missing_columns = []
                for col in required_columns[data_type]:
                    if col not in headers:
                        missing_columns.append(col)
                
                if missing_columns:
                    return {
                        'success': False,
                        'error': f'Missing required columns: {", ".join(missing_columns)}',
                        'required_columns': required_columns[data_type],
                        'found_columns': headers,
                        'delimiter_used': delimiter
                    }
                
                # Read data rows
                rows = []
                row_count = 0
                csvfile.seek(0)  # Reset file pointer
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                for row in reader:
                    # Clean row data
                    cleaned_row = {}
                    for key, value in row.items():
                        if key:
                            cleaned_row[key.strip()] = value.strip() if value else ''
                    rows.append(cleaned_row)
                    row_count += 1
                    if row_count >= 5:  # Only read first 5 for preview
                        break
                
                if row_count == 0:
                    return {'success': False, 'error': 'CSV file has no data rows'}
                
                return {
                    'success': True,
                    'row_count': row_count,
                    'columns': headers,
                    'data_preview': rows,
                    'delimiter_used': delimiter,
                    'data_summary': self.get_simple_summary(rows, data_type)
                }
                
        except Exception as e:
            return None
    
    def upload_file(self, file, data_type):
        """Upload and process CSV file using standard library"""
        try:
            # Validate file
            if not file or file.filename == '':
                return {'success': False, 'error': 'No file selected'}
            
            if not self.allowed_file(file.filename):
                return {'success': False, 'error': 'Only CSV files are supported in simple mode'}
            
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
                    'delimiter_used': validation_result.get('delimiter_used', 'auto'),
                    'upload_time': datetime.now().isoformat()
                }
            else:
                # Remove invalid file
                os.remove(file_path)
                return validation_result
                
        except Exception as e:
            return {'success': False, 'error': f'Upload failed: {str(e)}'}
    
    def validate_csv_data(self, file_path, data_type):
        """Validate CSV data using standard library with robust delimiter detection"""
        try:
            # Define required columns for each data type
            required_columns = {
                'workforce': ['region_name', 'worker_category', 'current_count', 'authorized_positions', 'filled_positions'],
                'population': ['region_name', 'total_population', 'age_0_14', 'age_15_64', 'age_65_plus'],
                'health_conditions': ['region_name', 'condition_name', 'total_cases', 'prevalence_rate'],
                'training': ['institution_name', 'program_type', 'annual_capacity', 'current_enrollment', 'annual_graduates']
            }
            
            if data_type not in required_columns:
                return {'success': False, 'error': f'Unknown data type: {data_type}'}
            
            # Detect delimiter
            delimiter = self.detect_delimiter(file_path)
            
            # Try to validate with detected delimiter
            result = self.validate_csv_with_delimiter(file_path, delimiter, data_type, required_columns)
            
            if result and result.get('success'):
                return result
            
            # If that fails, try common delimiters
            common_delimiters = [',', ';', '\t', '|']
            for test_delimiter in common_delimiters:
                if test_delimiter != delimiter:  # Skip the one we already tried
                    result = self.validate_csv_with_delimiter(file_path, test_delimiter, data_type, required_columns)
                    if result and result.get('success'):
                        return result
            
            # If all delimiter attempts fail, return the last error with helpful info
            return {
                'success': False, 
                'error': f'Could not parse CSV file. Please ensure your file uses common delimiters (comma, semicolon, tab) and has the required columns.',
                'required_columns': required_columns[data_type],
                'delimiter_tried': delimiter,
                'help': 'Try saving your Excel file as CSV (comma-separated) format'
            }
                
        except Exception as e:
            return {'success': False, 'error': f'File validation failed: {str(e)}'}
    
    def get_simple_summary(self, rows, data_type):
        """Get basic summary without pandas"""
        summary = {
            'total_rows': len(rows),
            'data_type': data_type
        }
        
        try:
            if data_type == 'workforce' and rows:
                # Simple workforce summary
                total_workers = sum(int(row.get('current_count', 0) or 0) for row in rows)
                regions = set(row.get('region_name', '') for row in rows if row.get('region_name'))
                categories = set(row.get('worker_category', '') for row in rows if row.get('worker_category'))
                
                summary.update({
                    'total_workers_sample': total_workers,
                    'regions_in_sample': len(regions),
                    'categories_in_sample': len(categories)
                })
            
            elif data_type == 'population' and rows:
                # Simple population summary
                total_pop = sum(int(row.get('total_population', 0) or 0) for row in rows)
                regions = set(row.get('region_name', '') for row in rows if row.get('region_name'))
                
                summary.update({
                    'total_population_sample': total_pop,
                    'regions_in_sample': len(regions)
                })
            
        except Exception as e:
            summary['error'] = f"Summary calculation error: {str(e)}"
        
        return summary
    
    def read_csv_data(self, file_path):
        """Read CSV data and return as list of dictionaries"""
        try:
            delimiter = self.detect_delimiter(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                rows = []
                for row in reader:
                    # Clean row data
                    cleaned_row = {}
                    for key, value in row.items():
                        if key:
                            cleaned_row[key.strip()] = value.strip() if value else ''
                    rows.append(cleaned_row)
                return rows
        except Exception as e:
            raise Exception(f"Failed to read file: {str(e)}")


class SimpleDataAnalyzer:
    """Simple data analyzer using only standard library"""
    
    def analyze_workforce_data(self, data_rows):
        """Simple workforce analysis"""
        try:
            total_workers = 0
            total_authorized = 0
            total_filled = 0
            regions = set()
            categories = set()
            
            for row in data_rows:
                try:
                    total_workers += int(row.get('current_count', 0) or 0)
                    total_authorized += int(row.get('authorized_positions', 0) or 0)
                    total_filled += int(row.get('filled_positions', 0) or 0)
                    
                    if row.get('region_name'):
                        regions.add(row['region_name'])
                    if row.get('worker_category'):
                        categories.add(row['worker_category'])
                except (ValueError, TypeError):
                    continue
            
            # Calculate vacancy rate
            vacancy_rate = 0
            if total_authorized > 0:
                vacancy_rate = ((total_authorized - total_filled) / total_authorized) * 100
            
            # Generate simple insights
            insights = []
            recommendations = []
            
            if vacancy_rate > 15:
                insights.append("🔴 HIGH ALERT: Overall vacancy rate exceeds 15% - critical staffing shortage")
                recommendations.append("🚀 URGENT: Launch emergency recruitment campaign")
                recommendations.append("💰 RETENTION: Increase salaries by 10-15% to reduce attrition")
            elif vacancy_rate > 10:
                insights.append("⚠️ WARNING: Vacancy rate above 10% - moderate staffing concerns")
                recommendations.append("📈 ATTENTION: Monitor staffing levels closely")
                recommendations.append("🎯 RECRUITMENT: Expand recruitment efforts")
            else:
                insights.append("✅ GOOD: Vacancy rate is manageable")
                recommendations.append("✅ MAINTAIN: Continue current staffing practices")
            
            # Regional insights
            if len(regions) > 1:
                insights.append(f"📍 COVERAGE: Data includes {len(regions)} regions")
                recommendations.append("🗺️ REGIONAL: Compare performance across regions")
            
            # Category insights
            if len(categories) > 1:
                insights.append(f"👥 CATEGORIES: Analysis covers {len(categories)} worker types")
                recommendations.append("📊 ANALYSIS: Review staffing by profession")
            
            return {
                'analysis_type': 'workforce',
                'analysis_date': datetime.now().isoformat(),
                'summary': {
                    'total_records': len(data_rows),
                    'total_workers': total_workers,
                    'total_authorized': total_authorized,
                    'total_filled': total_filled,
                    'vacancy_rate': round(vacancy_rate, 2),
                    'regions_covered': len(regions),
                    'categories_covered': len(categories)
                },
                'insights': insights,
                'recommendations': recommendations
            }
            
        except Exception as e:
            return {'error': f'Analysis failed: {str(e)}'}
    
    def analyze_other_data(self, data_rows, data_type):
        """Simple analysis for other data types"""
        insights = []
        recommendations = []
        
        if data_type == 'population':
            insights.append(f"📊 Uploaded {len(data_rows)} population records")
            recommendations.append("📈 Review population trends and demographics")
        elif data_type == 'health_conditions':
            insights.append(f"🏥 Uploaded {len(data_rows)} health condition records")
            recommendations.append("🎯 Focus on high-prevalence conditions")
        elif data_type == 'training':
            insights.append(f"🎓 Uploaded {len(data_rows)} training institution records")
            recommendations.append("📚 Analyze training capacity vs. demand")
        
        return {
            'analysis_type': data_type,
            'analysis_date': datetime.now().isoformat(),
            'summary': {
                'total_records': len(data_rows),
                'status': 'Basic analysis completed'
            },
            'insights': insights,
            'recommendations': recommendations
        } 