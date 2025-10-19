"""
Healthcare Worker Category Model
Defines different categories of healthcare workers with their requirements and characteristics
"""

from app import db
from app.models.base import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from app.models.workforce import WorkforceStock


class HealthcareWorkerCategory(BaseModel):
    """Model for healthcare worker categories (doctors, nurses, etc.)"""
    
    # Basic category information
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name_ar = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    description_ar = db.Column(db.Text)
    description_en = db.Column(db.Text)
    
    # Category hierarchy
    parent_category_id = db.Column(db.Integer, db.ForeignKey('healthcare_worker_category.id'))
    category_level = db.Column(db.Integer, default=1)  # 1=main, 2=sub, 3=specialty
    
    # Professional requirements
    requires_license = db.Column(db.Boolean, default=True, nullable=False)
    license_authority = db.Column(db.String(100))  # SCFHS, MOH, etc.
    minimum_education = db.Column(db.String(50))  # Bachelor, Master, PhD, Diploma
    required_experience_years = db.Column(db.Integer, default=0)
    
    # Specialization information
    is_specialized = db.Column(db.Boolean, default=False, nullable=False)
    specialization_type = db.Column(db.String(100))  # Medical, Surgical, etc.
    requires_residency = db.Column(db.Boolean, default=False, nullable=False)
    residency_years = db.Column(db.Integer, default=0)
    
    # Work characteristics
    is_clinical = db.Column(db.Boolean, default=True, nullable=False)
    is_administrative = db.Column(db.Boolean, default=False, nullable=False)
    is_support_role = db.Column(db.Boolean, default=False, nullable=False)
    
    # Planning parameters
    standard_working_hours = db.Column(db.Integer, default=40)  # per week
    patients_per_day_capacity = db.Column(db.Integer)
    average_consultation_time = db.Column(db.Integer)  # minutes
    
    # Employment characteristics
    typical_employment_type = db.Column(db.String(20), default='permanent')  # permanent, contract, locum
    average_salary_range_min = db.Column(db.Float)
    average_salary_range_max = db.Column(db.Float)
    
    # Training and development
    requires_continuing_education = db.Column(db.Boolean, default=True, nullable=False)
    ce_hours_per_year = db.Column(db.Integer, default=40)
    
    # Planning coefficients
    attrition_rate = db.Column(db.Float, default=0.05)  # Annual attrition rate
    recruitment_difficulty = db.Column(db.String(20), default='medium')  # easy, medium, hard
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_critical_shortage = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    parent_category = db.relationship('HealthcareWorkerCategory', 
                                    remote_side='HealthcareWorkerCategory.id',
                                    backref='subcategories')
    
    def get_name(self, language='en'):
        """Get category name in specified language"""
        return self.name_ar if language == 'ar' else self.name_en
    
    def get_description(self, language='en'):
        """Get category description in specified language"""
        return self.description_ar if language == 'ar' else self.description_en
    
    @hybrid_property
    def full_hierarchy_name(self):
        """Get full hierarchical name"""
        if self.parent_category:
            return f"{self.parent_category.name_en} -> {self.name_en}"
        return self.name_en
    
    def get_workforce_count(self, region_id=None):
        """Get workforce count for this category"""
        if region_id:
            workforce = WorkforceStock.query.filter_by(
                worker_category_id=self.id, 
                region_id=region_id,
                data_year=datetime.now().year,
                is_active=True
            ).first()
        else:
            # National count
            workforce_records = WorkforceStock.query.filter_by(
                worker_category_id=self.id,
                data_year=datetime.now().year,
                is_active=True
            ).all()
            
            if workforce_records:
                total_count = sum(w.current_count for w in workforce_records)
                authorized_positions = sum(w.authorized_positions for w in workforce_records)
                return {
                    'total_count': total_count,
                    'authorized_positions': authorized_positions
                }
        
        if workforce:
            return {
                'total_count': workforce.current_count,
                'authorized_positions': workforce.authorized_positions
            }
        
        return {'total_count': 0, 'authorized_positions': 0}
    
    def calculate_vacancy_rate(self, region_id):
        """Calculate vacancy rate for this category in a region"""
        workforce_count = self.get_workforce_count(region_id)
        if workforce_count['authorized_positions'] > 0:
            vacancy_rate = ((workforce_count['authorized_positions'] - workforce_count['total_count']) / 
                           workforce_count['authorized_positions']) * 100
            return round(vacancy_rate, 2)
        return 0.0
    
    def get_demand_projection(self, region_id=None, years=5):
        """Get demand projection for this category"""
        from app.services.workforce_calculator import WorkforceCalculatorService
        
        calculator = WorkforceCalculatorService()
        return calculator.calculate_demand_projection(
            region_id=region_id,
            category_id=self.id,
            years=years
        )
    
    def get_supply_projection(self, region_id=None, years=5):
        """Get supply projection for this category"""
        from app.services.workforce_calculator import WorkforceCalculatorService
        
        calculator = WorkforceCalculatorService()
        return calculator.calculate_supply_projection(
            region_id=region_id,
            category_id=self.id,
            years=years
        )
    
    def get_training_capacity(self):
        """Get training/education capacity for this category"""
        from app.models.training import TrainingProgram
        
        programs = db.session.query(
            func.sum(TrainingProgram.annual_capacity).label('total_capacity'),
            func.count(TrainingProgram.id).label('program_count')
        ).filter(TrainingProgram.worker_category_id == self.id).first()
        
        return {
            'annual_capacity': programs.total_capacity or 0,
            'program_count': programs.program_count or 0
        }
    
    def calculate_workload_metrics(self):
        """Calculate standard workload metrics"""
        if not self.patients_per_day_capacity or not self.average_consultation_time:
            return {}
        
        # Calculate theoretical capacity
        working_minutes_per_day = (self.standard_working_hours / 5) * 60  # Assuming 5-day work week
        theoretical_patients = working_minutes_per_day / self.average_consultation_time
        
        # Efficiency factor (usually 80-85% due to breaks, admin time, etc.)
        efficiency_factor = 0.82
        realistic_capacity = theoretical_patients * efficiency_factor
        
        return {
            'theoretical_patients_per_day': round(theoretical_patients, 1),
            'realistic_patients_per_day': round(realistic_capacity, 1),
            'minutes_per_patient': self.average_consultation_time,
            'hours_per_week': self.standard_working_hours
        }
    
    def get_compensation_info(self):
        """Get compensation information"""
        if self.average_salary_range_min and self.average_salary_range_max:
            return {
                'salary_min': self.average_salary_range_min,
                'salary_max': self.average_salary_range_max,
                'salary_mid': (self.average_salary_range_min + self.average_salary_range_max) / 2,
                'currency': 'SAR'
            }
        return {}
    
    def to_dict(self, language='en', include_analytics=False):
        """Convert category to dictionary"""
        data = super().to_dict()
        
        # Add localized content
        data['name'] = self.get_name(language)
        data['description'] = self.get_description(language)
        data['full_hierarchy_name'] = self.full_hierarchy_name
        
        # Add computed properties
        data['workload_metrics'] = self.calculate_workload_metrics()
        data['compensation_info'] = self.get_compensation_info()
        
        if include_analytics:
            data['workforce_count'] = self.get_workforce_count()
            data['vacancy_rate'] = self.calculate_vacancy_rate()
            data['training_capacity'] = self.get_training_capacity()
        
        return data
    
    @classmethod
    def get_main_categories(cls):
        """Get main healthcare worker categories"""
        return cls.query.filter_by(is_active=True, category_level=1).all()
    
    @classmethod
    def get_clinical_categories(cls):
        """Get clinical worker categories"""
        return cls.query.filter_by(is_clinical=True, is_active=True).all()
    
    @classmethod
    def get_critical_shortage_categories(cls):
        """Get categories with critical shortages"""
        return cls.query.filter_by(is_critical_shortage=True, is_active=True).all()
    
    @classmethod
    def find_by_code(cls, code):
        """Find category by code"""
        return cls.query.filter_by(code=code).first()
    
    @classmethod
    def get_hierarchy_tree(cls, language='en'):
        """Get full category hierarchy as tree structure"""
        main_categories = cls.get_main_categories()
        tree = []
        
        for main_cat in main_categories:
            node = {
                'id': main_cat.id,
                'code': main_cat.code,
                'name': main_cat.get_name(language),
                'level': main_cat.category_level,
                'children': []
            }
            
            # Add subcategories
            for sub_cat in main_cat.subcategories:
                if sub_cat.is_active:
                    sub_node = {
                        'id': sub_cat.id,
                        'code': sub_cat.code,
                        'name': sub_cat.get_name(language),
                        'level': sub_cat.category_level,
                        'children': []
                    }
                    
                    # Add sub-subcategories
                    for subsub_cat in sub_cat.subcategories:
                        if subsub_cat.is_active:
                            subsub_node = {
                                'id': subsub_cat.id,
                                'code': subsub_cat.code,
                                'name': subsub_cat.get_name(language),
                                'level': subsub_cat.category_level
                            }
                            sub_node['children'].append(subsub_node)
                    
                    node['children'].append(sub_node)
            
            tree.append(node)
        
        return tree
    
    def __repr__(self):
        return f'<HealthcareWorkerCategory {self.code}: {self.name_en}>' 