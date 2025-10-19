"""
CSV Analysis Routes
Web interface for uploading and analyzing CSV files
Supports both full mode (with pandas) and simple mode (standard library only)
"""

from flask import Blueprint, render_template_string, request, jsonify, send_file, Response
import os
from datetime import datetime
import io

# Import from the csv_analysis package which handles pandas availability
from app.csv_analysis import CSVUploadHandler, DataAnalyzer, PANDAS_AVAILABLE
from app.csv_analysis.csv_templates import get_all_templates, generate_sample_csv

# Create blueprint
csv_bp = Blueprint('csv_analysis', __name__, url_prefix='/csv')

# Initialize handlers
upload_handler = CSVUploadHandler()
analyzer = DataAnalyzer()

# Print mode information
if PANDAS_AVAILABLE:
    print("🐼 Pandas available - Full analysis mode enabled")
else:
    print("📊 Simple mode - Using standard library only")


@csv_bp.route('/')
def index():
    """CSV analysis main page"""
    mode = "Full Analysis Mode (with Pandas)" if PANDAS_AVAILABLE else "Simple Mode (Standard Library)"
    template = CSV_UPLOAD_TEMPLATE.replace("{{MODE}}", mode)
    return render_template_string(template)


@csv_bp.route('/templates')
def show_templates():
    """Show CSV templates and required attributes"""
    templates = get_all_templates()
    return jsonify({
        'success': True,
        'templates': templates,
        'mode': 'full' if PANDAS_AVAILABLE else 'simple'
    })


@csv_bp.route('/download-template/<template_type>')
def download_template(template_type):
    """Download sample CSV template - FIXED VERSION"""
    try:
        print(f"Download request for template: {template_type}")
        
        # Generate CSV content
        csv_content = generate_sample_csv(template_type)
        
        if not csv_content:
            print(f"Template not found: {template_type}")
            return jsonify({'success': False, 'error': 'Template not found'}), 404
        
        print(f"Generated CSV content length: {len(csv_content)}")
        
        # Create response with proper headers
        filename = f"sample_{template_type}_data.csv"
        
        # Create in-memory file to avoid disk I/O issues
        output = io.StringIO()
        output.write(csv_content)
        output.seek(0)
        
        # Convert to bytes for proper download
        csv_bytes = output.getvalue().encode('utf-8')
        
        # Create response
        response = Response(
            csv_bytes,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )
        
        print(f"Sending file: {filename}")
        return response
        
    except Exception as e:
        print(f"Download error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Download failed: {str(e)}'}), 500


@csv_bp.route('/download-template-alt/<template_type>')
def download_template_alt(template_type):
    """Alternative download method using file system"""
    try:
        csv_content = generate_sample_csv(template_type)
        
        if not csv_content:
            return jsonify({'success': False, 'error': 'Template not found'}), 404
        
        # Ensure uploads directory exists
        os.makedirs('uploads', exist_ok=True)
        
        # Create file with timestamp to avoid conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_filename = f"template_{template_type}_{timestamp}.csv"
        temp_path = os.path.join('uploads', temp_filename)
        
        # Write file
        with open(temp_path, 'w', encoding='utf-8', newline='') as f:
            f.write(csv_content)
        
        # Send file
        return send_file(
            temp_path, 
            as_attachment=True, 
            download_name=f"sample_{template_type}_data.csv",
            mimetype='text/csv'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@csv_bp.route('/test-download')
def test_download():
    """Test endpoint to verify download functionality"""
    try:
        # Simple test CSV
        test_csv = "name,value\nTest,123\nExample,456\n"
        
        response = Response(
            test_csv,
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename="test.csv"',
                'Content-Type': 'text/csv'
            }
        )
        
        return response
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@csv_bp.route('/upload', methods=['POST'])
def upload_csv():
    """Handle CSV file upload"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['file']
        data_type = request.form.get('data_type')
        
        if not data_type:
            return jsonify({'success': False, 'error': 'Data type not specified'})
        
        # Upload and validate file
        result = upload_handler.upload_file(file, data_type)
        
        if result['success']:
            # Perform analysis
            analysis_result = analyze_uploaded_file(result['file_path'], data_type)
            
            return jsonify({
                'success': True,
                'upload_info': result,
                'analysis': analysis_result,
                'mode': 'full' if PANDAS_AVAILABLE else 'simple'
            })
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Upload failed: {str(e)}'}), 500


@csv_bp.route('/analyze/<filename>')
def analyze_file(filename):
    """Analyze a specific uploaded file"""
    try:
        file_path = os.path.join(upload_handler.upload_folder, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # Determine data type from filename or request
        data_type = request.args.get('data_type', 'workforce')
        
        analysis_result = analyze_uploaded_file(file_path, data_type)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'analysis': analysis_result,
            'mode': 'full' if PANDAS_AVAILABLE else 'simple'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Analysis failed: {str(e)}'}), 500


def analyze_uploaded_file(file_path, data_type):
    """Analyze uploaded CSV file based on data type"""
    try:
        if PANDAS_AVAILABLE:
            # Full analysis with pandas
            df = upload_handler.read_csv_data(file_path)
            
            if data_type == 'workforce':
                return analyzer.analyze_workforce_data(df)
            elif data_type == 'population':
                return analyzer.analyze_population_data(df)
            elif data_type == 'health_conditions':
                return analyzer.analyze_health_conditions_data(df)
            elif data_type == 'training':
                return analyzer.analyze_training_data(df)
            else:
                return {'error': f'Unknown data type: {data_type}'}
        else:
            # Simple analysis without pandas
            data_rows = upload_handler.read_csv_data(file_path)
            
            if data_type == 'workforce':
                return analyzer.analyze_workforce_data(data_rows)
            else:
                return analyzer.analyze_other_data(data_rows, data_type)
            
    except Exception as e:
        return {'error': f'Analysis failed: {str(e)}'}


@csv_bp.route('/export-analysis/<filename>')
def export_analysis(filename):
    """Export analysis results"""
    try:
        file_path = os.path.join(upload_handler.upload_folder, filename)
        data_type = request.args.get('data_type', 'workforce')
        format_type = request.args.get('format', 'json')
        
        # Re-analyze file
        analysis_result = analyze_uploaded_file(file_path, data_type)
        
        # Export in requested format
        if PANDAS_AVAILABLE:
            export_content = analyzer.export_analysis_report(analysis_result, format_type)
        else:
            # Simple export for standard library mode
            if format_type == 'json':
                import json
                export_content = json.dumps(analysis_result, indent=2, default=str)
            else:
                export_content = f"""
HEALTHCARE WORKFORCE ANALYSIS REPORT
Generated: {analysis_result.get('analysis_date', 'Unknown')}
Analysis Type: {analysis_result.get('analysis_type', 'Unknown')}
Mode: Simple (Standard Library)

SUMMARY:
{_format_simple_summary(analysis_result.get('summary', {}))}

KEY INSIGHTS:
{_format_simple_list(analysis_result.get('insights', []))}

RECOMMENDATIONS:
{_format_simple_list(analysis_result.get('recommendations', []))}
"""
        
        if format_type == 'json':
            return jsonify({'success': True, 'content': export_content})
        else:
            # Return as text file
            export_filename = f"analysis_{filename.replace('.csv', '')}.txt"
            export_path = os.path.join('uploads', export_filename)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(export_content)
            
            return send_file(export_path, as_attachment=True, download_name=export_filename)
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def _format_simple_summary(summary):
    """Format summary for simple mode"""
    lines = []
    for key, value in summary.items():
        formatted_key = key.replace('_', ' ').title()
        if isinstance(value, (int, float)):
            lines.append(f"- {formatted_key}: {value:,}")
        else:
            lines.append(f"- {formatted_key}: {value}")
    return '\n'.join(lines)


def _format_simple_list(items):
    """Format list items for simple mode"""
    return '\n'.join(f"• {item}" for item in items)


# HTML Template for CSV Upload Interface
CSV_UPLOAD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>CSV Data Upload & Analysis - Healthcare Workforce Planning</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #e2e8f0;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .header p {
            font-size: 1.1rem;
            color: #94a3b8;
        }
        
        .mode-indicator {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid #10b981;
            border-radius: 6px;
            padding: 10px;
            margin: 20px 0;
            text-align: center;
            color: #6ee7b7;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }
        
        .upload-section, .templates-section {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid #475569;
            border-radius: 12px;
            padding: 30px;
            backdrop-filter: blur(10px);
        }
        
        .section-title {
            font-size: 1.5rem;
            margin-bottom: 20px;
            color: #10b981;
        }
        
        .upload-form {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .form-group label {
            font-weight: 600;
            color: #e2e8f0;
        }
        
        .form-group select, .form-group input[type="file"] {
            padding: 12px;
            border: 1px solid #475569;
            border-radius: 6px;
            background: #334155;
            color: #e2e8f0;
            font-size: 14px;
        }
        
        .form-group select:focus, .form-group input[type="file"]:focus {
            outline: none;
            border-color: #10b981;
        }
        
        .upload-btn {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .upload-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(16, 185, 129, 0.4);
        }
        
        .upload-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .template-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        
        .template-card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .template-card:hover {
            border-color: #10b981;
            transform: translateY(-2px);
        }
        
        .template-card h3 {
            color: #10b981;
            margin-bottom: 10px;
        }
        
        .template-card p {
            color: #94a3b8;
            font-size: 14px;
            margin-bottom: 15px;
        }
        
        .download-btn {
            background: #3b82f6;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .download-btn:hover {
            background: #2563eb;
        }
        
        .test-section {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid #475569;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .test-btn {
            background: #f59e0b;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        
        .results-section {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid #475569;
            border-radius: 12px;
            padding: 30px;
            backdrop-filter: blur(10px);
            display: none;
        }
        
        .results-section.show {
            display: block;
        }
        
        .analysis-summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .summary-card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }
        
        .summary-card h4 {
            color: #94a3b8;
            font-size: 14px;
            margin-bottom: 10px;
        }
        
        .summary-card .value {
            color: #10b981;
            font-size: 24px;
            font-weight: 700;
        }
        
        .insights-recommendations {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        
        .insights, .recommendations {
            background: #1e293b;
            border-radius: 8px;
            padding: 20px;
        }
        
        .insights h3, .recommendations h3 {
            color: #10b981;
            margin-bottom: 15px;
        }
        
        .insights ul, .recommendations ul {
            list-style: none;
        }
        
        .insights li, .recommendations li {
            padding: 8px 0;
            border-bottom: 1px solid #334155;
            color: #e2e8f0;
        }
        
        .insights li:last-child, .recommendations li:last-child {
            border-bottom: none;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #60a5fa;
        }
        
        .error {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid #ef4444;
            border-radius: 6px;
            padding: 15px;
            margin: 15px 0;
            color: #fecaca;
        }
        
        .success {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid #10b981;
            border-radius: 6px;
            padding: 15px;
            margin: 15px 0;
            color: #6ee7b7;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .template-grid {
                grid-template-columns: 1fr;
            }
            
            .insights-recommendations {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🏥 CSV Data Upload & Analysis</h1>
            <p>Upload your healthcare data and get instant insights</p>
            <div class="mode-indicator">
                📊 Running in: {{MODE}}
            </div>
        </div>
        
        <!-- Test Section -->
        <div class="test-section">
            <h3 style="color: #10b981; margin-bottom: 15px;">🧪 Test Download Functionality</h3>
            <p style="color: #94a3b8; margin-bottom: 15px;">Test the download system before using templates:</p>
            <button class="test-btn" onclick="testDownload()">Test Download</button>
            <button class="test-btn" onclick="downloadTemplate('workforce')">Test Workforce Template</button>
            <div id="testStatus"></div>
        </div>
        
        <!-- Main Content -->
        <div class="main-content">
            <!-- Upload Section -->
            <div class="upload-section">
                <h2 class="section-title">📊 Upload Your Data</h2>
                <form class="upload-form" id="uploadForm">
                    <div class="form-group">
                        <label for="dataType">Data Type:</label>
                        <select id="dataType" name="data_type" required>
                            <option value="">Select data type...</option>
                            <option value="workforce">Workforce Data</option>
                            <option value="population">Population Data</option>
                            <option value="health_conditions">Health Conditions</option>
                            <option value="training">Training Institutions</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="csvFile">CSV File:</label>
                        <input type="file" id="csvFile" name="file" accept=".csv" required>
                    </div>
                    
                    <button type="submit" class="upload-btn" id="uploadBtn">
                        📤 Upload & Analyze
                    </button>
                </form>
                
                <div id="uploadStatus"></div>
            </div>
            
            <!-- Templates Section -->
            <div class="templates-section">
                <h2 class="section-title">📋 CSV Templates</h2>
                <p style="margin-bottom: 20px; color: #94a3b8;">
                    Download sample templates to see what columns your CSV files should have:
                </p>
                
                <div class="template-grid">
                    <div class="template-card" onclick="downloadTemplate('workforce')">
                        <h3>👥 Workforce Data</h3>
                        <p>Track healthcare workers by region and category</p>
                        <button class="download-btn">Download Template</button>
                    </div>
                    
                    <div class="template-card" onclick="downloadTemplate('population')">
                        <h3>🌍 Population Data</h3>
                        <p>Regional population and demographics</p>
                        <button class="download-btn">Download Template</button>
                    </div>
                    
                    <div class="template-card" onclick="downloadTemplate('health_conditions')">
                        <h3>🏥 Health Conditions</h3>
                        <p>Disease prevalence and health statistics</p>
                        <button class="download-btn">Download Template</button>
                    </div>
                    
                    <div class="template-card" onclick="downloadTemplate('training')">
                        <h3>🎓 Training Institutions</h3>
                        <p>Medical schools and education capacity</p>
                        <button class="download-btn">Download Template</button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Results Section -->
        <div class="results-section" id="resultsSection">
            <h2 class="section-title">📈 Analysis Results</h2>
            <div id="analysisContent"></div>
        </div>
    </div>
    
    <script>
        // Test download functionality
        async function testDownload() {
            const statusDiv = document.getElementById('testStatus');
            statusDiv.innerHTML = '<div style="color: #60a5fa;">Testing download...</div>';
            
            try {
                const response = await fetch('/csv/test-download');
                
                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'test.csv';
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    statusDiv.innerHTML = '<div style="color: #10b981;">✅ Download test successful!</div>';
                } else {
                    statusDiv.innerHTML = '<div style="color: #ef4444;">❌ Download test failed</div>';
                }
            } catch (error) {
                statusDiv.innerHTML = `<div style="color: #ef4444;">❌ Error: ${error.message}</div>`;
            }
        }
        
        // Handle form submission
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const uploadBtn = document.getElementById('uploadBtn');
            const statusDiv = document.getElementById('uploadStatus');
            const resultsSection = document.getElementById('resultsSection');
            
            // Show loading state
            uploadBtn.disabled = true;
            uploadBtn.textContent = '⏳ Uploading & Analyzing...';
            statusDiv.innerHTML = '<div class="loading">Processing your file...</div>';
            resultsSection.classList.remove('show');
            
            try {
                const response = await fetch('/csv/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    statusDiv.innerHTML = '<div class="success">✅ File uploaded and analyzed successfully!</div>';
                    displayAnalysisResults(result.analysis);
                    resultsSection.classList.add('show');
                } else {
                    statusDiv.innerHTML = `<div class="error">❌ Error: ${result.error}</div>`;
                }
                
            } catch (error) {
                statusDiv.innerHTML = `<div class="error">❌ Upload failed: ${error.message}</div>`;
            } finally {
                uploadBtn.disabled = false;
                uploadBtn.textContent = '📤 Upload & Analyze';
            }
        });
        
        // Download template function - IMPROVED VERSION
        async function downloadTemplate(templateType) {
            const statusDiv = document.getElementById('testStatus');
            statusDiv.innerHTML = `<div style="color: #60a5fa;">Downloading ${templateType} template...</div>`;
            
            try {
                console.log('Requesting template:', templateType);
                const response = await fetch(`/csv/download-template/${templateType}`);
                
                console.log('Response status:', response.status);
                console.log('Response headers:', response.headers);
                
                if (response.ok) {
                    const blob = await response.blob();
                    console.log('Blob size:', blob.size);
                    
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `sample_${templateType}_data.csv`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    
                    statusDiv.innerHTML = `<div style="color: #10b981;">✅ ${templateType} template downloaded!</div>`;
                } else {
                    const errorText = await response.text();
                    console.error('Download failed:', errorText);
                    statusDiv.innerHTML = `<div style="color: #ef4444;">❌ Download failed: ${response.status}</div>`;
                    
                    // Try alternative method
                    console.log('Trying alternative download method...');
                    const altResponse = await fetch(`/csv/download-template-alt/${templateType}`);
                    if (altResponse.ok) {
                        const blob = await altResponse.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `sample_${templateType}_data.csv`;
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                        document.body.removeChild(a);
                        statusDiv.innerHTML = `<div style="color: #10b981;">✅ ${templateType} template downloaded (alt method)!</div>`;
                    }
                }
            } catch (error) {
                console.error('Download error:', error);
                statusDiv.innerHTML = `<div style="color: #ef4444;">❌ Download failed: ${error.message}</div>`;
            }
        }
        
        // Display analysis results
        function displayAnalysisResults(analysis) {
            const contentDiv = document.getElementById('analysisContent');
            
            if (analysis.error) {
                contentDiv.innerHTML = `<div class="error">Analysis Error: ${analysis.error}</div>`;
                return;
            }
            
            const summary = analysis.summary || {};
            const insights = analysis.insights || [];
            const recommendations = analysis.recommendations || [];
            
            let summaryCards = '';
            for (const [key, value] of Object.entries(summary)) {
                const formattedKey = key.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
                const formattedValue = typeof value === 'number' ? value.toLocaleString() : value;
                summaryCards += `
                    <div class="summary-card">
                        <h4>${formattedKey}</h4>
                        <div class="value">${formattedValue}</div>
                    </div>
                `;
            }
            
            const insightsList = insights.map(insight => `<li>${insight}</li>`).join('');
            const recommendationsList = recommendations.map(rec => `<li>${rec}</li>`).join('');
            
            contentDiv.innerHTML = `
                <div class="analysis-summary">
                    ${summaryCards}
                </div>
                
                <div class="insights-recommendations">
                    <div class="insights">
                        <h3>💡 Key Insights</h3>
                        <ul>${insightsList}</ul>
                    </div>
                    
                    <div class="recommendations">
                        <h3>🎯 Recommendations</h3>
                        <ul>${recommendationsList}</ul>
                    </div>
                </div>
            `;
        }
        
        console.log('🏥 CSV Upload & Analysis System Ready - Enhanced Download Version');
    </script>
</body>
</html>
''' 