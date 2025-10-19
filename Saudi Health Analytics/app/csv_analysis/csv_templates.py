"""
CSV Templates and Required Attributes
Defines what columns should be in each type of CSV file
"""

# 👥 WORKFORCE DATA CSV TEMPLATE
WORKFORCE_CSV_ATTRIBUTES = {
    'required_columns': [
        'region_name',           # e.g., "Riyadh", "Makkah"
        'worker_category',       # e.g., "Doctors", "Nurses", "Pharmacists"
        'current_count',         # Current number of workers
        'authorized_positions',  # How many positions are approved
        'filled_positions',      # How many positions are actually filled
    ],
    'optional_columns': [
        'saudi_workers',         # Number of Saudi nationals
        'non_saudi_workers',     # Number of non-Saudi workers
        'male_workers',          # Number of male workers
        'female_workers',        # Number of female workers
        'new_hires_last_year',   # How many hired in last 12 months
        'resignations_last_year', # How many quit in last 12 months
        'average_salary',        # Average salary for this category
        'years_experience_avg',  # Average years of experience
        'data_date',            # When this data was collected
        'notes'                 # Any additional comments
    ],
    'example_data': [
        {
            'region_name': 'Riyadh',
            'worker_category': 'Doctors',
            'current_count': 2500,
            'authorized_positions': 2800,
            'filled_positions': 2400,
            'saudi_workers': 1800,
            'non_saudi_workers': 700,
            'male_workers': 1600,
            'female_workers': 900,
            'new_hires_last_year': 120,
            'resignations_last_year': 85,
            'average_salary': 180000,
            'years_experience_avg': 8.5,
            'data_date': '2024-12-01',
            'notes': 'Shortage in cardiology'
        }
    ]
}

# 🌍 POPULATION DATA CSV TEMPLATE  
POPULATION_CSV_ATTRIBUTES = {
    'required_columns': [
        'region_name',           # e.g., "Riyadh", "Makkah"
        'total_population',      # Total people in region
        'age_0_14',             # Children 0-14 years
        'age_15_64',            # Working age 15-64 years
        'age_65_plus',          # Elderly 65+ years
    ],
    'optional_columns': [
        'saudi_population',      # Saudi nationals
        'non_saudi_population',  # Non-Saudi residents
        'male_population',       # Male population
        'female_population',     # Female population
        'urban_population',      # Living in cities
        'rural_population',      # Living in rural areas
        'birth_rate',           # Births per 1000 people
        'death_rate',           # Deaths per 1000 people
        'population_growth_rate', # Annual growth percentage
        'data_year',            # Year of data
        'notes'
    ],
    'example_data': [
        {
            'region_name': 'Riyadh',
            'total_population': 8216284,
            'age_0_14': 2054071,
            'age_15_64': 5973124,
            'age_65_plus': 189089,
            'saudi_population': 5188258,
            'non_saudi_population': 3028026,
            'male_population': 4650000,
            'female_population': 3566284,
            'urban_population': 7500000,
            'rural_population': 716284,
            'birth_rate': 18.2,
            'death_rate': 3.8,
            'population_growth_rate': 2.1,
            'data_year': 2024,
            'notes': 'Capital region'
        }
    ]
}

# 🏥 HEALTH CONDITIONS CSV TEMPLATE
HEALTH_CONDITIONS_CSV_ATTRIBUTES = {
    'required_columns': [
        'region_name',           # e.g., "Riyadh", "Makkah"
        'condition_name',        # e.g., "Diabetes", "Hypertension"
        'total_cases',          # Number of people with this condition
        'prevalence_rate',      # Percentage of population affected
    ],
    'optional_columns': [
        'new_cases_this_year',   # New diagnoses this year
        'male_cases',           # Cases in males
        'female_cases',         # Cases in females
        'age_0_17_cases',       # Cases in children
        'age_18_64_cases',      # Cases in adults
        'age_65_plus_cases',    # Cases in elderly
        'hospitalization_rate', # Percentage requiring hospital
        'treatment_cost_avg',   # Average cost per patient
        'condition_severity',   # "Mild", "Moderate", "Severe"
        'data_year',
        'notes'
    ],
    'example_data': [
        {
            'region_name': 'Riyadh',
            'condition_name': 'Diabetes Type 2',
            'total_cases': 1520000,
            'prevalence_rate': 18.5,
            'new_cases_this_year': 76000,
            'male_cases': 820000,
            'female_cases': 700000,
            'age_0_17_cases': 15200,
            'age_18_64_cases': 1140000,
            'age_65_plus_cases': 364800,
            'hospitalization_rate': 12.5,
            'treatment_cost_avg': 15000,
            'condition_severity': 'Moderate',
            'data_year': 2024,
            'notes': 'Rising trend'
        }
    ]
}

# 🎓 TRAINING INSTITUTIONS CSV TEMPLATE
TRAINING_CSV_ATTRIBUTES = {
    'required_columns': [
        'institution_name',      # e.g., "King Saud University"
        'program_type',         # e.g., "Medicine", "Nursing", "Pharmacy"
        'annual_capacity',      # How many students can enroll per year
        'current_enrollment',   # How many students currently enrolled
        'annual_graduates',     # How many graduate per year
    ],
    'optional_columns': [
        'region_location',       # Which region the institution is in
        'graduation_rate',      # Percentage who successfully graduate
        'employment_rate',      # Percentage who find jobs after graduation
        'quality_score',        # Institution quality rating (1-10)
        'male_students',        # Number of male students
        'female_students',      # Number of female students
        'faculty_count',        # Number of teachers
        'establishment_year',   # When institution was founded
        'accreditation_status', # "Accredited", "Provisional", "Not Accredited"
        'tuition_fee_annual',   # Annual cost
        'notes'
    ],
    'example_data': [
        {
            'institution_name': 'King Saud University',
            'program_type': 'Medicine',
            'annual_capacity': 530,
            'current_enrollment': 2650,
            'annual_graduates': 474,
            'region_location': 'Riyadh',
            'graduation_rate': 89.4,
            'employment_rate': 95.0,
            'quality_score': 9.2,
            'male_students': 1325,
            'female_students': 1325,
            'faculty_count': 185,
            'establishment_year': 1967,
            'accreditation_status': 'Accredited',
            'tuition_fee_annual': 0,
            'notes': 'Leading medical school'
        }
    ]
}

# 📋 ALL TEMPLATES SUMMARY
CSV_TEMPLATES = {
    'workforce': WORKFORCE_CSV_ATTRIBUTES,
    'population': POPULATION_CSV_ATTRIBUTES, 
    'health_conditions': HEALTH_CONDITIONS_CSV_ATTRIBUTES,
    'training': TRAINING_CSV_ATTRIBUTES
}

def get_csv_template(template_type):
    """Get CSV template for specific data type"""
    return CSV_TEMPLATES.get(template_type, {})

def get_all_templates():
    """Get all available CSV templates"""
    return CSV_TEMPLATES

def generate_sample_csv(template_type, filename=None):
    """Generate a sample CSV file for download"""
    template = get_csv_template(template_type)
    if not template:
        return None
    
    # Create CSV content
    required_cols = template['required_columns']
    optional_cols = template.get('optional_columns', [])
    all_columns = required_cols + optional_cols
    
    # Header row
    csv_content = ','.join(all_columns) + '\n'
    
    # Add example data if available
    if 'example_data' in template:
        for example in template['example_data']:
            row_data = []
            for col in all_columns:
                value = example.get(col, '')
                row_data.append(str(value))
            csv_content += ','.join(row_data) + '\n'
    
    return csv_content 