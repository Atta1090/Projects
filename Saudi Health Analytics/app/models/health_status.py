"""
Health Condition Model
Tracks disease prevalence, health conditions, and health status indicators
"""

from datetime import datetime
from app import db
from app.models.base import BaseModel
from sqlalchemy import func, and_
from sqlalchemy.ext.hybrid import hybrid_property


class HealthCondition(BaseModel):
    """Model for tracking health conditions and disease prevalence"""
    
    # References
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=False)
    
    # Condition identification
    condition_code = db.Column(db.String(20), index=True)  # ICD-10 or local code
    condition_name_ar = db.Column(db.String(200), nullable=False)
    condition_name_en = db.Column(db.String(200), nullable=False)
    condition_category = db.Column(db.String(100))  # Chronic, Infectious, Mental Health, etc.
    
    # Data period
    data_year = db.Column(db.Integer, nullable=False, default=lambda: datetime.now().year)
    data_source = db.Column(db.String(100))  # MOH, hospitals, surveys, etc.
    
    # Prevalence data
    total_cases = db.Column(db.Integer, default=0)
    new_cases_annual = db.Column(db.Integer, default=0)  # Incidence
    prevalence_rate = db.Column(db.Float)  # Per 100,000 population
    incidence_rate = db.Column(db.Float)   # Per 100,000 population per year
    
    # Demographics
    male_cases = db.Column(db.Integer, default=0)
    female_cases = db.Column(db.Integer, default=0)
    saudi_cases = db.Column(db.Integer, default=0)
    non_saudi_cases = db.Column(db.Integer, default=0)
    
    # Age-specific prevalence
    age_0_17_cases = db.Column(db.Integer, default=0)
    age_18_39_cases = db.Column(db.Integer, default=0)
    age_40_59_cases = db.Column(db.Integer, default=0)
    age_60_plus_cases = db.Column(db.Integer, default=0)
    
    # Severity classification
    mild_cases = db.Column(db.Integer, default=0)
    moderate_cases = db.Column(db.Integer, default=0)
    severe_cases = db.Column(db.Integer, default=0)
    critical_cases = db.Column(db.Integer, default=0)
    
    # Healthcare utilization
    primary_care_visits = db.Column(db.Integer, default=0)
    specialist_visits = db.Column(db.Integer, default=0)
    emergency_visits = db.Column(db.Integer, default=0)
    hospitalizations = db.Column(db.Integer, default=0)
    average_length_of_stay = db.Column(db.Float)  # Days
    
    # Mortality data
    deaths_annual = db.Column(db.Integer, default=0)
    case_fatality_rate = db.Column(db.Float)  # Percentage
    mortality_rate = db.Column(db.Float)  # Per 100,000 population
    
    # Economic impact
    direct_cost_per_case = db.Column(db.Float)  # SAR
    indirect_cost_per_case = db.Column(db.Float)  # SAR
    productivity_loss_days = db.Column(db.Integer)  # Days per case
    
    # Treatment and care requirements
    requires_specialist_care = db.Column(db.Boolean, default=False)
    requires_hospitalization = db.Column(db.Boolean, default=False)
    requires_long_term_care = db.Column(db.Boolean, default=False)
    is_preventable = db.Column(db.Boolean, default=True)
    
    # Service utilization factors
    average_consultations_per_year = db.Column(db.Float)
    average_diagnostic_tests = db.Column(db.Integer)
    average_medications_prescribed = db.Column(db.Integer)
    follow_up_frequency_months = db.Column(db.Integer)
    
    # Risk factors
    lifestyle_related = db.Column(db.Boolean, default=False)
    occupational_related = db.Column(db.Boolean, default=False)
    genetic_related = db.Column(db.Boolean, default=False)
    environmental_related = db.Column(db.Boolean, default=False)
    
    # Data quality
    is_estimated = db.Column(db.Boolean, default=False)
    confidence_interval_lower = db.Column(db.Float)
    confidence_interval_upper = db.Column(db.Float)
    data_quality_score = db.Column(db.Float, default=1.0)  # 0-1
    
    # Status and classification
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_notifiable = db.Column(db.Boolean, default=False)  # Reportable disease
    is_chronic = db.Column(db.Boolean, default=False)
    is_infectious = db.Column(db.Boolean, default=False)
    priority_level = db.Column(db.String(20), default='medium')  # high, medium, low
    
    # Relationships
    region = db.relationship('Region', backref='health_conditions')
    
    def get_condition_name(self, language='en'):
        """Get condition name in specified language"""
        return self.condition_name_ar if language == 'ar' else self.condition_name_en
    
    @hybrid_property
    def male_percentage(self):
        """Calculate percentage of male cases"""
        if self.total_cases > 0:
            return (self.male_cases / self.total_cases) * 100
        return 0
    
    @male_percentage.expression
    def male_percentage(cls):
        """SQLAlchemy expression for male percentage"""
        return func.case(
            [(cls.total_cases > 0, cls.male_cases / cls.total_cases * 100)],
            else_=0
        )
    
    @hybrid_property
    def saudi_percentage(self):
        """Calculate percentage of Saudi cases"""
        if self.total_cases > 0:
            return (self.saudi_cases / self.total_cases) * 100
        return 0
    
    @saudi_percentage.expression
    def saudi_percentage(cls):
        """SQLAlchemy expression for Saudi percentage"""
        return func.case(
            [(cls.total_cases > 0, cls.saudi_cases / cls.total_cases * 100)],
            else_=0
        )
    
    def get_age_distribution(self):
        """Get age distribution of cases"""
        if self.total_cases == 0:
            return {}
        
        return {
            '0-17': {
                'cases': self.age_0_17_cases,
                'percentage': round((self.age_0_17_cases / self.total_cases) * 100, 1)
            },
            '18-39': {
                'cases': self.age_18_39_cases,
                'percentage': round((self.age_18_39_cases / self.total_cases) * 100, 1)
            },
            '40-59': {
                'cases': self.age_40_59_cases,
                'percentage': round((self.age_40_59_cases / self.total_cases) * 100, 1)
            },
            '60+': {
                'cases': self.age_60_plus_cases,
                'percentage': round((self.age_60_plus_cases / self.total_cases) * 100, 1)
            }
        }
    
    def get_severity_distribution(self):
        """Get severity distribution of cases"""
        total_with_severity = (self.mild_cases + self.moderate_cases + 
                              self.severe_cases + self.critical_cases)
        
        if total_with_severity == 0:
            return {}
        
        return {
            'mild': {
                'cases': self.mild_cases,
                'percentage': round((self.mild_cases / total_with_severity) * 100, 1)
            },
            'moderate': {
                'cases': self.moderate_cases,
                'percentage': round((self.moderate_cases / total_with_severity) * 100, 1)
            },
            'severe': {
                'cases': self.severe_cases,
                'percentage': round((self.severe_cases / total_with_severity) * 100, 1)
            },
            'critical': {
                'cases': self.critical_cases,
                'percentage': round((self.critical_cases / total_with_severity) * 100, 1)
            }
        }
    
    def calculate_healthcare_burden(self):
        """Calculate healthcare system burden"""
        if self.total_cases == 0:
            return {}
        
        # Calculate resource utilization
        total_visits = (self.primary_care_visits + self.specialist_visits + 
                       self.emergency_visits)
        
        visits_per_case = total_visits / self.total_cases if self.total_cases > 0 else 0
        hospitalization_rate = (self.hospitalizations / self.total_cases) * 100 if self.total_cases > 0 else 0
        
        return {
            'total_healthcare_visits': total_visits,
            'visits_per_case': round(visits_per_case, 1),
            'hospitalization_rate': round(hospitalization_rate, 2),
            'average_length_of_stay': self.average_length_of_stay,
            'emergency_visit_rate': round((self.emergency_visits / self.total_cases) * 100, 2) if self.total_cases > 0 else 0
        }
    
    def calculate_economic_impact(self):
        """Calculate economic impact of the condition"""
        if not self.total_cases:
            return {}
        
        total_direct_cost = (self.direct_cost_per_case * self.total_cases) if self.direct_cost_per_case else 0
        total_indirect_cost = (self.indirect_cost_per_case * self.total_cases) if self.indirect_cost_per_case else 0
        total_cost = total_direct_cost + total_indirect_cost
        
        return {
            'total_direct_cost': total_direct_cost,
            'total_indirect_cost': total_indirect_cost,
            'total_economic_impact': total_cost,
            'cost_per_case': round((total_cost / self.total_cases), 2) if self.total_cases > 0 else 0,
            'productivity_loss_days_total': self.productivity_loss_days * self.total_cases if self.productivity_loss_days else 0
        }
    
    def estimate_workforce_requirements(self):
        """Estimate workforce requirements for this condition"""
        if not self.total_cases:
            return {}
        
        # Basic workforce requirement calculations
        primary_care_workload = self.primary_care_visits
        specialist_workload = self.specialist_visits
        
        # Assuming standard consultation times and capacity
        primary_care_fte = (primary_care_workload * 30) / (40 * 52 * 60) if primary_care_workload else 0  # 30 min consultations
        specialist_fte = (specialist_workload * 45) / (40 * 52 * 60) if specialist_workload else 0  # 45 min consultations
        
        return {
            'estimated_primary_care_fte': round(primary_care_fte, 2),
            'estimated_specialist_fte': round(specialist_fte, 2),
            'total_estimated_fte': round(primary_care_fte + specialist_fte, 2),
            'nursing_fte_estimate': round((primary_care_fte + specialist_fte) * 2.5, 2),  # Nurse-to-doctor ratio
            'support_staff_fte': round((primary_care_fte + specialist_fte) * 1.5, 2)
        }
    
    def get_risk_profile(self):
        """Get risk factor profile"""
        risk_factors = []
        if self.lifestyle_related:
            risk_factors.append('lifestyle')
        if self.occupational_related:
            risk_factors.append('occupational')
        if self.genetic_related:
            risk_factors.append('genetic')
        if self.environmental_related:
            risk_factors.append('environmental')
        
        return {
            'risk_factors': risk_factors,
            'is_preventable': self.is_preventable,
            'is_chronic': self.is_chronic,
            'is_infectious': self.is_infectious,
            'priority_level': self.priority_level
        }
    
    def calculate_trend_indicators(self):
        """Calculate trend indicators (requires historical data)"""
        # Get previous year data for comparison
        previous_year_data = self.__class__.query.filter(
            and_(
                self.__class__.region_id == self.region_id,
                self.__class__.condition_code == self.condition_code,
                self.__class__.data_year == self.data_year - 1,
                self.__class__.id != self.id
            )
        ).first()
        
        if not previous_year_data:
            return {}
        
        # Calculate year-over-year changes
        case_change = self.total_cases - previous_year_data.total_cases
        prevalence_change = self.prevalence_rate - previous_year_data.prevalence_rate
        mortality_change = (self.mortality_rate - previous_year_data.mortality_rate) if self.mortality_rate and previous_year_data.mortality_rate else 0
        
        return {
            'case_change_absolute': case_change,
            'case_change_percentage': round((case_change / previous_year_data.total_cases) * 100, 2) if previous_year_data.total_cases > 0 else 0,
            'prevalence_change': round(prevalence_change, 2),
            'mortality_change': round(mortality_change, 2),
            'trend_direction': 'increasing' if case_change > 0 else 'decreasing' if case_change < 0 else 'stable'
        }
    
    def to_dict(self, language='en', include_analytics=False):
        """Convert to dictionary with optional analytics"""
        data = super().to_dict()
        
        # Add localized content
        data['condition_name'] = self.get_condition_name(language)
        
        # Add computed properties
        data['male_percentage'] = round(self.male_percentage, 2)
        data['saudi_percentage'] = round(self.saudi_percentage, 2)
        
        if include_analytics:
            data['age_distribution'] = self.get_age_distribution()
            data['severity_distribution'] = self.get_severity_distribution()
            data['healthcare_burden'] = self.calculate_healthcare_burden()
            data['economic_impact'] = self.calculate_economic_impact()
            data['workforce_requirements'] = self.estimate_workforce_requirements()
            data['risk_profile'] = self.get_risk_profile()
            data['trend_indicators'] = self.calculate_trend_indicators()
        
        return data
    
    @classmethod
    def get_top_conditions_by_prevalence(cls, region_id=None, limit=10):
        """Get top conditions by prevalence rate"""
        query = cls.query.filter_by(is_active=True)
        
        if region_id:
            query = query.filter_by(region_id=region_id)
        
        return query.order_by(cls.prevalence_rate.desc()).limit(limit).all()
    
    @classmethod
    def get_chronic_disease_summary(cls, region_id=None):
        """Get summary of chronic diseases"""
        query = db.session.query(
            func.sum(cls.total_cases).label('total_chronic_cases'),
            func.avg(cls.prevalence_rate).label('avg_prevalence'),
            func.sum(cls.deaths_annual).label('total_deaths'),
            func.count(cls.id).label('condition_count')
        ).filter(
            cls.is_chronic == True,
            cls.is_active == True
        )
        
        if region_id:
            query = query.filter(cls.region_id == region_id)
        
        result = query.first()
        
        return {
            'total_chronic_cases': result.total_chronic_cases or 0,
            'average_prevalence_rate': round(result.avg_prevalence, 2) if result.avg_prevalence else 0,
            'total_chronic_deaths': result.total_deaths or 0,
            'number_of_conditions': result.condition_count or 0
        }
    
    @classmethod
    def get_infectious_disease_summary(cls, region_id=None):
        """Get summary of infectious diseases"""
        query = db.session.query(
            func.sum(cls.total_cases).label('total_infectious_cases'),
            func.sum(cls.new_cases_annual).label('total_new_cases'),
            func.avg(cls.incidence_rate).label('avg_incidence'),
            func.count(cls.id).label('condition_count')
        ).filter(
            cls.is_infectious == True,
            cls.is_active == True
        )
        
        if region_id:
            query = query.filter(cls.region_id == region_id)
        
        result = query.first()
        
        return {
            'total_infectious_cases': result.total_infectious_cases or 0,
            'total_new_cases': result.total_new_cases or 0,
            'average_incidence_rate': round(result.avg_incidence, 2) if result.avg_incidence else 0,
            'number_of_conditions': result.condition_count or 0
        }
    
    def __repr__(self):
        return f'<HealthCondition {self.condition_code}: {self.condition_name_en}>' 