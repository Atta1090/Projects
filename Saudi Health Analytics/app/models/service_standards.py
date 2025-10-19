"""
Service Standards Model
Defines healthcare service standards, requirements, and capacity metrics
"""

from datetime import datetime
from app import db
from app.models.base import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property


class ServiceStandard(BaseModel):
    """Model for healthcare service standards and capacity requirements"""
    
    # Service identification
    service_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    service_name_ar = db.Column(db.String(200), nullable=False)
    service_name_en = db.Column(db.String(200), nullable=False)
    service_description_ar = db.Column(db.Text)
    service_description_en = db.Column(db.Text)
    
    # Service classification
    service_category = db.Column(db.String(100))  # Primary, Secondary, Tertiary
    service_type = db.Column(db.String(100))      # Preventive, Curative, Rehabilitative
    service_level = db.Column(db.String(50))      # Basic, Intermediate, Advanced
    
    # Healthcare worker requirements
    worker_category_id = db.Column(db.Integer, db.ForeignKey('healthcare_worker_category.id'))
    primary_provider_type = db.Column(db.String(100))    # Doctor, Nurse, Technician, etc.
    secondary_provider_type = db.Column(db.String(100))  # Supporting staff
    
    # Time and capacity standards
    standard_consultation_time = db.Column(db.Integer)     # Minutes per service
    preparation_time = db.Column(db.Integer, default=5)    # Minutes for setup
    documentation_time = db.Column(db.Integer, default=5)  # Minutes for documentation
    total_service_time = db.Column(db.Integer)             # Total time including all activities
    
    # Daily capacity standards
    services_per_day_standard = db.Column(db.Integer)      # Standard daily capacity per provider
    services_per_day_maximum = db.Column(db.Integer)       # Maximum daily capacity
    services_per_hour = db.Column(db.Float)                # Services per hour
    
    # Weekly and annual capacity
    services_per_week = db.Column(db.Integer)
    services_per_year = db.Column(db.Integer)
    working_days_per_week = db.Column(db.Integer, default=5)
    working_weeks_per_year = db.Column(db.Integer, default=48)  # Accounting for holidays/vacation
    
    # Quality standards
    target_wait_time_minutes = db.Column(db.Integer)       # Target waiting time
    maximum_wait_time_minutes = db.Column(db.Integer)      # Maximum acceptable wait time
    patient_satisfaction_target = db.Column(db.Float)     # Target satisfaction score (1-10)
    quality_indicator = db.Column(db.String(200))         # Quality metrics description
    
    # Resource requirements
    equipment_required = db.Column(db.Text)                # Equipment needed
    consumables_per_service = db.Column(db.Float)         # Cost of consumables per service (SAR)
    space_required_sqm = db.Column(db.Float)              # Space requirement in square meters
    
    # Population-based planning ratios
    population_ratio_standard = db.Column(db.Float)       # Services per 1000 population
    high_need_population_ratio = db.Column(db.Float)      # For high-need populations
    minimum_population_threshold = db.Column(db.Integer)   # Minimum population to justify service
    
    # Demographic adjustments
    pediatric_adjustment_factor = db.Column(db.Float, default=1.0)     # Adjustment for children
    geriatric_adjustment_factor = db.Column(db.Float, default=1.0)     # Adjustment for elderly
    chronic_disease_adjustment = db.Column(db.Float, default=1.0)      # Adjustment for chronic conditions
    urban_rural_adjustment = db.Column(db.Float, default=1.0)          # Urban vs rural adjustment
    
    # Complexity and acuity factors
    complexity_level = db.Column(db.String(20), default='medium')     # low, medium, high
    acuity_factor = db.Column(db.Float, default=1.0)                  # Complexity multiplier
    skill_level_required = db.Column(db.String(50))                   # Entry, Intermediate, Advanced, Expert
    
    # Seasonal and temporal variations
    seasonal_variation_factor = db.Column(db.Float, default=1.0)      # Seasonal demand variation
    peak_hours_factor = db.Column(db.Float, default=1.2)              # Peak hours multiplier
    off_hours_availability = db.Column(db.Boolean, default=False)     # 24/7 availability required
    
    # Financial standards
    cost_per_service = db.Column(db.Float)                 # Average cost per service (SAR)
    revenue_per_service = db.Column(db.Float)              # Revenue per service (SAR)
    profitability_margin = db.Column(db.Float)             # Expected margin percentage
    
    # Technology and innovation
    technology_level = db.Column(db.String(50))            # Basic, Intermediate, Advanced
    telemedicine_suitable = db.Column(db.Boolean, default=False)
    ai_automation_potential = db.Column(db.String(20), default='low')  # low, medium, high
    
    # Regulatory and compliance
    regulatory_requirements = db.Column(db.Text)           # Regulatory compliance requirements
    accreditation_standards = db.Column(db.Text)          # Required accreditations
    safety_protocols = db.Column(db.Text)                 # Safety requirements
    
    # Data collection and monitoring
    performance_metrics = db.Column(db.Text)              # Key performance indicators
    data_collection_frequency = db.Column(db.String(20), default='monthly')
    reporting_requirements = db.Column(db.Text)
    
    # Version and validity
    version = db.Column(db.String(10), default='1.0')
    effective_date = db.Column(db.Date, default=datetime.now().date)
    review_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_mandatory = db.Column(db.Boolean, default=False)               # Mandatory service
    is_specialized = db.Column(db.Boolean, default=False)
    
    # Relationships
    worker_category = db.relationship('HealthcareWorkerCategory', backref='service_standards')
    
    def get_service_name(self, language='en'):
        """Get service name in specified language"""
        return self.service_name_ar if language == 'ar' else self.service_name_en
    
    def get_service_description(self, language='en'):
        """Get service description in specified language"""
        return self.service_description_ar if language == 'ar' else self.service_description_en
    
    @hybrid_property
    def total_service_time_calculated(self):
        """Calculate total service time including all components"""
        if self.standard_consultation_time:
            return (self.standard_consultation_time + 
                   (self.preparation_time or 0) + 
                   (self.documentation_time or 0))
        return self.total_service_time or 0
    
    @hybrid_property
    def theoretical_annual_capacity(self):
        """Calculate theoretical annual capacity per provider"""
        if self.services_per_day_standard and self.working_days_per_week and self.working_weeks_per_year:
            return self.services_per_day_standard * self.working_days_per_week * self.working_weeks_per_year
        return 0
    
    def calculate_capacity_metrics(self):
        """Calculate various capacity metrics"""
        if not self.services_per_day_standard:
            return {}
        
        # Calculate different capacity scenarios
        theoretical_daily = self.services_per_day_standard
        maximum_daily = self.services_per_day_maximum or theoretical_daily
        
        # Account for efficiency factors
        realistic_capacity = theoretical_daily * 0.85  # 85% efficiency factor
        
        return {
            'theoretical_daily_capacity': theoretical_daily,
            'realistic_daily_capacity': round(realistic_capacity, 1),
            'maximum_daily_capacity': maximum_daily,
            'weekly_capacity': theoretical_daily * self.working_days_per_week,
            'annual_capacity': self.theoretical_annual_capacity,
            'capacity_utilization_target': 85.0  # Target utilization percentage
        }
    
    def calculate_staffing_requirements(self, annual_demand):
        """Calculate staffing requirements based on demand"""
        if not self.theoretical_annual_capacity or self.theoretical_annual_capacity == 0:
            return {}
        
        # Calculate base FTE requirement
        base_fte = annual_demand / self.theoretical_annual_capacity
        
        # Apply complexity and acuity adjustments
        adjusted_fte = base_fte * (self.acuity_factor or 1.0)
        
        # Apply demographic adjustments (if demographic data available)
        # This would typically require population data input
        
        # Add buffer for leave, training, etc. (typically 15-20%)
        total_fte = adjusted_fte * 1.18
        
        return {
            'base_fte_requirement': round(base_fte, 2),
            'adjusted_fte_requirement': round(adjusted_fte, 2),
            'total_fte_with_buffer': round(total_fte, 2),
            'full_time_positions': round(total_fte),
            'part_time_equivalent': round((total_fte - round(total_fte)) * 40, 1)  # Hours for part-time
        }
    
    def calculate_resource_requirements(self, annual_volume):
        """Calculate resource requirements for given volume"""
        if not annual_volume:
            return {}
        
        # Calculate space requirements
        daily_volume = annual_volume / (self.working_weeks_per_year * self.working_days_per_week)
        concurrent_services = daily_volume / (8 * 60 / self.total_service_time_calculated) if self.total_service_time_calculated else 0
        total_space = concurrent_services * (self.space_required_sqm or 0)
        
        # Calculate consumables cost
        total_consumables_cost = annual_volume * (self.consumables_per_service or 0)
        
        return {
            'estimated_daily_volume': round(daily_volume, 1),
            'concurrent_services_needed': round(concurrent_services, 1),
            'total_space_required_sqm': round(total_space, 1),
            'annual_consumables_cost': round(total_consumables_cost, 2),
            'equipment_requirements': self.equipment_required
        }
    
    def calculate_financial_projections(self, annual_volume):
        """Calculate financial projections"""
        if not annual_volume:
            return {}
        
        total_revenue = annual_volume * (self.revenue_per_service or 0)
        total_cost = annual_volume * (self.cost_per_service or 0)
        profit = total_revenue - total_cost
        margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            'annual_volume': annual_volume,
            'total_revenue': round(total_revenue, 2),
            'total_cost': round(total_cost, 2),
            'gross_profit': round(profit, 2),
            'profit_margin_percentage': round(margin, 2),
            'revenue_per_service': self.revenue_per_service,
            'cost_per_service': self.cost_per_service
        }
    
    def get_quality_standards(self):
        """Get quality standards summary"""
        return {
            'target_wait_time': self.target_wait_time_minutes,
            'maximum_wait_time': self.maximum_wait_time_minutes,
            'satisfaction_target': self.patient_satisfaction_target,
            'quality_indicators': self.quality_indicator,
            'performance_metrics': self.performance_metrics
        }
    
    def assess_service_complexity(self):
        """Assess service complexity and requirements"""
        complexity_score = 0
        
        # Time complexity
        if self.total_service_time_calculated > 60:
            complexity_score += 2
        elif self.total_service_time_calculated > 30:
            complexity_score += 1
        
        # Skill level complexity
        skill_scores = {'entry': 0, 'intermediate': 1, 'advanced': 2, 'expert': 3}
        complexity_score += skill_scores.get(self.skill_level_required, 1)
        
        # Technology complexity
        tech_scores = {'basic': 0, 'intermediate': 1, 'advanced': 2}
        complexity_score += tech_scores.get(self.technology_level, 0)
        
        complexity_level = 'low' if complexity_score <= 2 else 'medium' if complexity_score <= 5 else 'high'
        
        return {
            'complexity_score': complexity_score,
            'complexity_level': complexity_level,
            'skill_level_required': self.skill_level_required,
            'technology_level': self.technology_level,
            'specialization_required': self.is_specialized
        }
    
    def to_dict(self, language='en', include_analytics=False):
        """Convert to dictionary with optional analytics"""
        data = super().to_dict()
        
        # Add localized content
        data['service_name'] = self.get_service_name(language)
        data['service_description'] = self.get_service_description(language)
        
        # Add computed properties
        data['total_service_time_calculated'] = self.total_service_time_calculated
        data['theoretical_annual_capacity'] = self.theoretical_annual_capacity
        
        if include_analytics:
            data['capacity_metrics'] = self.calculate_capacity_metrics()
            data['quality_standards'] = self.get_quality_standards()
            data['complexity_assessment'] = self.assess_service_complexity()
        
        return data
    
    @classmethod
    def get_by_category(cls, category):
        """Get services by category"""
        return cls.query.filter_by(service_category=category, is_active=True).all()
    
    @classmethod
    def get_specialized_services(cls):
        """Get specialized services"""
        return cls.query.filter_by(is_specialized=True, is_active=True).all()
    
    @classmethod
    def get_mandatory_services(cls):
        """Get mandatory services"""
        return cls.query.filter_by(is_mandatory=True, is_active=True).all()
    
    @classmethod
    def calculate_total_capacity_requirements(cls, population_size, demographic_factors=None):
        """Calculate total capacity requirements for a population"""
        services = cls.query.filter_by(is_active=True).all()
        total_requirements = {}
        
        for service in services:
            if service.population_ratio_standard:
                base_demand = (population_size / 1000) * service.population_ratio_standard
                
                # Apply demographic adjustments if provided
                adjusted_demand = base_demand
                if demographic_factors:
                    if demographic_factors.get('pediatric_percentage'):
                        adjusted_demand *= (1 + demographic_factors['pediatric_percentage'] / 100 * 
                                          (service.pediatric_adjustment_factor - 1))
                    if demographic_factors.get('geriatric_percentage'):
                        adjusted_demand *= (1 + demographic_factors['geriatric_percentage'] / 100 * 
                                          (service.geriatric_adjustment_factor - 1))
                
                staffing_req = service.calculate_staffing_requirements(adjusted_demand)
                
                total_requirements[service.service_code] = {
                    'service_name': service.service_name_en,
                    'estimated_demand': round(adjusted_demand),
                    'staffing_requirements': staffing_req
                }
        
        return total_requirements
    
    def __repr__(self):
        return f'<ServiceStandard {self.service_code}: {self.service_name_en}>' 