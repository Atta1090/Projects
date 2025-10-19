"""
Workforce Stock Model
Tracks current healthcare workforce inventory by region and category
"""

from datetime import datetime, date
from app import db
from app.models.base import BaseModel
from sqlalchemy import func, and_, or_
from sqlalchemy.ext.hybrid import hybrid_property


class WorkforceStock(BaseModel):
    """Model for tracking current workforce inventory"""
    
    # References
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=False)
    worker_category_id = db.Column(db.Integer, db.ForeignKey('healthcare_worker_category.id'), nullable=False)
    
    # Data period
    data_year = db.Column(db.Integer, nullable=False, default=lambda: datetime.now().year)
    data_quarter = db.Column(db.Integer)  # 1-4, null for annual data
    data_month = db.Column(db.Integer)   # 1-12, null for quarterly/annual data
    data_date = db.Column(db.Date, default=date.today)
    
    # Current workforce counts
    current_count = db.Column(db.Integer, default=0, nullable=False)
    filled_positions = db.Column(db.Integer, default=0, nullable=False)
    authorized_positions = db.Column(db.Integer, default=0, nullable=False)
    
    # Demographics
    male_count = db.Column(db.Integer, default=0)
    female_count = db.Column(db.Integer, default=0)
    saudi_count = db.Column(db.Integer, default=0)
    non_saudi_count = db.Column(db.Integer, default=0)
    
    # Age distribution
    age_under_30 = db.Column(db.Integer, default=0)
    age_30_39 = db.Column(db.Integer, default=0)
    age_40_49 = db.Column(db.Integer, default=0)
    age_50_59 = db.Column(db.Integer, default=0)
    age_60_plus = db.Column(db.Integer, default=0)
    
    # Experience distribution
    experience_0_2_years = db.Column(db.Integer, default=0)
    experience_3_5_years = db.Column(db.Integer, default=0)
    experience_6_10_years = db.Column(db.Integer, default=0)
    experience_11_15_years = db.Column(db.Integer, default=0)
    experience_16_plus_years = db.Column(db.Integer, default=0)
    
    # Employment type
    permanent_count = db.Column(db.Integer, default=0)
    contract_count = db.Column(db.Integer, default=0)
    temporary_count = db.Column(db.Integer, default=0)
    locum_count = db.Column(db.Integer, default=0)
    
    # Performance metrics
    attrition_rate = db.Column(db.Float, default=0.0)  # Annual attrition rate
    recruitment_rate = db.Column(db.Float, default=0.0)  # Annual recruitment rate
    productivity_index = db.Column(db.Float, default=1.0)  # Productivity relative to standard
    satisfaction_score = db.Column(db.Float)  # Employee satisfaction (1-10)
    
    # Workload metrics
    average_weekly_hours = db.Column(db.Float, default=40.0)
    overtime_hours_per_week = db.Column(db.Float, default=0.0)
    patients_per_day_average = db.Column(db.Float)
    
    # Financial metrics
    average_salary = db.Column(db.Float)
    total_payroll_cost = db.Column(db.Float)
    
    # Data quality
    data_source = db.Column(db.String(100))  # HR system, survey, manual, etc.
    data_quality_score = db.Column(db.Float, default=1.0)  # 0-1, 1 = highest quality
    is_estimated = db.Column(db.Boolean, default=False)
    estimation_method = db.Column(db.String(100))
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    region = db.relationship('Region', backref='workforce_stock')
    worker_category = db.relationship('HealthcareWorkerCategory', backref='workforce_stock')
    
    def __init__(self, **kwargs):
        """Initialize with data validation"""
        super(WorkforceStock, self).__init__(**kwargs)
        self.validate_data_consistency()
    
    def validate_data_consistency(self):
        """Validate data consistency across fields"""
        # Ensure demographic totals match current count
        if self.male_count and self.female_count:
            demographic_total = self.male_count + self.female_count
            if demographic_total != self.current_count:
                # Auto-adjust if slight discrepancy
                if abs(demographic_total - self.current_count) <= 2:
                    self.current_count = demographic_total
        
        # Ensure nationality totals match
        if self.saudi_count and self.non_saudi_count:
            nationality_total = self.saudi_count + self.non_saudi_count
            if nationality_total != self.current_count:
                if abs(nationality_total - self.current_count) <= 2:
                    self.current_count = nationality_total
        
        # Ensure filled positions don't exceed authorized
        if self.filled_positions > self.authorized_positions:
            self.authorized_positions = self.filled_positions
    
    @hybrid_property
    def vacancy_count(self):
        """Calculate number of vacant positions"""
        return self.authorized_positions - self.filled_positions
    
    @vacancy_count.expression
    def vacancy_count(cls):
        """SQLAlchemy expression for vacancy count"""
        return cls.authorized_positions - cls.filled_positions
    
    @hybrid_property
    def vacancy_rate(self):
        """Calculate vacancy rate as percentage"""
        if self.authorized_positions > 0:
            return (self.vacancy_count / self.authorized_positions) * 100
        return 0
    
    @vacancy_rate.expression
    def vacancy_rate(cls):
        """SQLAlchemy expression for vacancy rate"""
        return func.case(
            [(cls.authorized_positions > 0, 
              (cls.authorized_positions - cls.filled_positions) / cls.authorized_positions * 100)],
            else_=0
        )
    
    @hybrid_property
    def utilization_rate(self):
        """Calculate utilization rate as percentage"""
        if self.authorized_positions > 0:
            return (self.filled_positions / self.authorized_positions) * 100
        return 0
    
    @utilization_rate.expression
    def utilization_rate(cls):
        """SQLAlchemy expression for utilization rate"""
        return func.case(
            [(cls.authorized_positions > 0, cls.filled_positions / cls.authorized_positions * 100)],
            else_=0
        )
    
    @hybrid_property
    def saudi_percentage(self):
        """Calculate percentage of Saudi workers"""
        if self.current_count > 0:
            return (self.saudi_count / self.current_count) * 100
        return 0
    
    @saudi_percentage.expression
    def saudi_percentage(cls):
        """SQLAlchemy expression for Saudi percentage"""
        return func.case(
            [(cls.current_count > 0, cls.saudi_count / cls.current_count * 100)],
            else_=0
        )
    
    def get_age_distribution(self):
        """Get age distribution as percentages"""
        if self.current_count == 0:
            return {}
        
        return {
            'under_30': round((self.age_under_30 / self.current_count) * 100, 1),
            '30_39': round((self.age_30_39 / self.current_count) * 100, 1),
            '40_49': round((self.age_40_49 / self.current_count) * 100, 1),
            '50_59': round((self.age_50_59 / self.current_count) * 100, 1),
            '60_plus': round((self.age_60_plus / self.current_count) * 100, 1)
        }
    
    def get_experience_distribution(self):
        """Get experience distribution as percentages"""
        if self.current_count == 0:
            return {}
        
        return {
            '0_2_years': round((self.experience_0_2_years / self.current_count) * 100, 1),
            '3_5_years': round((self.experience_3_5_years / self.current_count) * 100, 1),
            '6_10_years': round((self.experience_6_10_years / self.current_count) * 100, 1),
            '11_15_years': round((self.experience_11_15_years / self.current_count) * 100, 1),
            '16_plus_years': round((self.experience_16_plus_years / self.current_count) * 100, 1)
        }
    
    def get_employment_type_distribution(self):
        """Get employment type distribution"""
        if self.current_count == 0:
            return {}
        
        return {
            'permanent': {
                'count': self.permanent_count,
                'percentage': round((self.permanent_count / self.current_count) * 100, 1)
            },
            'contract': {
                'count': self.contract_count,
                'percentage': round((self.contract_count / self.current_count) * 100, 1)
            },
            'temporary': {
                'count': self.temporary_count,
                'percentage': round((self.temporary_count / self.current_count) * 100, 1)
            },
            'locum': {
                'count': self.locum_count,
                'percentage': round((self.locum_count / self.current_count) * 100, 1)
            }
        }
    
    def calculate_productivity_metrics(self):
        """Calculate productivity and efficiency metrics"""
        return {
            'productivity_index': self.productivity_index,
            'average_weekly_hours': self.average_weekly_hours,
            'overtime_ratio': round((self.overtime_hours_per_week / self.average_weekly_hours) * 100, 1) if self.average_weekly_hours > 0 else 0,
            'patients_per_day': self.patients_per_day_average,
            'satisfaction_score': self.satisfaction_score
        }
    
    def calculate_cost_metrics(self):
        """Calculate cost-related metrics"""
        if not self.average_salary or not self.total_payroll_cost:
            return {}
        
        cost_per_position = self.total_payroll_cost / self.current_count if self.current_count > 0 else 0
        
        return {
            'average_salary': self.average_salary,
            'total_payroll_cost': self.total_payroll_cost,
            'cost_per_position': round(cost_per_position, 2),
            'cost_per_patient': round(self.total_payroll_cost / (self.patients_per_day_average * self.current_count * 250), 2) if self.patients_per_day_average and self.current_count > 0 else 0  # Assuming 250 working days
        }
    
    def get_trend_comparison(self, previous_periods=4):
        """Get trend comparison with previous periods"""
        # Get previous periods data
        previous_data = self.__class__.query.filter(
            and_(
                self.__class__.region_id == self.region_id,
                self.__class__.worker_category_id == self.worker_category_id,
                self.__class__.data_year <= self.data_year,
                self.__class__.id != self.id
            )
        ).order_by(
            self.__class__.data_year.desc(),
            self.__class__.data_quarter.desc(),
            self.__class__.data_month.desc()
        ).limit(previous_periods).all()
        
        if not previous_data:
            return {}
        
        # Calculate trends
        trends = {}
        for i, prev_record in enumerate(previous_data):
            period_key = f"period_{i+1}_ago"
            trends[period_key] = {
                'current_count_change': self.current_count - prev_record.current_count,
                'vacancy_rate_change': self.vacancy_rate - prev_record.vacancy_rate,
                'attrition_rate_change': self.attrition_rate - prev_record.attrition_rate,
                'productivity_change': self.productivity_index - prev_record.productivity_index
            }
        
        return trends
    
    def to_dict(self, include_analytics=False):
        """Convert to dictionary with optional analytics"""
        data = super().to_dict()
        
        # Add computed properties
        data['vacancy_count'] = self.vacancy_count
        data['vacancy_rate'] = round(self.vacancy_rate, 2)
        data['utilization_rate'] = round(self.utilization_rate, 2)
        data['saudi_percentage'] = round(self.saudi_percentage, 2)
        
        if include_analytics:
            data['age_distribution'] = self.get_age_distribution()
            data['experience_distribution'] = self.get_experience_distribution()
            data['employment_type_distribution'] = self.get_employment_type_distribution()
            data['productivity_metrics'] = self.calculate_productivity_metrics()
            data['cost_metrics'] = self.calculate_cost_metrics()
            data['trend_comparison'] = self.get_trend_comparison()
        
        return data
    
    @classmethod
    def get_latest_by_region_category(cls, region_id, category_id):
        """Get latest workforce data for a region and category"""
        return cls.query.filter_by(
            region_id=region_id,
            worker_category_id=category_id,
            data_year=datetime.now().year,
            is_active=True
        ).first()
    
    @classmethod
    def get_national_summary(cls):
        """Get national workforce summary"""
        current_year = datetime.now().year
        
        # Get all current workforce records
        workforce_records = cls.query.filter_by(
            data_year=current_year,
            is_active=True
        ).all()
        
        if not workforce_records:
            return {
                'total_workforce': 0,
                'total_authorized': 0,
                'vacancy_rate': 0,
                'utilization_rate': 0
            }
        
        total_current = sum(w.current_count for w in workforce_records)
        total_authorized = sum(w.authorized_positions for w in workforce_records)
        total_filled = sum(w.filled_positions for w in workforce_records)
        
        vacancy_rate = ((total_authorized - total_filled) / total_authorized * 100) if total_authorized > 0 else 0
        utilization_rate = (total_filled / total_authorized * 100) if total_authorized > 0 else 0
        
        return {
            'total_workforce': total_current,
            'total_authorized': total_authorized,
            'vacancy_rate': round(vacancy_rate, 2),
            'utilization_rate': round(utilization_rate, 2)
        }
    
    @classmethod
    def get_regional_comparison(cls, year=None):
        """Get workforce comparison across regions"""
        if year is None:
            year = datetime.now().year
        
        regional_data = db.session.query(
            cls.region_id,
            func.sum(cls.current_count).label('total_workforce'),
            func.sum(cls.authorized_positions).label('total_authorized'),
            func.avg(cls.vacancy_rate).label('avg_vacancy_rate'),
            func.avg(cls.saudi_percentage).label('avg_saudi_percentage')
        ).filter(
            cls.data_year == year,
            cls.is_active == True
        ).group_by(cls.region_id).all()
        
        return [
            {
                'region_id': region.region_id,
                'total_workforce': region.total_workforce,
                'total_authorized': region.total_authorized,
                'vacancy_rate': round(region.avg_vacancy_rate, 2),
                'saudi_percentage': round(region.avg_saudi_percentage, 2)
            }
            for region in regional_data
        ]
    
    def __repr__(self):
        return f'<WorkforceStock {self.region_id}-{self.worker_category_id}-{self.data_year}>' 