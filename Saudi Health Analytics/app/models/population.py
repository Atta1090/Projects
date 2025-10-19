"""
Population Data Model
Stores demographic and population statistics by region and time periods
"""

from datetime import datetime
from app import db
from app.models.base import BaseModel
from sqlalchemy import func, and_
from sqlalchemy.ext.hybrid import hybrid_property


class PopulationData(BaseModel):
    """Model for storing population and demographic data"""
    
    # References
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=False)
    
    # Data period
    data_year = db.Column(db.Integer, nullable=False, default=lambda: datetime.now().year)
    data_source = db.Column(db.String(100))  # Census, GASTAT, estimates, etc.
    
    # Basic population counts
    total_population = db.Column(db.Integer, default=0, nullable=False)
    male_count = db.Column(db.Integer, default=0)
    female_count = db.Column(db.Integer, default=0)
    
    # Nationality breakdown
    saudi_count = db.Column(db.Integer, default=0)
    non_saudi_count = db.Column(db.Integer, default=0)
    
    # Age groups (WHO standard age groups)
    age_0_4 = db.Column(db.Integer, default=0)
    age_5_9 = db.Column(db.Integer, default=0)
    age_10_14 = db.Column(db.Integer, default=0)
    age_15_19 = db.Column(db.Integer, default=0)
    age_20_24 = db.Column(db.Integer, default=0)
    age_25_29 = db.Column(db.Integer, default=0)
    age_30_34 = db.Column(db.Integer, default=0)
    age_35_39 = db.Column(db.Integer, default=0)
    age_40_44 = db.Column(db.Integer, default=0)
    age_45_49 = db.Column(db.Integer, default=0)
    age_50_54 = db.Column(db.Integer, default=0)
    age_55_59 = db.Column(db.Integer, default=0)
    age_60_64 = db.Column(db.Integer, default=0)
    age_65_69 = db.Column(db.Integer, default=0)
    age_70_74 = db.Column(db.Integer, default=0)
    age_75_79 = db.Column(db.Integer, default=0)
    age_80_plus = db.Column(db.Integer, default=0)
    
    # Economic indicators
    labor_force_participation_rate = db.Column(db.Float)  # Percentage
    unemployment_rate = db.Column(db.Float)  # Percentage
    economic_activity_rate = db.Column(db.Float)  # Percentage
    
    # Education levels
    illiterate_count = db.Column(db.Integer, default=0)
    primary_education = db.Column(db.Integer, default=0)
    intermediate_education = db.Column(db.Integer, default=0)
    secondary_education = db.Column(db.Integer, default=0)
    university_education = db.Column(db.Integer, default=0)
    postgraduate_education = db.Column(db.Integer, default=0)
    
    # Health coverage and access
    health_insurance_coverage_rate = db.Column(db.Float)  # Percentage
    private_insurance_rate = db.Column(db.Float)  # Percentage
    no_insurance_rate = db.Column(db.Float)  # Percentage
    
    # Urban/Rural distribution
    urban_population = db.Column(db.Integer, default=0)
    rural_population = db.Column(db.Integer, default=0)
    
    # Household information
    total_households = db.Column(db.Integer)
    average_household_size = db.Column(db.Float)
    
    # Birth and death rates (per 1000)
    birth_rate = db.Column(db.Float)
    death_rate = db.Column(db.Float)
    natural_increase_rate = db.Column(db.Float)
    
    # Migration
    internal_migration_in = db.Column(db.Integer, default=0)
    internal_migration_out = db.Column(db.Integer, default=0)
    international_migration_in = db.Column(db.Integer, default=0)
    international_migration_out = db.Column(db.Integer, default=0)
    
    # Health indicators
    life_expectancy_male = db.Column(db.Float)
    life_expectancy_female = db.Column(db.Float)
    infant_mortality_rate = db.Column(db.Float)  # per 1000 live births
    maternal_mortality_rate = db.Column(db.Float)  # per 100,000 live births
    
    # Chronic disease prevalence (percentages)
    diabetes_prevalence = db.Column(db.Float)
    hypertension_prevalence = db.Column(db.Float)
    obesity_prevalence = db.Column(db.Float)
    smoking_prevalence = db.Column(db.Float)
    
    # Data quality
    is_estimated = db.Column(db.Boolean, default=False)
    confidence_level = db.Column(db.Float, default=95.0)  # Confidence level for estimates
    margin_of_error = db.Column(db.Float)  # Margin of error percentage
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    region = db.relationship('Region', backref='population_data')
    
    @hybrid_property
    def saudi_percentage(self):
        """Calculate percentage of Saudi population"""
        if self.total_population > 0:
            return (self.saudi_count / self.total_population) * 100
        return 0
    
    @saudi_percentage.expression
    def saudi_percentage(cls):
        """SQLAlchemy expression for Saudi percentage"""
        return func.case(
            [(cls.total_population > 0, cls.saudi_count / cls.total_population * 100)],
            else_=0
        )
    
    @hybrid_property
    def dependency_ratio(self):
        """Calculate dependency ratio (children + elderly / working age)"""
        children = (self.age_0_4 + self.age_5_9 + self.age_10_14)
        elderly = (self.age_65_69 + self.age_70_74 + self.age_75_79 + self.age_80_plus)
        working_age = self.total_population - children - elderly
        
        if working_age > 0:
            return ((children + elderly) / working_age) * 100
        return 0
    
    @hybrid_property
    def median_age_estimate(self):
        """Estimate median age based on age distribution"""
        # Simplified median age calculation
        total = self.total_population
        if total == 0:
            return 0
        
        cumulative = 0
        age_groups = [
            (2.5, self.age_0_4), (7.5, self.age_5_9), (12.5, self.age_10_14),
            (17.5, self.age_15_19), (22.5, self.age_20_24), (27.5, self.age_25_29),
            (32.5, self.age_30_34), (37.5, self.age_35_39), (42.5, self.age_40_44),
            (47.5, self.age_45_49), (52.5, self.age_50_54), (57.5, self.age_55_59),
            (62.5, self.age_60_64), (67.5, self.age_65_69), (72.5, self.age_70_74),
            (77.5, self.age_75_79), (85, self.age_80_plus)
        ]
        
        for age_midpoint, count in age_groups:
            cumulative += count
            if cumulative >= total / 2:
                return age_midpoint
        
        return 40  # Default if calculation fails
    
    def get_age_group_percentages(self):
        """Get age group distribution as percentages"""
        if self.total_population == 0:
            return {}
        
        return {
            '0-14': round(((self.age_0_4 + self.age_5_9 + self.age_10_14) / self.total_population) * 100, 1),
            '15-29': round(((self.age_15_19 + self.age_20_24 + self.age_25_29) / self.total_population) * 100, 1),
            '30-44': round(((self.age_30_34 + self.age_35_39 + self.age_40_44) / self.total_population) * 100, 1),
            '45-59': round(((self.age_45_49 + self.age_50_54 + self.age_55_59) / self.total_population) * 100, 1),
            '60+': round(((self.age_60_64 + self.age_65_69 + self.age_70_74 + 
                          self.age_75_79 + self.age_80_plus) / self.total_population) * 100, 1)
        }
    
    def get_education_distribution(self):
        """Get education level distribution"""
        total_educated = (self.illiterate_count + self.primary_education + 
                         self.intermediate_education + self.secondary_education + 
                         self.university_education + self.postgraduate_education)
        
        if total_educated == 0:
            return {}
        
        return {
            'illiterate': {
                'count': self.illiterate_count,
                'percentage': round((self.illiterate_count / total_educated) * 100, 1)
            },
            'primary': {
                'count': self.primary_education,
                'percentage': round((self.primary_education / total_educated) * 100, 1)
            },
            'intermediate': {
                'count': self.intermediate_education,
                'percentage': round((self.intermediate_education / total_educated) * 100, 1)
            },
            'secondary': {
                'count': self.secondary_education,
                'percentage': round((self.secondary_education / total_educated) * 100, 1)
            },
            'university': {
                'count': self.university_education,
                'percentage': round((self.university_education / total_educated) * 100, 1)
            },
            'postgraduate': {
                'count': self.postgraduate_education,
                'percentage': round((self.postgraduate_education / total_educated) * 100, 1)
            }
        }
    
    def get_health_indicators(self):
        """Get health indicators summary"""
        return {
            'life_expectancy': {
                'male': self.life_expectancy_male,
                'female': self.life_expectancy_female,
                'average': round((self.life_expectancy_male + self.life_expectancy_female) / 2, 1) 
                          if self.life_expectancy_male and self.life_expectancy_female else None
            },
            'mortality_rates': {
                'infant': self.infant_mortality_rate,
                'maternal': self.maternal_mortality_rate,
                'natural_increase': self.natural_increase_rate
            },
            'disease_prevalence': {
                'diabetes': self.diabetes_prevalence,
                'hypertension': self.hypertension_prevalence,
                'obesity': self.obesity_prevalence,
                'smoking': self.smoking_prevalence
            },
            'insurance_coverage': {
                'health_insurance': self.health_insurance_coverage_rate,
                'private_insurance': self.private_insurance_rate,
                'no_insurance': self.no_insurance_rate
            }
        }
    
    def calculate_healthcare_demand_factors(self):
        """Calculate factors affecting healthcare demand"""
        # Age-based demand factors (elderly need more healthcare)
        elderly_population = (self.age_60_64 + self.age_65_69 + self.age_70_74 + 
                             self.age_75_79 + self.age_80_plus)
        children_population = (self.age_0_4 + self.age_5_9 + self.age_10_14)
        
        elderly_factor = (elderly_population / self.total_population) * 100 if self.total_population > 0 else 0
        children_factor = (children_population / self.total_population) * 100 if self.total_population > 0 else 0
        
        # Chronic disease burden
        chronic_disease_burden = 0
        if self.diabetes_prevalence:
            chronic_disease_burden += self.diabetes_prevalence
        if self.hypertension_prevalence:
            chronic_disease_burden += self.hypertension_prevalence
        if self.obesity_prevalence:
            chronic_disease_burden += self.obesity_prevalence
        
        return {
            'elderly_percentage': round(elderly_factor, 2),
            'children_percentage': round(children_factor, 2),
            'chronic_disease_burden': round(chronic_disease_burden, 2),
            'dependency_ratio': round(self.dependency_ratio, 2),
            'healthcare_demand_index': round((elderly_factor * 2 + children_factor + chronic_disease_burden) / 4, 2)
        }
    
    def project_population_growth(self, years=5):
        """Simple population growth projection"""
        if not self.natural_increase_rate:
            return []
        
        # Convert rate per 1000 to decimal
        growth_rate = self.natural_increase_rate / 1000
        
        projections = []
        current_pop = self.total_population
        
        for year in range(1, years + 1):
            current_pop = current_pop * (1 + growth_rate)
            projections.append({
                'year': self.data_year + year,
                'projected_population': round(current_pop),
                'growth_from_base': round(((current_pop - self.total_population) / self.total_population) * 100, 2)
            })
        
        return projections
    
    def to_dict(self, include_analytics=False):
        """Convert to dictionary with optional analytics"""
        data = super().to_dict()
        
        # Add computed properties
        data['saudi_percentage'] = round(self.saudi_percentage, 2)
        data['dependency_ratio'] = round(self.dependency_ratio, 2)
        data['median_age_estimate'] = round(self.median_age_estimate, 1)
        
        if include_analytics:
            data['age_group_percentages'] = self.get_age_group_percentages()
            data['education_distribution'] = self.get_education_distribution()
            data['health_indicators'] = self.get_health_indicators()
            data['healthcare_demand_factors'] = self.calculate_healthcare_demand_factors()
            data['population_projections'] = self.project_population_growth()
        
        return data
    
    @classmethod
    def get_latest_by_region(cls, region_id):
        """Get latest population data for a region"""
        return cls.query.filter_by(
            region_id=region_id,
            data_year=datetime.now().year,
            is_active=True
        ).first()
    
    @classmethod
    def get_national_summary(cls):
        """Get national population summary"""
        current_year = datetime.now().year
        
        # Get all current population records
        population_records = cls.query.filter_by(
            data_year=current_year,
            is_active=True
        ).all()
        
        if not population_records:
            return {
                'total_population': 0,
                'total_saudi': 0,
                'saudi_percentage': 0,
                'average_age': 0
            }
        
        total_population = sum(p.total_population for p in population_records)
        total_saudi = sum(p.saudi_count for p in population_records)
        
        saudi_percentage = (total_saudi / total_population * 100) if total_population > 0 else 0
        
        return {
            'total_population': total_population,
            'total_saudi': total_saudi,
            'saudi_percentage': round(saudi_percentage, 2),
            'average_age': 32.5  # Simplified
        }
    
    def __repr__(self):
        return f'<PopulationData {self.region_id}-{self.data_year}: {self.total_population}>' 