"""
Reporting Service
Data aggregation, visualization generation, and export management
"""

import json
import io
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from app import db
from app.models.region import Region
from app.models.healthcare_worker import HealthcareWorkerCategory
from app.models.workforce import WorkforceStock
from app.models.population import PopulationData
from app.models.health_status import HealthCondition
from app.services.workforce_calculator import WorkforceCalculatorService
from app.services.population_service import PopulationService
from app.services.health_status_service import HealthStatusService
from app.services.training_service import TrainingService


@dataclass
class ReportMetadata:
    """Report metadata"""
    report_id: str
    title: str
    description: str
    report_type: str
    generated_at: datetime
    generated_by: str
    parameters: Dict
    data_sources: List[str]
    language: str


@dataclass
class ChartData:
    """Chart data structure"""
    chart_type: str
    title: str
    data: Dict
    options: Dict
    description: str


@dataclass
class ReportSection:
    """Report section structure"""
    section_id: str
    title: str
    content_type: str  # 'text', 'chart', 'table', 'kpi'
    content: Any
    order: int


class ReportingService:
    """
    Service for generating comprehensive reports and data visualizations
    Supports multiple export formats and scheduled reporting
    """
    
    def __init__(self):
        self.workforce_service = WorkforceCalculatorService()
        self.population_service = PopulationService()
        self.health_service = HealthStatusService()
        self.training_service = TrainingService()
        
        # Chart color palettes
        self.color_palettes = {
            'primary': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
            'secondary': ['#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'],
            'saudi_theme': ['#006C35', '#FFFFFF', '#CE1126', '#000000']
        }
    
    def generate_executive_dashboard(self, region_id: Optional[int] = None, language: str = 'en') -> Dict:
        """
        Generate executive dashboard with key metrics and visualizations
        """
        report_metadata = ReportMetadata(
            report_id=f"exec_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title="Executive Dashboard" if language == 'en' else "لوحة القيادة التنفيذية",
            description="High-level overview of healthcare workforce status",
            report_type="dashboard",
            generated_at=datetime.now(),
            generated_by="system",
            parameters={'region_id': region_id, 'language': language},
            data_sources=['workforce', 'population', 'health_status'],
            language=language
        )
        
        # Key Performance Indicators
        kpis = self._generate_executive_kpis(region_id)
        
        # Charts
        charts = self._generate_executive_charts(region_id, language)
        
        # Alert indicators
        alerts = self._generate_executive_alerts(region_id)
        
        # Regional comparison (if national view)
        regional_comparison = None
        if region_id is None:
            regional_comparison = self._generate_regional_comparison_chart(language)
        
        return {
            'metadata': asdict(report_metadata),
            'kpis': kpis,
            'charts': charts,
            'alerts': alerts,
            'regional_comparison': regional_comparison,
            'last_updated': datetime.now().isoformat(),
            'refresh_interval': 300  # 5 minutes
        }
    
    def generate_workforce_analysis_report(self, region_id: int, years: int = 5, language: str = 'en') -> Dict:
        """
        Generate comprehensive workforce analysis report
        """
        region = Region.find_by_id(region_id)
        if not region:
            return {'error': 'Region not found'}
        
        report_metadata = ReportMetadata(
            report_id=f"workforce_analysis_{region_id}_{datetime.now().strftime('%Y%m%d')}",
            title=f"Workforce Analysis - {region.get_name(language)}",
            description="Comprehensive workforce planning analysis with projections",
            report_type="analytical",
            generated_at=datetime.now(),
            generated_by="system",
            parameters={'region_id': region_id, 'years': years, 'language': language},
            data_sources=['workforce', 'training', 'projections'],
            language=language
        )
        
        # Report sections
        sections = []
        
        # Executive Summary
        sections.append(self._create_executive_summary_section(region_id, language))
        
        # Current Workforce Status
        sections.append(self._create_current_workforce_section(region_id, language))
        
        # Supply Projections
        sections.append(self._create_supply_projections_section(region_id, years, language))
        
        # Demand Projections
        sections.append(self._create_demand_projections_section(region_id, years, language))
        
        # Gap Analysis
        sections.append(self._create_gap_analysis_section(region_id, years, language))
        
        # Recommendations
        sections.append(self._create_recommendations_section(region_id, language))
        
        return {
            'metadata': asdict(report_metadata),
            'sections': [asdict(section) for section in sections],
            'appendices': self._generate_report_appendices(region_id, language)
        }
    
    def generate_population_health_report(self, region_id: int, language: str = 'en') -> Dict:
        """
        Generate population health status report
        """
        region = Region.find_by_id(region_id)
        if not region:
            return {'error': 'Region not found'}
        
        report_metadata = ReportMetadata(
            report_id=f"population_health_{region_id}_{datetime.now().strftime('%Y%m%d')}",
            title=f"Population Health Report - {region.get_name(language)}",
            description="Comprehensive analysis of population health status and trends",
            report_type="health_analysis",
            generated_at=datetime.now(),
            generated_by="system",
            parameters={'region_id': region_id, 'language': language},
            data_sources=['population', 'health_status', 'demographics'],
            language=language
        )
        
        # Get data
        demographic_profile = self.population_service.get_demographic_profile(region_id)
        health_profile = self.health_service.get_epidemiological_profile(region_id)
        health_trends = self.health_service.track_health_trends(region_id)
        
        # Generate visualizations
        charts = [
            self._create_population_pyramid_chart(demographic_profile, language),
            self._create_disease_burden_chart(health_profile, language),
            self._create_health_trends_chart(health_trends, language),
            self._create_health_indicators_chart(region_id, language)
        ]
        
        # Tables
        tables = [
            self._create_demographic_table(demographic_profile, language),
            self._create_top_conditions_table(health_profile, language)
        ]
        
        return {
            'metadata': asdict(report_metadata),
            'demographic_profile': asdict(demographic_profile),
            'health_profile': asdict(health_profile),
            'charts': [asdict(chart) for chart in charts],
            'tables': tables,
            'summary_statistics': self._calculate_health_summary_stats(region_id)
        }
    
    def generate_training_capacity_report(self, language: str = 'en') -> Dict:
        """
        Generate training and education capacity report
        """
        report_metadata = ReportMetadata(
            report_id=f"training_capacity_{datetime.now().strftime('%Y%m%d')}",
            title="Healthcare Training Capacity Report" if language == 'en' else "تقرير قدرات التدريب الصحي",
            description="Analysis of healthcare education and training capacity",
            report_type="training_analysis",
            generated_at=datetime.now(),
            generated_by="system",
            parameters={'language': language},
            data_sources=['training', 'graduates', 'institutions'],
            language=language
        )
        
        # Training data
        national_capacity = self.training_service.get_training_capacity_overview()
        graduate_projections = self.training_service.project_graduate_output()
        quality_assessment = self.training_service.evaluate_training_quality()
        
        # Charts
        charts = [
            self._create_capacity_by_category_chart(national_capacity, language),
            self._create_graduate_projections_chart(graduate_projections, language),
            self._create_institution_quality_chart(quality_assessment, language)
        ]
        
        return {
            'metadata': asdict(report_metadata),
            'capacity_overview': national_capacity,
            'graduate_projections': [asdict(proj) for proj in graduate_projections],
            'quality_assessment': quality_assessment,
            'charts': [asdict(chart) for chart in charts],
            'recommendations': self._generate_training_recommendations(language)
        }
    
    def generate_custom_report(self, report_config: Dict) -> Dict:
        """
        Generate custom report based on user configuration
        """
        config = report_config
        report_type = config.get('report_type', 'custom')
        
        report_metadata = ReportMetadata(
            report_id=f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=config.get('title', 'Custom Report'),
            description=config.get('description', 'User-defined custom report'),
            report_type=report_type,
            generated_at=datetime.now(),
            generated_by=config.get('user', 'system'),
            parameters=config.get('parameters', {}),
            data_sources=config.get('data_sources', []),
            language=config.get('language', 'en')
        )
        
        # Generate sections based on configuration
        sections = []
        for section_config in config.get('sections', []):
            section = self._generate_custom_section(section_config)
            if section:
                sections.append(section)
        
        return {
            'metadata': asdict(report_metadata),
            'sections': [asdict(section) for section in sections]
        }
    
    def export_report(self, report_data: Dict, export_format: str = 'json') -> Union[str, bytes]:
        """
        Export report in specified format
        """
        if export_format.lower() == 'json':
            return json.dumps(report_data, indent=2, default=str, ensure_ascii=False)
        
        elif export_format.lower() == 'csv':
            return self._export_to_csv(report_data)
        
        elif export_format.lower() == 'excel':
            return self._export_to_excel(report_data)
        
        elif export_format.lower() == 'pdf':
            return self._export_to_pdf(report_data)
        
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
    
    def schedule_report(self, report_config: Dict, schedule: Dict) -> str:
        """
        Schedule recurring report generation
        """
        schedule_id = f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Store schedule configuration (would typically use a task queue like Celery)
        schedule_data = {
            'schedule_id': schedule_id,
            'report_config': report_config,
            'frequency': schedule.get('frequency', 'monthly'),
            'recipients': schedule.get('recipients', []),
            'export_format': schedule.get('export_format', 'pdf'),
            'next_run': self._calculate_next_run(schedule.get('frequency')),
            'created_at': datetime.now().isoformat(),
            'is_active': True
        }
        
        # In production, this would be stored in database and processed by background tasks
        return schedule_id
    
    # Private helper methods for report generation
    
    def _generate_executive_kpis(self, region_id: Optional[int]) -> Dict:
        """Generate executive KPIs"""
        if region_id:
            # Regional KPIs
            region = Region.find_by_id(region_id)
            workforce_summary = region.get_workforce_summary() if region else {}
            population_data = PopulationData.get_latest_by_region(region_id)
            
            kpis = {
                'total_workforce': workforce_summary.get('total_workforce', 0),
                'vacancy_rate': workforce_summary.get('vacancy_rate', 0),
                'utilization_rate': workforce_summary.get('utilization_rate', 0),
                'population_served': population_data.total_population if population_data else 0
            }
        else:
            # National KPIs
            national_workforce = WorkforceStock.get_national_summary()
            national_population = PopulationData.get_national_summary()
            
            kpis = {
                'total_workforce': national_workforce.get('total_workforce', 0),
                'vacancy_rate': national_workforce.get('vacancy_rate', 0),
                'total_population': national_population.get('total_population', 0),
                'regions_count': Region.query.filter_by(is_active=True).count()
            }
        
        return kpis
    
    def _generate_executive_charts(self, region_id: Optional[int], language: str) -> List[ChartData]:
        """Generate executive dashboard charts"""
        charts = []
        
        # Workforce distribution by category
        charts.append(self._create_workforce_distribution_chart(region_id, language))
        
        # Vacancy trends
        charts.append(self._create_vacancy_trends_chart(region_id, language))
        
        # Population demographics
        charts.append(self._create_demographics_overview_chart(region_id, language))
        
        return charts
    
    def _generate_executive_alerts(self, region_id: Optional[int]) -> List[Dict]:
        """Generate executive alerts"""
        alerts = []
        
        # Check for critical shortages
        if region_id:
            categories = HealthcareWorkerCategory.get_critical_shortage_categories()
            for category in categories:
                gap_analysis = self.workforce_service.generate_gap_analysis(region_id, category.id, 1)
                if gap_analysis and gap_analysis[0].severity == 'critical_shortage':
                    alerts.append({
                        'type': 'critical',
                        'title': f'Critical Shortage: {category.name_en}',
                        'message': f'Severe workforce shortage detected in {category.name_en}',
                        'action_required': True
                    })
        
        # Disease outbreak alerts
        if region_id:
            outbreaks = self.health_service.monitor_disease_surveillance(region_id)
            for outbreak in outbreaks:
                if outbreak.severity_level in ['critical', 'high']:
                    alerts.append({
                        'type': 'health_alert',
                        'title': f'Disease Outbreak: {outbreak.condition_name}',
                        'message': f'Potential outbreak detected with {outbreak.cases_detected} cases',
                        'action_required': True
                    })
        
        return alerts
    
    def _generate_regional_comparison_chart(self, language: str) -> ChartData:
        """Generate regional comparison chart"""
        regions = Region.query.filter_by(is_active=True).all()
        
        chart_data = {
            'labels': [region.get_name(language) for region in regions],
            'datasets': [{
                'label': 'Total Workforce' if language == 'en' else 'إجمالي القوى العاملة',
                'data': [region.get_workforce_summary()['total_workforce'] for region in regions],
                'backgroundColor': self.color_palettes['primary']
            }]
        }
        
        return ChartData(
            chart_type='bar',
            title='Regional Workforce Comparison' if language == 'en' else 'مقارنة القوى العاملة الإقليمية',
            data=chart_data,
            options={'responsive': True, 'maintainAspectRatio': False},
            description='Comparison of total healthcare workforce across regions'
        )
    
    def _create_workforce_distribution_chart(self, region_id: Optional[int], language: str) -> ChartData:
        """Create workforce distribution pie chart"""
        categories = HealthcareWorkerCategory.get_main_categories()
        
        data = []
        labels = []
        
        for category in categories:
            if region_id:
                workforce_count = category.get_workforce_count(region_id)['total_count']
            else:
                workforce_count = category.get_workforce_count()['total_count']
            
            data.append(workforce_count)
            labels.append(category.get_name(language))
        
        chart_data = {
            'labels': labels,
            'datasets': [{
                'data': data,
                'backgroundColor': self.color_palettes['primary'][:len(data)]
            }]
        }
        
        return ChartData(
            chart_type='pie',
            title='Workforce Distribution by Category' if language == 'en' else 'توزيع القوى العاملة حسب الفئة',
            data=chart_data,
            options={'responsive': True},
            description='Distribution of healthcare workforce by professional category'
        )
    
    def _create_vacancy_trends_chart(self, region_id: Optional[int], language: str) -> ChartData:
        """Create vacancy trends line chart"""
        # Simplified trend data (would pull from historical data in production)
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        vacancy_rates = [8.5, 7.8, 9.2, 8.1, 7.5, 8.8]
        
        chart_data = {
            'labels': months,
            'datasets': [{
                'label': 'Vacancy Rate (%)' if language == 'en' else 'معدل الشواغر (%)',
                'data': vacancy_rates,
                'borderColor': self.color_palettes['primary'][0],
                'tension': 0.1
            }]
        }
        
        return ChartData(
            chart_type='line',
            title='Vacancy Rate Trends' if language == 'en' else 'اتجاهات معدل الشواغر',
            data=chart_data,
            options={'responsive': True, 'scales': {'y': {'beginAtZero': True}}},
            description='Monthly trends in healthcare workforce vacancy rates'
        )
    
    def _create_demographics_overview_chart(self, region_id: Optional[int], language: str) -> ChartData:
        """Create demographics overview chart"""
        if region_id:
            demographic_profile = self.population_service.get_demographic_profile(region_id)
            age_distribution = demographic_profile.age_distribution
        else:
            # National aggregation would be more complex
            age_distribution = {'0-14': 25, '15-29': 30, '30-44': 25, '45-59': 15, '60+': 5}
        
        chart_data = {
            'labels': list(age_distribution.keys()),
            'datasets': [{
                'label': 'Population %' if language == 'en' else 'نسبة السكان %',
                'data': list(age_distribution.values()),
                'backgroundColor': self.color_palettes['secondary']
            }]
        }
        
        return ChartData(
            chart_type='bar',
            title='Population Age Distribution' if language == 'en' else 'التوزيع العمري للسكان',
            data=chart_data,
            options={'responsive': True},
            description='Population distribution by age groups'
        )
    
    def _create_executive_summary_section(self, region_id: int, language: str) -> ReportSection:
        """Create executive summary section"""
        region = Region.find_by_id(region_id)
        workforce_summary = region.get_workforce_summary()
        
        summary_text = f"""
        This report provides a comprehensive analysis of the healthcare workforce in {region.get_name(language)}.
        
        Key Findings:
        - Total Healthcare Workforce: {workforce_summary['total_workforce']:,}
        - Vacancy Rate: {workforce_summary['vacancy_rate']:.1f}%
        - Utilization Rate: {workforce_summary['utilization_rate']:.1f}%
        
        The analysis reveals both opportunities and challenges in maintaining adequate healthcare staffing levels.
        """
        
        return ReportSection(
            section_id='executive_summary',
            title='Executive Summary' if language == 'en' else 'الملخص التنفيذي',
            content_type='text',
            content=summary_text.strip(),
            order=1
        )
    
    def _create_current_workforce_section(self, region_id: int, language: str) -> ReportSection:
        """Create current workforce status section"""
        categories = HealthcareWorkerCategory.get_main_categories()
        
        workforce_data = []
        for category in categories:
            workforce_count = category.get_workforce_count(region_id)
            workforce_data.append({
                'category': category.get_name(language),
                'current_count': workforce_count['total_count'],
                'authorized_positions': workforce_count['authorized_positions'],
                'vacancy_rate': category.calculate_vacancy_rate(region_id)
            })
        
        return ReportSection(
            section_id='current_workforce',
            title='Current Workforce Status' if language == 'en' else 'حالة القوى العاملة الحالية',
            content_type='table',
            content=workforce_data,
            order=2
        )
    
    def _create_supply_projections_section(self, region_id: int, years: int, language: str) -> ReportSection:
        """Create supply projections section"""
        categories = HealthcareWorkerCategory.get_main_categories()
        
        projections_data = {}
        for category in categories[:3]:  # Limit to top 3 categories for summary
            projections = self.workforce_service.calculate_supply_projection(region_id, category.id, years)
            projections_data[category.get_name(language)] = [
                {'year': p.year, 'projected_supply': p.value} for p in projections
            ]
        
        return ReportSection(
            section_id='supply_projections',
            title='Supply Projections' if language == 'en' else 'توقعات العرض',
            content_type='chart',
            content=projections_data,
            order=3
        )
    
    def _create_demand_projections_section(self, region_id: int, years: int, language: str) -> ReportSection:
        """Create demand projections section"""
        categories = HealthcareWorkerCategory.get_main_categories()
        
        projections_data = {}
        for category in categories[:3]:  # Limit to top 3 categories
            projections = self.workforce_service.calculate_demand_projection(region_id, category.id, years)
            projections_data[category.get_name(language)] = [
                {'year': p.year, 'projected_demand': p.value} for p in projections
            ]
        
        return ReportSection(
            section_id='demand_projections',
            title='Demand Projections' if language == 'en' else 'توقعات الطلب',
            content_type='chart',
            content=projections_data,
            order=4
        )
    
    def _create_gap_analysis_section(self, region_id: int, years: int, language: str) -> ReportSection:
        """Create gap analysis section"""
        categories = HealthcareWorkerCategory.get_main_categories()
        
        gap_data = []
        for category in categories:
            gap_analysis = self.workforce_service.generate_gap_analysis(region_id, category.id, years)
            if gap_analysis:
                latest_gap = gap_analysis[-1]  # Last year projection
                gap_data.append({
                    'category': category.get_name(language),
                    'projected_gap': latest_gap.gap,
                    'gap_percentage': latest_gap.gap_percentage,
                    'severity': latest_gap.severity,
                    'recommendations': latest_gap.recommendations[:3]  # Top 3 recommendations
                })
        
        return ReportSection(
            section_id='gap_analysis',
            title='Gap Analysis' if language == 'en' else 'تحليل الفجوات',
            content_type='table',
            content=gap_data,
            order=5
        )
    
    def _create_recommendations_section(self, region_id: int, language: str) -> ReportSection:
        """Create recommendations section"""
        recommendations = [
            "Accelerate recruitment in critical shortage areas",
            "Expand training capacity for high-demand categories",
            "Implement retention strategies to reduce attrition",
            "Develop partnerships with international healthcare institutions",
            "Invest in technology to improve workforce productivity"
        ]
        
        if language == 'ar':
            recommendations = [
                "تسريع التوظيف في المناطق التي تعاني من نقص حاد",
                "توسيع قدرات التدريب للفئات عالية الطلب",
                "تنفيذ استراتيجيات الاستبقاء لتقليل معدل الدوران",
                "تطوير شراكات مع المؤسسات الصحية الدولية",
                "الاستثمار في التكنولوجيا لتحسين إنتاجية القوى العاملة"
            ]
        
        return ReportSection(
            section_id='recommendations',
            title='Strategic Recommendations' if language == 'en' else 'التوصيات الاستراتيجية',
            content_type='text',
            content='\n'.join(f"• {rec}" for rec in recommendations),
            order=6
        )
    
    def _generate_report_appendices(self, region_id: int, language: str) -> Dict:
        """Generate report appendices"""
        return {
            'methodology': 'Workforce projections use cohort-component analysis with Monte Carlo simulation',
            'data_sources': ['Ministry of Health', 'General Authority for Statistics', 'Training Institutions'],
            'assumptions': ['5% annual attrition rate', '3% population growth', '87% graduation rate'],
            'limitations': ['Data availability constraints', 'Projection uncertainty increases with time horizon'],
            'glossary': {
                'FTE': 'Full-Time Equivalent',
                'Vacancy Rate': 'Percentage of unfilled authorized positions',
                'Utilization Rate': 'Percentage of authorized positions that are filled'
            }
        }
    
    def _create_population_pyramid_chart(self, demographic_profile, language: str) -> ChartData:
        """Create population pyramid chart"""
        age_distribution = demographic_profile.age_distribution
        
        chart_data = {
            'labels': list(age_distribution.keys()),
            'datasets': [{
                'label': 'Population %' if language == 'en' else 'نسبة السكان %',
                'data': list(age_distribution.values()),
                'backgroundColor': self.color_palettes['primary'][0]
            }]
        }
        
        return ChartData(
            chart_type='horizontalBar',
            title='Population Pyramid' if language == 'en' else 'الهرم السكاني',
            data=chart_data,
            options={'responsive': True, 'indexAxis': 'y'},
            description='Population distribution by age groups'
        )
    
    def _create_disease_burden_chart(self, health_profile, language: str) -> ChartData:
        """Create disease burden chart"""
        chart_data = {
            'labels': ['Chronic Diseases' if language == 'en' else 'الأمراض المزمنة',
                      'Infectious Diseases' if language == 'en' else 'الأمراض المعدية'],
            'datasets': [{
                'data': [health_profile.chronic_disease_burden, health_profile.infectious_disease_burden],
                'backgroundColor': self.color_palettes['primary'][:2]
            }]
        }
        
        return ChartData(
            chart_type='doughnut',
            title='Disease Burden Distribution' if language == 'en' else 'توزيع عبء المرض',
            data=chart_data,
            options={'responsive': True},
            description='Distribution of disease burden by type'
        )
    
    def _create_health_trends_chart(self, health_trends: Dict, language: str) -> ChartData:
        """Create health trends chart"""
        # Simplified trend visualization
        chart_data = {
            'labels': ['2020', '2021', '2022', '2023', '2024'],
            'datasets': [{
                'label': 'Health Index' if language == 'en' else 'مؤشر الصحة',
                'data': [85, 87, 86, 88, 89],  # Simplified data
                'borderColor': self.color_palettes['primary'][0],
                'tension': 0.1
            }]
        }
        
        return ChartData(
            chart_type='line',
            title='Health Trends Over Time' if language == 'en' else 'اتجاهات الصحة عبر الوقت',
            data=chart_data,
            options={'responsive': True},
            description='Health indicators trends over recent years'
        )
    
    def _create_health_indicators_chart(self, region_id: int, language: str) -> ChartData:
        """Create health indicators radar chart"""
        # Simplified health indicators
        indicators = {
            'Life Expectancy' if language == 'en' else 'متوسط العمر': 75,
            'Infant Mortality' if language == 'en' else 'وفيات الرضع': 85,  # Lower is better, so inverted
            'Vaccination Coverage' if language == 'en' else 'تغطية التطعيم': 95,
            'Healthcare Access' if language == 'en' else 'الوصول للرعاية': 88,
            'Disease Prevention' if language == 'en' else 'الوقاية من الأمراض': 82
        }
        
        chart_data = {
            'labels': list(indicators.keys()),
            'datasets': [{
                'label': 'Health Indicators' if language == 'en' else 'المؤشرات الصحية',
                'data': list(indicators.values()),
                'backgroundColor': 'rgba(31, 119, 180, 0.2)',
                'borderColor': self.color_palettes['primary'][0],
                'pointBackgroundColor': self.color_palettes['primary'][0]
            }]
        }
        
        return ChartData(
            chart_type='radar',
            title='Health Indicators Overview' if language == 'en' else 'نظرة عامة على المؤشرات الصحية',
            data=chart_data,
            options={'responsive': True, 'scales': {'r': {'beginAtZero': True, 'max': 100}}},
            description='Comprehensive health indicators assessment'
        )
    
    def _create_demographic_table(self, demographic_profile, language: str) -> Dict:
        """Create demographic data table"""
        return {
            'title': 'Demographic Profile' if language == 'en' else 'الملف الديموغرافي',
            'headers': ['Indicator', 'Value'] if language == 'en' else ['المؤشر', 'القيمة'],
            'data': [
                ['Total Population', f"{demographic_profile.total_population:,}"],
                ['Dependency Ratio', f"{demographic_profile.dependency_ratio:.1f}"],
                ['Median Age', f"{demographic_profile.median_age:.1f}"],
                ['Saudi Percentage', f"{demographic_profile.nationality_distribution.get('saudi', 0):.1f}%"]
            ]
        }
    
    def _create_top_conditions_table(self, health_profile, language: str) -> Dict:
        """Create top health conditions table"""
        return {
            'title': 'Top Health Conditions' if language == 'en' else 'أهم الحالات الصحية',
            'headers': ['Condition', 'Cases', 'Rate'] if language == 'en' else ['الحالة', 'الحالات', 'المعدل'],
            'data': [
                [condition.get('condition_name', 'Unknown'), 
                 condition.get('total_cases', 0),
                 f"{condition.get('prevalence_rate', 0):.1f}"]
                for condition in health_profile.top_conditions[:5]
            ]
        }
    
    def _calculate_health_summary_stats(self, region_id: int) -> Dict:
        """Calculate health summary statistics"""
        return {
            'health_index': 85.5,
            'disease_burden_score': 12.3,
            'health_equity_index': 78.9,
            'preventable_disease_rate': 34.2
        }
    
    def _create_capacity_by_category_chart(self, capacity_data: Dict, language: str) -> ChartData:
        """Create training capacity chart"""
        programs = capacity_data.get('programs_by_category', {})
        
        chart_data = {
            'labels': list(programs.keys()),
            'datasets': [{
                'label': 'Annual Capacity' if language == 'en' else 'القدرة السنوية',
                'data': list(programs.values()),
                'backgroundColor': self.color_palettes['primary']
            }]
        }
        
        return ChartData(
            chart_type='bar',
            title='Training Capacity by Category' if language == 'en' else 'قدرة التدريب حسب الفئة',
            data=chart_data,
            options={'responsive': True},
            description='Annual training capacity by healthcare category'
        )
    
    def _create_graduate_projections_chart(self, projections: List, language: str) -> ChartData:
        """Create graduate projections chart"""
        # Group by category
        categories = {}
        for proj in projections:
            if proj.category not in categories:
                categories[proj.category] = {'years': [], 'graduates': []}
            categories[proj.category]['years'].append(proj.year)
            categories[proj.category]['graduates'].append(proj.expected_graduates)
        
        datasets = []
        colors = self.color_palettes['primary']
        
        for i, (category, data) in enumerate(categories.items()):
            datasets.append({
                'label': category,
                'data': data['graduates'],
                'borderColor': colors[i % len(colors)],
                'tension': 0.1
            })
        
        chart_data = {
            'labels': list(range(2024, 2029)),  # 5 year projection
            'datasets': datasets
        }
        
        return ChartData(
            chart_type='line',
            title='Graduate Projections' if language == 'en' else 'توقعات الخريجين',
            data=chart_data,
            options={'responsive': True},
            description='Projected graduate output by category over time'
        )
    
    def _create_institution_quality_chart(self, quality_data: Dict, language: str) -> ChartData:
        """Create institution quality chart"""
        rankings = quality_data.get('institution_rankings', [])
        
        chart_data = {
            'labels': [inst['name'] for inst in rankings[:5]],  # Top 5
            'datasets': [{
                'label': 'Quality Score' if language == 'en' else 'نقاط الجودة',
                'data': [inst['score'] for inst in rankings[:5]],
                'backgroundColor': self.color_palettes['secondary'][0]
            }]
        }
        
        return ChartData(
            chart_type='bar',
            title='Institution Quality Rankings' if language == 'en' else 'تصنيفات جودة المؤسسات',
            data=chart_data,
            options={'responsive': True, 'scales': {'y': {'min': 0, 'max': 10}}},
            description='Quality scores of healthcare training institutions'
        )
    
    def _generate_training_recommendations(self, language: str) -> List[str]:
        """Generate training recommendations"""
        if language == 'en':
            return [
                "Expand nursing education capacity by 25%",
                "Establish new medical schools in underserved regions",
                "Enhance clinical training partnerships",
                "Implement competency-based curriculum standards",
                "Increase faculty development programs"
            ]
        else:
            return [
                "توسيع قدرة تعليم التمريض بنسبة 25%",
                "إنشاء كليات طب جديدة في المناطق المحرومة",
                "تعزيز شراكات التدريب السريري",
                "تنفيذ معايير المناهج القائمة على الكفاءة",
                "زيادة برامج تطوير أعضاء هيئة التدريس"
            ]
    
    def _generate_custom_section(self, section_config: Dict) -> Optional[ReportSection]:
        """Generate custom report section"""
        section_type = section_config.get('type')
        
        if section_type == 'kpi':
            return self._create_kpi_section(section_config)
        elif section_type == 'chart':
            return self._create_chart_section(section_config)
        elif section_type == 'table':
            return self._create_table_section(section_config)
        elif section_type == 'text':
            return self._create_text_section(section_config)
        
        return None
    
    def _create_kpi_section(self, config: Dict) -> ReportSection:
        """Create KPI section"""
        return ReportSection(
            section_id=config.get('id', 'kpi_section'),
            title=config.get('title', 'Key Performance Indicators'),
            content_type='kpi',
            content=config.get('kpis', []),
            order=config.get('order', 1)
        )
    
    def _create_chart_section(self, config: Dict) -> ReportSection:
        """Create chart section"""
        return ReportSection(
            section_id=config.get('id', 'chart_section'),
            title=config.get('title', 'Chart'),
            content_type='chart',
            content=config.get('chart_data', {}),
            order=config.get('order', 1)
        )
    
    def _create_table_section(self, config: Dict) -> ReportSection:
        """Create table section"""
        return ReportSection(
            section_id=config.get('id', 'table_section'),
            title=config.get('title', 'Data Table'),
            content_type='table',
            content=config.get('table_data', []),
            order=config.get('order', 1)
        )
    
    def _create_text_section(self, config: Dict) -> ReportSection:
        """Create text section"""
        return ReportSection(
            section_id=config.get('id', 'text_section'),
            title=config.get('title', 'Text Section'),
            content_type='text',
            content=config.get('content', ''),
            order=config.get('order', 1)
        )
    
    def _export_to_csv(self, report_data: Dict) -> str:
        """Export report data to CSV format"""
        # Simplified CSV export - would be more sophisticated in production
        csv_content = "Section,Content\n"
        
        sections = report_data.get('sections', [])
        for section in sections:
            title = section.get('title', 'Unknown')
            content_type = section.get('content_type', 'unknown')
            csv_content += f'"{title}","{content_type}"\n'
        
        return csv_content
    
    def _export_to_excel(self, report_data: Dict) -> bytes:
        """Export report data to Excel format"""
        # This would use libraries like openpyxl in production
        # For now, returning placeholder
        return b"Excel export not implemented in demo"
    
    def _export_to_pdf(self, report_data: Dict) -> bytes:
        """Export report data to PDF format"""
        # This would use libraries like reportlab in production
        # For now, returning placeholder
        return b"PDF export not implemented in demo"
    
    def _calculate_next_run(self, frequency: str) -> datetime:
        """Calculate next run time for scheduled reports"""
        now = datetime.now()
        
        if frequency == 'daily':
            return now + timedelta(days=1)
        elif frequency == 'weekly':
            return now + timedelta(weeks=1)
        elif frequency == 'monthly':
            return now + timedelta(days=30)
        elif frequency == 'quarterly':
            return now + timedelta(days=90)
        else:
            return now + timedelta(days=30)  # Default to monthly 