# Saudi Arabia Health Workforce Planning System

## 🚀 **Quick Start**

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Start the System**
```bash
python run.py
```

### **3. Access the System**
- **Homepage**: http://localhost:5000
- **File Import**: http://localhost:5000/csv/
- **Dashboard**: http://localhost:5000/dashboard
- **Login**: http://localhost:5000/auth/login (Demo: demo@health.gov.sa / demo123456)

## 📁 **Clean Project Structure**

```
html-frontend/
├── app/                    # Flask application backend
│   ├── auth/              # Authentication module
│   ├── analytics/         # Projections, scenarios, reports
│   ├── csv_analysis/      # File upload & analysis
│   ├── dashboard/         # Main dashboard
│   ├── workforce/         # Workforce analysis
│   ├── models/            # Database models
│   └── services/          # Business logic
├── assets/                # CSS, JS, images
├── pages/                 # HTML frontend pages
├── uploads/               # Sample CSV templates
├── config.py             # Configuration
├── run.py                # Main application starter
├── requirements.txt      # Dependencies
├── index.html           # Homepage
└── dashboard.html       # Dashboard page
```

## 🎯 **Key Features**

### **📊 Data Import & Analysis**
- **CSV/Excel Upload**: Bulk data import with validation
- **Sample Templates**: Pre-built templates for all data types
- **Real-time Analysis**: Instant insights and gap analysis
- **Export Options**: Download results in multiple formats

### **📈 Real-Time Dashboard**
- **Live Metrics**: Workforce distribution across 13 Saudi regions
- **Gap Analysis**: Automatic shortage/surplus identification
- **Visual Charts**: Interactive data visualizations
- **Executive Summary**: Key performance indicators

### **🔮 Predictive Analytics**
- **10-Year Projections**: Monte Carlo simulations with confidence intervals
- **Supply & Demand**: Workforce forecasting by specialty and region
- **Scenario Planning**: "What-if" analysis for policy decisions
- **Training Analytics**: Education capacity and graduate projections

### **📋 Comprehensive Reporting**
- **Executive Reports**: Summary reports for decision makers
- **Regional Analysis**: Detailed breakdown by region
- **Specialty Reports**: Analysis by healthcare specialty
- **Export Formats**: PDF, Excel, CSV downloads

## 🎯 **Sample Data Templates**

The system includes sample CSV templates in the `/uploads/` directory:

- **📊 sample_workforce_data.csv** - Healthcare worker data template
- **🌍 sample_population_data.csv** - Population demographics template  
- **🏥 sample_health_conditions_data.csv** - Health conditions template
- **🎓 sample_training_data.csv** - Training institutions template

## 🔐 **Demo Login**

**Email**: demo@health.gov.sa  
**Password**: demo123456

## 🏗️ **Technology Stack**

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite (development), PostgreSQL (production)
- **Analytics**: Pandas, NumPy, Scikit-learn
- **Visualization**: Plotly, Matplotlib, Seaborn

## 🌍 **Saudi Arabia Focus**

- **13 Regions Coverage**: All Saudi administrative regions
- **Arabic/English Support**: Bilingual interface
- **50+ Medical Specialties**: Complete healthcare categorization
- **Vision 2030 Aligned**: Supporting national healthcare goals
- **Government Grade Security**: Enterprise-level security standards

## 🛠️ **Development**

### **Database Initialization**
The system automatically creates and seeds the database with Saudi-specific data on first run.

### **Configuration**
Edit `config.py` to customize:
- Database settings
- Security configurations  
- API settings
- Saudi-specific parameters

### **Extensions**
The modular design allows easy extension of:
- New data types and templates
- Additional analytics modules
- Custom reporting formats
- Integration with external systems

---

## 📞 **Support**

For technical support or questions about the Healthcare Workforce Planning System, please refer to the system documentation or contact the development team.

**System Status**: ✅ Production Ready  
**Last Updated**: January 2025  
**Version**: 1.0 