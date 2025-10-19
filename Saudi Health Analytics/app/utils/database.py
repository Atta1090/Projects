"""
Database Initialization and Data Seeding
Creates comprehensive dummy data for Saudi Arabian healthcare workforce planning
"""

from datetime import datetime, timedelta
import random
from app import db
from app.models.user import User
from app.models.region import Region
from app.models.healthcare_worker import HealthcareWorkerCategory
from app.models.workforce import WorkforceStock
from app.models.population import PopulationData
from app.models.health_status import HealthCondition
from app.models.service_standards import ServiceStandard


def init_database():
    """Initialize database with comprehensive Saudi Arabian healthcare data"""
    try:
        print("🏥 Initializing Saudi Healthcare Workforce Database...")
        
        # Create all tables
        db.create_all()
        
        # Clear existing data
        clear_existing_data()
        
        # Seed data in order (foreign key dependencies)
        seed_users()
        seed_regions()
        seed_healthcare_categories()
        seed_workforce_data()
        seed_population_data()
        seed_health_conditions()
        seed_service_standards()
        
        # Commit all changes
        db.session.commit()
        
        print("✅ Database initialized successfully with comprehensive data!")
        print(f"📊 Data includes:")
        print(f"   • {Region.query.count()} Saudi regions")
        print(f"   • {HealthcareWorkerCategory.query.count()} healthcare worker categories")
        print(f"   • {WorkforceStock.query.count()} workforce records")
        print(f"   • {PopulationData.query.count()} population records")
        print(f"   • {HealthCondition.query.count()} health condition records")
        print(f"   • {ServiceStandard.query.count()} service standards")
        
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        db.session.rollback()
        raise


def clear_existing_data():
    """Clear existing data for fresh start"""
    print("🧹 Clearing existing data...")
    
    # Clear in reverse order of dependencies
    ServiceStandard.query.delete()
    HealthCondition.query.delete()
    PopulationData.query.delete()
    WorkforceStock.query.delete()
    HealthcareWorkerCategory.query.delete()
    Region.query.delete()
    User.query.delete()


def seed_users():
    """Create default users for the system"""
    print("👥 Creating system users...")
    
    users = [
        {
            'username': 'admin',
            'email': 'admin@moh.gov.sa',
            'first_name': 'System',
            'last_name': 'Administrator',
            'role': 'admin',
            'department': 'Ministry of Health',
            'is_confirmed': True,
            'is_active': True
        },
        {
            'username': 'riyadh.director',
            'email': 'director@riyadh.health.gov.sa',
            'first_name': 'Ahmed',
            'last_name': 'Al-Rashid',
            'role': 'regional_director',
            'department': 'Riyadh Health Directorate',
            'is_confirmed': True,
            'is_active': True
        },
        {
            'username': 'analyst',
            'email': 'analyst@moh.gov.sa',
            'first_name': 'Fatima',
            'last_name': 'Al-Zahra',
            'role': 'analyst',
            'department': 'Planning & Development',
            'is_confirmed': True,
            'is_active': True
        }
    ]
    
    for user_data in users:
        user = User(**user_data)
        user.set_password('healthcare2024')  # Default password
        db.session.add(user)


def seed_regions():
    """Create all 13 Saudi Arabian regions with realistic data"""
    print("🌍 Creating Saudi Arabian regions...")
    
    regions_data = [
        {
            'name_en': 'Riyadh',
            'name_ar': 'الرياض',
            'region_code': 'RD',
            'capital_city': 'Riyadh',
            'area_km2': 380000,
            'total_population': 8216284,
            'saudi_population': 5188258,
            'non_saudi_population': 3028026,
            'urban_population': 7500000,
            'rural_population': 716284,
            'population_density': 21.6,
            'hospitals_count': 158,
            'health_centers_count': 542,
            'gdp_per_capita': 95000,
            'coordinates_lat': 24.7136,
            'coordinates_lng': 46.6753
        },
        {
            'name_en': 'Makkah',
            'name_ar': 'مكة المكرمة',
            'region_code': 'MK',
            'capital_city': 'Makkah',
            'area_km2': 164000,
            'total_population': 8557766,
            'saudi_population': 5284845,
            'non_saudi_population': 3272921,
            'urban_population': 7800000,
            'rural_population': 757766,
            'population_density': 52.2,
            'hospitals_count': 142,
            'health_centers_count': 487,
            'gdp_per_capita': 78000,
            'coordinates_lat': 21.3891,
            'coordinates_lng': 39.8579
        },
        {
            'name_en': 'Eastern Province',
            'name_ar': 'المنطقة الشرقية',
            'region_code': 'EP',
            'capital_city': 'Dammam',
            'area_km2': 672000,
            'total_population': 5120567,
            'saudi_population': 3276363,
            'non_saudi_population': 1844204,
            'urban_population': 4600000,
            'rural_population': 520567,
            'population_density': 7.6,
            'hospitals_count': 98,
            'health_centers_count': 324,
            'gdp_per_capita': 112000,
            'coordinates_lat': 26.4207,
            'coordinates_lng': 50.0888
        },
        {
            'name_en': 'Asir',
            'name_ar': 'عسير',
            'region_code': 'AS',
            'capital_city': 'Abha',
            'area_km2': 76000,
            'total_population': 2211875,
            'saudi_population': 1974798,
            'non_saudi_population': 237077,
            'urban_population': 1450000,
            'rural_population': 761875,
            'population_density': 29.1,
            'hospitals_count': 54,
            'health_centers_count': 189,
            'gdp_per_capita': 45000,
            'coordinates_lat': 18.2465,
            'coordinates_lng': 42.5326
        },
        {
            'name_en': 'Jazan',
            'name_ar': 'جازان',
            'region_code': 'JZ',
            'capital_city': 'Jazan',
            'area_km2': 11000,
            'total_population': 1567547,
            'saudi_population': 1465221,
            'non_saudi_population': 102326,
            'urban_population': 980000,
            'rural_population': 587547,
            'population_density': 142.5,
            'hospitals_count': 28,
            'health_centers_count': 156,
            'gdp_per_capita': 38000,
            'coordinates_lat': 16.8892,
            'coordinates_lng': 42.5511
        },
        {
            'name_en': 'Medina',
            'name_ar': 'المدينة المنورة',
            'region_code': 'MD',
            'capital_city': 'Medina',
            'area_km2': 151000,
            'total_population': 2132679,
            'saudi_population': 1678291,
            'non_saudi_population': 454388,
            'urban_population': 1850000,
            'rural_population': 282679,
            'population_density': 14.1,
            'hospitals_count': 45,
            'health_centers_count': 178,
            'gdp_per_capita': 68000,
            'coordinates_lat': 24.5247,
            'coordinates_lng': 39.5692
        },
        {
            'name_en': 'Qassim',
            'name_ar': 'القصيم',
            'region_code': 'QS',
            'capital_city': 'Buraydah',
            'area_km2': 58000,
            'total_population': 1370727,
            'saudi_population': 1215392,
            'non_saudi_population': 155335,
            'urban_population': 1100000,
            'rural_population': 270727,
            'population_density': 23.6,
            'hospitals_count': 32,
            'health_centers_count': 142,
            'gdp_per_capita': 52000,
            'coordinates_lat': 26.3260,
            'coordinates_lng': 43.9750
        },
        {
            'name_en': 'Hail',
            'name_ar': 'حائل',
            'region_code': 'HL',
            'capital_city': 'Hail',
            'area_km2': 103000,
            'total_population': 731147,
            'saudi_population': 670891,
            'non_saudi_population': 60256,
            'urban_population': 550000,
            'rural_population': 181147,
            'population_density': 7.1,
            'hospitals_count': 18,
            'health_centers_count': 89,
            'gdp_per_capita': 47000,
            'coordinates_lat': 27.5114,
            'coordinates_lng': 41.6900
        },
        {
            'name_en': 'Tabuk',
            'name_ar': 'تبوك',
            'region_code': 'TB',
            'capital_city': 'Tabuk',
            'area_km2': 117000,
            'total_population': 910030,
            'saudi_population': 807642,
            'non_saudi_population': 102388,
            'urban_population': 720000,
            'rural_population': 190030,
            'population_density': 7.8,
            'hospitals_count': 22,
            'health_centers_count': 98,
            'gdp_per_capita': 49000,
            'coordinates_lat': 28.3998,
            'coordinates_lng': 36.5709
        },
        {
            'name_en': 'Northern Borders',
            'name_ar': 'الحدود الشمالية',
            'region_code': 'NB',
            'capital_city': 'Arar',
            'area_km2': 104000,
            'total_population': 373556,
            'saudi_population': 339711,
            'non_saudi_population': 33845,
            'urban_population': 280000,
            'rural_population': 93556,
            'population_density': 3.6,
            'hospitals_count': 12,
            'health_centers_count': 45,
            'gdp_per_capita': 44000,
            'coordinates_lat': 30.9758,
            'coordinates_lng': 41.0378
        },
        {
            'name_en': 'Najran',
            'name_ar': 'نجران',
            'region_code': 'NJ',
            'capital_city': 'Najran',
            'area_km2': 149000,
            'total_population': 595705,
            'saudi_population': 567928,
            'non_saudi_population': 27777,
            'urban_population': 420000,
            'rural_population': 175705,
            'population_density': 4.0,
            'hospitals_count': 16,
            'health_centers_count': 67,
            'gdp_per_capita': 41000,
            'coordinates_lat': 17.4924,
            'coordinates_lng': 44.1277
        },
        {
            'name_en': 'Al Bahah',
            'name_ar': 'الباحة',
            'region_code': 'BH',
            'capital_city': 'Al Bahah',
            'area_km2': 9000,
            'total_population': 476172,
            'saudi_population': 452311,
            'non_saudi_population': 23861,
            'urban_population': 300000,
            'rural_population': 176172,
            'population_density': 52.9,
            'hospitals_count': 14,
            'health_centers_count': 78,
            'gdp_per_capita': 43000,
            'coordinates_lat': 20.0129,
            'coordinates_lng': 41.4687
        },
        {
            'name_en': 'Al Jouf',
            'name_ar': 'الجوف',
            'region_code': 'JF',
            'capital_city': 'Sakaka',
            'area_km2': 100000,
            'total_population': 508475,
            'saudi_population': 463218,
            'non_saudi_population': 45257,
            'urban_population': 380000,
            'rural_population': 128475,
            'population_density': 5.1,
            'hospitals_count': 15,
            'health_centers_count': 62,
            'gdp_per_capita': 46000,
            'coordinates_lat': 29.8547,
            'coordinates_lng': 40.2098
        }
    ]
    
    for region_data in regions_data:
        region = Region(**region_data)
        db.session.add(region)


def seed_healthcare_categories():
    """Create healthcare worker categories with realistic Saudi data"""
    print("🏥 Creating healthcare worker categories...")
    
    categories_data = [
        {
            'name_en': 'Physicians',
            'name_ar': 'الأطباء',
            'category_code': 'PHY',
            'category_level': 1,
            'description_en': 'Medical doctors across all specialties',
            'description_ar': 'الأطباء عبر جميع التخصصات',
            'minimum_education': 'Medical Degree (MBBS/MD)',
            'license_required': True,
            'professional_body': 'Saudi Commission for Health Specialties',
            'average_salary': 180000,
            'work_hours_per_week': 48,
            'patient_ratio': 1500,
            'training_duration_months': 72,
            'continuing_education_hours': 50,
            'is_critical_shortage': True
        },
        {
            'name_en': 'Nurses',
            'name_ar': 'الممرضون',
            'category_code': 'NUR',
            'category_level': 1,
            'description_en': 'Registered nurses providing patient care',
            'description_ar': 'الممرضون المسجلون الذين يقدمون رعاية المرضى',
            'minimum_education': 'Bachelor of Nursing',
            'license_required': True,
            'professional_body': 'Saudi Commission for Health Specialties',
            'average_salary': 120000,
            'work_hours_per_week': 40,
            'patient_ratio': 8,
            'training_duration_months': 48,
            'continuing_education_hours': 40,
            'is_critical_shortage': True
        },
        {
            'name_en': 'Pharmacists',
            'name_ar': 'الصيادلة',
            'category_code': 'PHA',
            'category_level': 1,
            'description_en': 'Licensed pharmacists managing medication therapy',
            'description_ar': 'الصيادلة المرخصون المسؤولون عن العلاج الدوائي',
            'minimum_education': 'Doctor of Pharmacy (PharmD)',
            'license_required': True,
            'professional_body': 'Saudi Commission for Health Specialties',
            'average_salary': 140000,
            'work_hours_per_week': 40,
            'patient_ratio': 2000,
            'training_duration_months': 60,
            'continuing_education_hours': 30,
            'is_critical_shortage': False
        },
        {
            'name_en': 'Medical Technicians',
            'name_ar': 'التقنيون الطبيون',
            'category_code': 'MTC',
            'category_level': 2,
            'description_en': 'Medical laboratory and radiology technicians',
            'description_ar': 'تقنيو المختبرات الطبية والأشعة',
            'minimum_education': 'Associate Degree in Medical Technology',
            'license_required': True,
            'professional_body': 'Saudi Commission for Health Specialties',
            'average_salary': 85000,
            'work_hours_per_week': 40,
            'patient_ratio': 500,
            'training_duration_months': 24,
            'continuing_education_hours': 25,
            'is_critical_shortage': False
        },
        {
            'name_en': 'Dentists',
            'name_ar': 'أطباء الأسنان',
            'category_code': 'DEN',
            'category_level': 1,
            'description_en': 'Dental practitioners and specialists',
            'description_ar': 'ممارسو طب الأسنان والمتخصصون',
            'minimum_education': 'Doctor of Dental Surgery (DDS)',
            'license_required': True,
            'professional_body': 'Saudi Commission for Health Specialties',
            'average_salary': 160000,
            'work_hours_per_week': 40,
            'patient_ratio': 1800,
            'training_duration_months': 60,
            'continuing_education_hours': 40,
            'is_critical_shortage': False
        },
        {
            'name_en': 'Mental Health Specialists',
            'name_ar': 'أخصائيو الصحة النفسية',
            'category_code': 'MHS',
            'category_level': 1,
            'description_en': 'Psychiatrists and clinical psychologists',
            'description_ar': 'أطباء نفسيون وأخصائيون نفسيون إكلينيكيون',
            'minimum_education': 'Medical Degree + Psychiatry Residency',
            'license_required': True,
            'professional_body': 'Saudi Commission for Health Specialties',
            'average_salary': 200000,
            'work_hours_per_week': 40,
            'patient_ratio': 800,
            'training_duration_months': 60,
            'continuing_education_hours': 45,
            'is_critical_shortage': True
        },
        {
            'name_en': 'Emergency Medicine Physicians',
            'name_ar': 'أطباء الطوارئ',
            'category_code': 'EMP',
            'category_level': 2,
            'description_en': 'Emergency department physicians',
            'description_ar': 'أطباء أقسام الطوارئ',
            'minimum_education': 'Medical Degree + Emergency Medicine Residency',
            'license_required': True,
            'professional_body': 'Saudi Commission for Health Specialties',
            'average_salary': 220000,
            'work_hours_per_week': 48,
            'patient_ratio': 1200,
            'training_duration_months': 48,
            'continuing_education_hours': 60,
            'is_critical_shortage': True
        },
        {
            'name_en': 'Physiotherapists',
            'name_ar': 'أخصائيو العلاج الطبيعي',
            'category_code': 'PHT',
            'category_level': 2,
            'description_en': 'Physical therapy specialists',
            'description_ar': 'أخصائيو العلاج الطبيعي',
            'minimum_education': 'Bachelor in Physiotherapy',
            'license_required': True,
            'professional_body': 'Saudi Commission for Health Specialties',
            'average_salary': 110000,
            'work_hours_per_week': 40,
            'patient_ratio': 50,
            'training_duration_months': 48,
            'continuing_education_hours': 30,
            'is_critical_shortage': False
        }
    ]
    
    for category_data in categories_data:
        category = HealthcareWorkerCategory(**category_data)
        db.session.add(category)


def seed_workforce_data():
    """Create comprehensive workforce data for all regions and categories"""
    print("👥 Creating workforce data...")
    
    # Get all regions and categories
    regions = Region.query.all()
    categories = HealthcareWorkerCategory.query.all()
    current_year = datetime.now().year
    
    # Base workforce numbers (will be adjusted by region size)
    base_workforce = {
        'PHY': {'current': 8500, 'authorized': 10200, 'filled': 8100},  # Physicians
        'NUR': {'current': 15200, 'authorized': 18500, 'filled': 14800},  # Nurses
        'PHA': {'current': 3200, 'authorized': 3800, 'filled': 3150},   # Pharmacists
        'MTC': {'current': 2800, 'authorized': 3200, 'filled': 2750},   # Medical Technicians
        'DEN': {'current': 1200, 'authorized': 1400, 'filled': 1180},   # Dentists
        'MHS': {'current': 650, 'authorized': 950, 'filled': 620},      # Mental Health
        'EMP': {'current': 480, 'authorized': 650, 'filled': 460},      # Emergency Medicine
        'PHT': {'current': 920, 'authorized': 1100, 'filled': 900}      # Physiotherapists
    }
    
    for region in regions:
        # Calculate region factor based on population
        region_factor = region.total_population / 35000000  # National population
        
        for category in categories:
            if category.category_code in base_workforce:
                base_data = base_workforce[category.category_code]
                
                # Calculate region-specific numbers
                current_count = int(base_data['current'] * region_factor)
                authorized = int(base_data['authorized'] * region_factor)
                filled = int(base_data['filled'] * region_factor)
                
                # Add some randomness for realism
                current_count += random.randint(-50, 50)
                authorized += random.randint(-20, 30)
                filled += random.randint(-30, 20)
                
                # Ensure logical constraints
                current_count = max(0, current_count)
                authorized = max(current_count, authorized)
                filled = min(current_count, max(0, filled))
                
                # Calculate demographics
                saudi_count = int(current_count * random.uniform(0.65, 0.85))  # 65-85% Saudi
                male_count = int(current_count * random.uniform(0.45, 0.75))   # Gender distribution
                female_count = current_count - male_count
                
                # Age distribution
                age_20_30 = int(current_count * random.uniform(0.25, 0.35))
                age_31_40 = int(current_count * random.uniform(0.30, 0.40))
                age_41_50 = int(current_count * random.uniform(0.20, 0.30))
                age_51_60 = current_count - age_20_30 - age_31_40 - age_41_50
                
                # Experience distribution
                exp_0_5 = int(current_count * random.uniform(0.30, 0.40))
                exp_6_10 = int(current_count * random.uniform(0.25, 0.35))
                exp_11_15 = int(current_count * random.uniform(0.15, 0.25))
                exp_16_plus = current_count - exp_0_5 - exp_6_10 - exp_11_15
                
                workforce_record = WorkforceStock(
                    region_id=region.id,
                    worker_category_id=category.id,
                    data_year=current_year,
                    data_quarter=4,
                    data_month=12,
                    current_count=current_count,
                    authorized_positions=authorized,
                    filled_positions=filled,
                    vacant_positions=authorized - filled,
                    saudi_count=saudi_count,
                    non_saudi_count=current_count - saudi_count,
                    male_count=male_count,
                    female_count=female_count,
                    age_20_30=age_20_30,
                    age_31_40=age_31_40,
                    age_41_50=age_41_50,
                    age_51_60=age_51_60,
                    experience_0_5=exp_0_5,
                    experience_6_10=exp_6_10,
                    experience_11_15=exp_11_15,
                    experience_16_plus=exp_16_plus,
                    new_hires_count=int(current_count * random.uniform(0.08, 0.15)),
                    resignation_count=int(current_count * random.uniform(0.05, 0.12)),
                    retirement_count=int(current_count * random.uniform(0.02, 0.05)),
                    transfer_in_count=int(current_count * random.uniform(0.03, 0.08)),
                    transfer_out_count=int(current_count * random.uniform(0.03, 0.08)),
                    attrition_rate=random.uniform(8.5, 15.2),
                    productivity_index=random.uniform(75.0, 95.0),
                    average_salary=category.average_salary + random.randint(-15000, 25000),
                    overtime_hours_avg=random.uniform(5.0, 12.0),
                    training_hours_completed=random.uniform(20.0, 45.0),
                    performance_rating_avg=random.uniform(3.2, 4.8),
                    is_active=True,
                    notes=f"Generated data for {region.name_en} - {category.name_en}",
                    created_by=1,
                    updated_by=1
                )
                
                db.session.add(workforce_record)


def seed_population_data():
    """Create population data for all regions"""
    print("🌍 Creating population data...")
    
    regions = Region.query.all()
    current_year = datetime.now().year
    
    for region in regions:
        # Use existing region population data as base
        total_pop = region.total_population
        saudi_pop = region.saudi_population
        
        # Calculate age distribution (realistic for Saudi Arabia)
        age_0_14 = int(total_pop * random.uniform(0.24, 0.28))    # Young population
        age_15_29 = int(total_pop * random.uniform(0.28, 0.32))   # Working age
        age_30_44 = int(total_pop * random.uniform(0.22, 0.26))   # Prime working age
        age_45_59 = int(total_pop * random.uniform(0.12, 0.16))   # Senior working age
        age_60_plus = total_pop - age_0_14 - age_15_29 - age_30_44 - age_45_59
        
        # Gender distribution
        male_count = int(total_pop * random.uniform(0.52, 0.58))  # Male majority due to expats
        female_count = total_pop - male_count
        
        # Education distribution
        illiterate = int(total_pop * random.uniform(0.05, 0.12))
        primary = int(total_pop * random.uniform(0.15, 0.22))
        secondary = int(total_pop * random.uniform(0.25, 0.32))
        university = int(total_pop * random.uniform(0.28, 0.35))
        postgraduate = total_pop - illiterate - primary - secondary - university
        
        population_record = PopulationData(
            region_id=region.id,
            data_year=current_year,
            data_quarter=4,
            total_population=total_pop,
            saudi_count=saudi_pop,
            non_saudi_count=total_pop - saudi_pop,
            male_count=male_count,
            female_count=female_count,
            age_0_14=age_0_14,
            age_15_29=age_15_29,
            age_30_44=age_30_44,
            age_45_59=age_45_59,
            age_60_plus=age_60_plus,
            urban_population=region.urban_population,
            rural_population=region.rural_population,
            education_illiterate=illiterate,
            education_primary=primary,
            education_secondary=secondary,
            education_university=university,
            education_postgraduate=postgraduate,
            birth_rate=random.uniform(15.2, 22.8),
            death_rate=random.uniform(3.1, 4.8),
            infant_mortality_rate=random.uniform(6.2, 12.5),
            life_expectancy_male=random.uniform(72.5, 76.2),
            life_expectancy_female=random.uniform(76.8, 80.5),
            unemployment_rate=random.uniform(5.6, 12.3),
            labor_force_participation=random.uniform(58.2, 67.8),
            household_size_avg=random.uniform(5.2, 6.8),
            poverty_rate=random.uniform(2.1, 8.5),
            health_insurance_coverage=random.uniform(87.5, 96.2),
            chronic_disease_prevalence=random.uniform(18.5, 28.7),
            is_active=True,
            created_by=1,
            updated_by=1
        )
        
        db.session.add(population_record)


def seed_health_conditions():
    """Create health condition data tracking disease prevalence"""
    print("🏥 Creating health condition data...")
    
    regions = Region.query.all()
    current_year = datetime.now().year
    
    # Common health conditions in Saudi Arabia
    conditions_data = [
        {
            'name_en': 'Diabetes Mellitus Type 2',
            'name_ar': 'داء السكري من النوع الثاني',
            'condition_code': 'DM2',
            'category': 'Chronic Disease',
            'is_chronic': True,
            'prevalence_base': 18.5,  # Base prevalence percentage
            'severity': 'High'
        },
        {
            'name_en': 'Hypertension',
            'name_ar': 'ارتفاع ضغط الدم',
            'condition_code': 'HTN',
            'category': 'Cardiovascular',
            'is_chronic': True,
            'prevalence_base': 15.2,
            'severity': 'Medium'
        },
        {
            'name_en': 'Obesity',
            'name_ar': 'السمنة',
            'condition_code': 'OBS',
            'category': 'Metabolic',
            'is_chronic': True,
            'prevalence_base': 28.7,
            'severity': 'High'
        },
        {
            'name_en': 'Asthma',
            'name_ar': 'الربو',
            'condition_code': 'AST',
            'category': 'Respiratory',
            'is_chronic': True,
            'prevalence_base': 8.3,
            'severity': 'Medium'
        },
        {
            'name_en': 'Depression',
            'name_ar': 'الاكتئاب',
            'condition_code': 'DEP',
            'category': 'Mental Health',
            'is_chronic': True,
            'prevalence_base': 6.8,
            'severity': 'Medium'
        },
        {
            'name_en': 'Coronary Heart Disease',
            'name_ar': 'مرض القلب التاجي',
            'condition_code': 'CHD',
            'category': 'Cardiovascular',
            'is_chronic': True,
            'prevalence_base': 5.2,
            'severity': 'High'
        },
        {
            'name_en': 'Chronic Kidney Disease',
            'name_ar': 'مرض الكلى المزمن',
            'condition_code': 'CKD',
            'category': 'Renal',
            'is_chronic': True,
            'prevalence_base': 4.1,
            'severity': 'High'
        }
    ]
    
    for region in regions:
        for condition_data in conditions_data:
            # Adjust prevalence based on region (urban vs rural, demographics)
            base_prevalence = condition_data['prevalence_base']
            
            # Urban areas might have different prevalence
            urban_factor = region.urban_population / region.total_population
            if condition_data['condition_code'] in ['DM2', 'HTN', 'OBS']:
                prevalence = base_prevalence * (1 + urban_factor * 0.2)  # Higher in urban
            else:
                prevalence = base_prevalence * random.uniform(0.8, 1.2)
            
            # Calculate cases
            total_cases = int(region.total_population * prevalence / 100)
            male_cases = int(total_cases * random.uniform(0.45, 0.65))
            female_cases = total_cases - male_cases
            
            # Age distribution of cases
            age_0_17 = int(total_cases * random.uniform(0.05, 0.15))
            age_18_44 = int(total_cases * random.uniform(0.25, 0.40))
            age_45_64 = int(total_cases * random.uniform(0.35, 0.50))
            age_65_plus = total_cases - age_0_17 - age_18_44 - age_45_64
            
            health_condition = HealthCondition(
                region_id=region.id,
                condition_name_en=condition_data['name_en'],
                condition_name_ar=condition_data['name_ar'],
                condition_code=condition_data['condition_code'],
                condition_category=condition_data['category'],
                data_year=current_year,
                data_quarter=4,
                prevalence_rate=round(prevalence, 2),
                incidence_rate=round(prevalence * random.uniform(0.15, 0.35), 2),
                total_cases=total_cases,
                new_cases_annual=int(total_cases * random.uniform(0.1, 0.25)),
                male_cases=male_cases,
                female_cases=female_cases,
                age_0_17_cases=age_0_17,
                age_18_44_cases=age_18_44,
                age_45_64_cases=age_45_64,
                age_65_plus_cases=age_65_plus,
                hospitalization_rate=random.uniform(8.5, 25.3),
                mortality_rate=random.uniform(0.5, 8.2),
                disability_adjusted_life_years=random.uniform(1200, 8500),
                treatment_cost_annual=random.uniform(15000, 85000),
                prevention_cost_per_case=random.uniform(500, 2500),
                is_notifiable=condition_data['condition_code'] in ['DEP'],
                is_chronic=condition_data['is_chronic'],
                severity_level=condition_data['severity'],
                is_active=True,
                created_by=1,
                updated_by=1
            )
            
            db.session.add(health_condition)


def seed_service_standards():
    """Create service standards and capacity metrics"""
    print("📊 Creating service standards...")
    
    regions = Region.query.all()
    categories = HealthcareWorkerCategory.query.all()
    
    # Service standards per healthcare category
    standards_data = [
        {
            'category_code': 'PHY',
            'service_name': 'Primary Care Consultation',
            'standard_time_minutes': 15,
            'patients_per_day': 32,
            'quality_threshold': 85.0
        },
        {
            'category_code': 'NUR',
            'service_name': 'Patient Care Monitoring',
            'standard_time_minutes': 45,
            'patients_per_day': 8,
            'quality_threshold': 90.0
        },
        {
            'category_code': 'PHA',
            'service_name': 'Medication Dispensing',
            'standard_time_minutes': 8,
            'patients_per_day': 60,
            'quality_threshold': 95.0
        },
        {
            'category_code': 'DEN',
            'service_name': 'Dental Examination',
            'standard_time_minutes': 30,
            'patients_per_day': 16,
            'quality_threshold': 88.0
        },
        {
            'category_code': 'MHS',
            'service_name': 'Mental Health Consultation',
            'standard_time_minutes': 50,
            'patients_per_day': 8,
            'quality_threshold': 85.0
        }
    ]
    
    for region in regions:
        for category in categories:
            # Find matching standard
            standard = next((s for s in standards_data if s['category_code'] == category.category_code), None)
            
            if standard:
                service_standard = ServiceStandard(
                    region_id=region.id,
                    worker_category_id=category.id,
                    service_name_en=standard['service_name'],
                    service_name_ar=f"{standard['service_name']} (عربي)",  # Simplified Arabic
                    service_code=f"{category.category_code}_STD",
                    data_year=datetime.now().year,
                    standard_capacity_per_worker=standard['patients_per_day'],
                    target_utilization_rate=random.uniform(85.0, 95.0),
                    actual_utilization_rate=random.uniform(75.0, 92.0),
                    quality_score=random.uniform(80.0, 96.0),
                    patient_satisfaction_score=random.uniform(82.5, 94.8),
                    average_wait_time_minutes=random.uniform(8.5, 35.2),
                    service_cost_per_unit=random.uniform(150.0, 850.0),
                    compliance_rate=random.uniform(88.5, 98.2),
                    benchmark_national=standard['quality_threshold'],
                    benchmark_international=standard['quality_threshold'] + random.uniform(2.0, 8.0),
                    improvement_target=random.uniform(2.0, 5.0),
                    is_active=True,
                    created_by=1,
                    updated_by=1
                )
                
                db.session.add(service_standard)


def get_sample_data_summary():
    """Get summary of created sample data"""
    try:
        summary = {
            'regions': Region.query.count(),
            'healthcare_categories': HealthcareWorkerCategory.query.count(),
            'workforce_records': WorkforceStock.query.count(),
            'population_records': PopulationData.query.count(),
            'health_conditions': HealthCondition.query.count(),
            'service_standards': ServiceStandard.query.count(),
            'users': User.query.count()
        }
        
        # Get some sample statistics
        total_workforce = db.session.query(db.func.sum(WorkforceStock.current_count)).scalar() or 0
        total_population = db.session.query(db.func.sum(PopulationData.total_population)).scalar() or 0
        
        summary['total_workforce'] = total_workforce
        summary['total_population'] = total_population
        summary['workforce_per_1000'] = round(total_workforce / (total_population / 1000), 2) if total_population > 0 else 0
        
        return summary
        
    except Exception as e:
        print(f"Error getting summary: {str(e)}")
        return {}


if __name__ == '__main__':
    init_database()