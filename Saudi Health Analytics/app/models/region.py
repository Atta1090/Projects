"""
Region Model
Stores information about Saudi Arabia's 13 administrative regions
Supports Arabic and English names, population data, and geographic information
"""

from app import db
from app.models.base import BaseModel
from sqlalchemy import and_, func
from sqlalchemy.ext.hybrid import hybrid_property


class Region(BaseModel):
    """Model for Saudi Arabia's administrative regions"""
    
    # Basic region information
    code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    name_ar = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    
    # Geographic information
    area_km2 = db.Column(db.Float)  # Area in square kilometers
    latitude = db.Column(db.Float)  # Center latitude
    longitude = db.Column(db.Float)  # Center longitude
    
    # Administrative information
    capital_ar = db.Column(db.String(100))
    capital_en = db.Column(db.String(100))
    governor = db.Column(db.String(100))
    
    # Population data (current)
    population_total = db.Column(db.Integer)
    population_saudi = db.Column(db.Integer)
    population_non_saudi = db.Column(db.Integer)
    population_male = db.Column(db.Integer)
    population_female = db.Column(db.Integer)
    
    # Economic indicators
    gdp_per_capita = db.Column(db.Float)
    unemployment_rate = db.Column(db.Float)
    
    # Healthcare infrastructure
    hospitals_count = db.Column(db.Integer, default=0)
    primary_care_centers = db.Column(db.Integer, default=0)
    specialized_centers = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    def __init__(self, **kwargs):
        """Initialize region with default values"""
        super(Region, self).__init__(**kwargs)
        if self.population_total is None:
            self.population_total = 0
        if self.hospitals_count is None:
            self.hospitals_count = 0
        if self.primary_care_centers is None:
            self.primary_care_centers = 0
    
    def get_name(self, language='en'):
        """Get region name in specified language"""
        return self.name_ar if language == 'ar' else self.name_en
    
    def get_capital(self, language='en'):
        """Get capital name in specified language"""
        return self.capital_ar if language == 'ar' else self.capital_en
    
    @hybrid_property
    def population_density(self):
        """Calculate population density per km²"""
        if self.area_km2 and self.area_km2 > 0:
            return self.population_total / self.area_km2
        return 0
    
    @population_density.expression
    def population_density(cls):
        """SQLAlchemy expression for population density"""
        return func.case(
            [(cls.area_km2 > 0, cls.population_total / cls.area_km2)],
            else_=0
        )
    
    @hybrid_property
    def saudi_percentage(self):
        """Calculate percentage of Saudi citizens"""
        if self.population_total and self.population_total > 0:
            return (self.population_saudi / self.population_total) * 100
        return 0
    
    @saudi_percentage.expression
    def saudi_percentage(cls):
        """SQLAlchemy expression for Saudi percentage"""
        return func.case(
            [(cls.population_total > 0, (cls.population_saudi / cls.population_total) * 100)],
            else_=0
        )
    
    def get_workforce_summary(self):
        """Get workforce summary for this region"""
        from app.models.workforce import WorkforceStock
        
        workforce_data = db.session.query(
            func.sum(WorkforceStock.current_count).label('total_workforce'),
            func.sum(WorkforceStock.filled_positions).label('filled_positions'),
            func.sum(WorkforceStock.authorized_positions).label('authorized_positions')
        ).filter(WorkforceStock.region_id == self.id).first()
        
        total_workforce = workforce_data.total_workforce or 0
        filled_positions = workforce_data.filled_positions or 0
        authorized_positions = workforce_data.authorized_positions or 0
        
        # Calculate vacancy rate
        vacancy_rate = 0
        if authorized_positions > 0:
            vacancy_rate = ((authorized_positions - filled_positions) / authorized_positions) * 100
        
        return {
            'total_workforce': total_workforce,
            'filled_positions': filled_positions,
            'authorized_positions': authorized_positions,
            'vacancy_rate': round(vacancy_rate, 2),
            'utilization_rate': round((filled_positions / authorized_positions * 100) if authorized_positions > 0 else 0, 2)
        }
    
    def get_population_by_age_group(self):
        """Get population breakdown by age groups"""
        from app.models.population import PopulationData
        
        age_groups = db.session.query(
            PopulationData.age_group,
            func.sum(PopulationData.male_count + PopulationData.female_count).label('total')
        ).filter(
            PopulationData.region_id == self.id
        ).group_by(PopulationData.age_group).all()
        
        return {group.age_group: group.total for group in age_groups}
    
    def calculate_healthcare_ratios(self):
        """Calculate healthcare infrastructure ratios"""
        if not self.population_total or self.population_total == 0:
            return {
                'hospitals_per_100k': 0,
                'primary_care_per_100k': 0,
                'specialized_per_100k': 0
            }
        
        population_100k = self.population_total / 100000
        
        return {
            'hospitals_per_100k': round(self.hospitals_count / population_100k, 2),
            'primary_care_per_100k': round(self.primary_care_centers / population_100k, 2),
            'specialized_per_100k': round(self.specialized_centers / population_100k, 2)
        }
    
    def get_health_conditions_prevalence(self):
        """Get health conditions prevalence in this region"""
        from app.models.health_status import HealthCondition
        
        conditions = db.session.query(
            HealthCondition.condition_name_en,
            HealthCondition.condition_name_ar,
            func.avg(HealthCondition.prevalence_rate).label('avg_prevalence')
        ).filter(
            HealthCondition.region_id == self.id
        ).group_by(
            HealthCondition.condition_name_en,
            HealthCondition.condition_name_ar
        ).all()
        
        return [
            {
                'condition_en': condition.condition_name_en,
                'condition_ar': condition.condition_name_ar,
                'prevalence_rate': round(condition.avg_prevalence, 2)
            }
            for condition in conditions
        ]
    
    def to_dict(self, language='en', include_analytics=False):
        """Convert region to dictionary with language support"""
        data = super().to_dict()
        
        # Add localized names
        data['name'] = self.get_name(language)
        data['capital'] = self.get_capital(language)
        
        # Add calculated properties
        data['population_density'] = round(self.population_density, 2)
        data['saudi_percentage'] = round(self.saudi_percentage, 2)
        
        if include_analytics:
            data['workforce_summary'] = self.get_workforce_summary()
            data['healthcare_ratios'] = self.calculate_healthcare_ratios()
            data['age_groups'] = self.get_population_by_age_group()
            data['health_conditions'] = self.get_health_conditions_prevalence()
        
        return data
    
    @classmethod
    def get_all_with_summary(cls, language='en'):
        """Get all regions with summary statistics"""
        regions = cls.query.filter_by(is_active=True).all()
        return [
            region.to_dict(language=language, include_analytics=True)
            for region in regions
        ]
    
    @classmethod
    def find_by_code(cls, code):
        """Find region by code"""
        return cls.query.filter_by(code=code).first()
    
    @classmethod
    def get_national_summary(cls):
        """Get national-level summary statistics"""
        national_data = db.session.query(
            func.sum(cls.population_total).label('total_population'),
            func.sum(cls.population_saudi).label('total_saudi'),
            func.sum(cls.population_non_saudi).label('total_non_saudi'),
            func.sum(cls.hospitals_count).label('total_hospitals'),
            func.sum(cls.primary_care_centers).label('total_primary_care'),
            func.sum(cls.specialized_centers).label('total_specialized'),
            func.sum(cls.area_km2).label('total_area')
        ).filter(cls.is_active == True).first()
        
        if not national_data.total_population:
            return {}
        
        return {
            'total_population': national_data.total_population,
            'saudi_percentage': round((national_data.total_saudi / national_data.total_population) * 100, 2),
            'population_density': round(national_data.total_population / national_data.total_area, 2),
            'total_hospitals': national_data.total_hospitals,
            'total_primary_care': national_data.total_primary_care,
            'total_specialized': national_data.total_specialized,
            'hospitals_per_100k': round((national_data.total_hospitals / national_data.total_population) * 100000, 2)
        }
    
    def __repr__(self):
        return f'<Region {self.code}: {self.name_en}>' 