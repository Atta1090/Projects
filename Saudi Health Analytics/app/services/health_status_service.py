"""
Health Status Service
Disease surveillance, epidemiological analysis, and health impact assessment
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from app import db
from app.models.region import Region
from app.models.health_status import HealthCondition
from app.models.population import PopulationData
from app.models.healthcare_worker import HealthcareWorkerCategory


@dataclass
class EpidemiologicalProfile:
    """Epidemiological profile for a region"""
    region_id: int
    total_conditions: int
    chronic_disease_burden: float
    infectious_disease_burden: float
    top_conditions: List[Dict]
    mortality_indicators: Dict
    health_trends: Dict


@dataclass
class DiseaseOutbreak:
    """Disease outbreak detection result"""
    condition_name: str
    severity_level: str
    cases_detected: int
    expected_cases: int
    outbreak_threshold: float
    confidence_level: float
    recommendations: List[str]


@dataclass
class WorkforceImpactAssessment:
    """Assessment of health conditions impact on workforce needs"""
    condition_name: str
    estimated_cases: int
    workforce_categories_affected: List[str]
    additional_fte_needed: Dict[str, float]
    cost_implications: Dict
    timeline: str


class HealthStatusService:
    """
    Service for health status monitoring and epidemiological analysis
    Supports workforce planning through health trend analysis
    """
    
    def __init__(self):
        self.outbreak_threshold = 1.5  # Cases 50% above expected
        self.confidence_level = 95.0
    
    def get_epidemiological_profile(self, region_id: int, year: Optional[int] = None) -> EpidemiologicalProfile:
        """
        Generate comprehensive epidemiological profile for a region
        """
        if year is None:
            year = datetime.now().year
        
        # Get all health conditions for the region
        conditions = db.session.query(HealthCondition).filter(
            HealthCondition.region_id == region_id,
            HealthCondition.data_year == year,
            HealthCondition.is_active == True
        ).all()
        
        if not conditions:
            return self._create_empty_profile(region_id)
        
        # Calculate disease burden
        chronic_burden = self._calculate_chronic_disease_burden(conditions)
        infectious_burden = self._calculate_infectious_disease_burden(conditions)
        
        # Identify top conditions
        top_conditions = self._identify_top_conditions(conditions)
        
        # Calculate mortality indicators
        mortality_indicators = self._calculate_mortality_indicators(conditions)
        
        # Analyze health trends
        health_trends = self._analyze_health_trends(region_id, conditions)
        
        return EpidemiologicalProfile(
            region_id=region_id,
            total_conditions=len(conditions),
            chronic_disease_burden=chronic_burden,
            infectious_disease_burden=infectious_burden,
            top_conditions=top_conditions,
            mortality_indicators=mortality_indicators,
            health_trends=health_trends
        )
    
    def monitor_disease_surveillance(self, region_id: int) -> List[DiseaseOutbreak]:
        """
        Monitor for potential disease outbreaks using statistical analysis
        """
        outbreaks = []
        
        # Get current year data
        current_conditions = db.session.query(HealthCondition).filter(
            HealthCondition.region_id == region_id,
            HealthCondition.data_year == datetime.now().year,
            HealthCondition.is_active == True
        ).all()
        
        for condition in current_conditions:
            # Check for outbreak patterns
            outbreak_assessment = self._assess_outbreak_risk(condition, region_id)
            
            if outbreak_assessment['is_outbreak']:
                outbreaks.append(DiseaseOutbreak(
                    condition_name=condition.get_condition_name('en'),
                    severity_level=outbreak_assessment['severity'],
                    cases_detected=condition.total_cases,
                    expected_cases=outbreak_assessment['expected_cases'],
                    outbreak_threshold=self.outbreak_threshold,
                    confidence_level=outbreak_assessment['confidence'],
                    recommendations=outbreak_assessment['recommendations']
                ))
        
        return outbreaks
    
    def assess_workforce_impact(self, region_id: int, condition_codes: List[str] = None) -> List[WorkforceImpactAssessment]:
        """
        Assess the impact of health conditions on healthcare workforce requirements
        """
        assessments = []
        
        # Get conditions to assess
        if condition_codes:
            conditions = db.session.query(HealthCondition).filter(
                HealthCondition.region_id == region_id,
                HealthCondition.condition_code.in_(condition_codes),
                HealthCondition.is_active == True
            ).all()
        else:
            # Assess top conditions by case volume
            conditions = db.session.query(HealthCondition).filter(
                HealthCondition.region_id == region_id,
                HealthCondition.is_active == True
            ).order_by(HealthCondition.total_cases.desc()).limit(10).all()
        
        for condition in conditions:
            impact_assessment = self._calculate_workforce_impact(condition)
            
            assessments.append(WorkforceImpactAssessment(
                condition_name=condition.get_condition_name('en'),
                estimated_cases=condition.total_cases,
                workforce_categories_affected=impact_assessment['categories_affected'],
                additional_fte_needed=impact_assessment['fte_requirements'],
                cost_implications=impact_assessment['cost_implications'],
                timeline=impact_assessment['timeline']
            ))
        
        return assessments
    
    def analyze_prevention_opportunities(self, region_id: int) -> Dict:
        """
        Analyze prevention opportunities to reduce disease burden
        """
        # Get preventable conditions
        preventable_conditions = db.session.query(HealthCondition).filter(
            HealthCondition.region_id == region_id,
            HealthCondition.is_preventable == True,
            HealthCondition.is_active == True
        ).all()
        
        prevention_analysis = {
            'total_preventable_cases': sum(c.total_cases for c in preventable_conditions),
            'prevention_opportunities': [],
            'estimated_savings': 0,
            'workforce_reduction_potential': {}
        }
        
        for condition in preventable_conditions:
            # Calculate prevention potential
            prevention_potential = self._calculate_prevention_potential(condition)
            
            prevention_analysis['prevention_opportunities'].append({
                'condition': condition.get_condition_name('en'),
                'current_cases': condition.total_cases,
                'preventable_percentage': prevention_potential['preventable_percentage'],
                'preventable_cases': prevention_potential['preventable_cases'],
                'intervention_type': prevention_potential['intervention_type'],
                'cost_effectiveness': prevention_potential['cost_effectiveness'],
                'workforce_impact': prevention_potential['workforce_impact']
            })
        
        # Calculate total estimated savings
        prevention_analysis['estimated_savings'] = self._calculate_prevention_savings(preventable_conditions)
        prevention_analysis['workforce_reduction_potential'] = self._calculate_workforce_reduction_potential(preventable_conditions)
        
        return prevention_analysis
    
    def track_health_trends(self, region_id: int, years: int = 5) -> Dict:
        """
        Track health trends over multiple years for predictive analysis
        """
        trends = {}
        
        # Get historical data
        historical_data = db.session.query(HealthCondition).filter(
            HealthCondition.region_id == region_id,
            HealthCondition.data_year >= (datetime.now().year - years),
            HealthCondition.is_active == True
        ).order_by(HealthCondition.data_year, HealthCondition.condition_code).all()
        
        # Group by condition
        condition_trends = {}
        for condition in historical_data:
            code = condition.condition_code
            if code not in condition_trends:
                condition_trends[code] = []
            
            condition_trends[code].append({
                'year': condition.data_year,
                'cases': condition.total_cases,
                'prevalence_rate': condition.prevalence_rate,
                'incidence_rate': condition.incidence_rate
            })
        
        # Analyze trends for each condition
        for condition_code, data_points in condition_trends.items():
            if len(data_points) >= 3:  # Need at least 3 years for trend analysis
                trend_analysis = self._analyze_condition_trend(data_points)
                trends[condition_code] = trend_analysis
        
        # Overall health system trends
        trends['overall_analysis'] = self._analyze_overall_health_trends(historical_data)
        
        return trends
    
    def compare_regional_health_status(self, region_ids: List[int]) -> Dict:
        """
        Compare health status across multiple regions
        """
        regional_comparisons = {}
        
        for region_id in region_ids:
            region = Region.find_by_id(region_id)
            if region:
                profile = self.get_epidemiological_profile(region_id)
                regional_comparisons[region.name_en] = profile
        
        # Calculate comparative metrics
        comparison_metrics = self._calculate_health_comparison_metrics(regional_comparisons)
        
        return {
            'regional_profiles': regional_comparisons,
            'comparison_metrics': comparison_metrics,
            'health_rankings': self._rank_regions_by_health_indicators(regional_comparisons),
            'disparity_analysis': self._analyze_health_disparities(regional_comparisons),
            'best_practices': self._identify_best_practices(regional_comparisons)
        }
    
    # Private helper methods
    
    def _calculate_chronic_disease_burden(self, conditions: List[HealthCondition]) -> float:
        """Calculate chronic disease burden index"""
        chronic_conditions = [c for c in conditions if c.is_chronic]
        
        if not chronic_conditions:
            return 0.0
        
        # Calculate weighted burden based on prevalence and severity
        total_burden = 0
        total_population = 0
        
        for condition in chronic_conditions:
            # Weight by severity distribution
            severity_weight = (
                condition.mild_cases * 1 +
                condition.moderate_cases * 2 +
                condition.severe_cases * 3 +
                condition.critical_cases * 4
            ) / max(condition.total_cases, 1)
            
            condition_burden = condition.prevalence_rate * severity_weight
            total_burden += condition_burden
        
        return round(total_burden / len(chronic_conditions), 2)
    
    def _calculate_infectious_disease_burden(self, conditions: List[HealthCondition]) -> float:
        """Calculate infectious disease burden index"""
        infectious_conditions = [c for c in conditions if c.is_infectious]
        
        if not infectious_conditions:
            return 0.0
        
        # Calculate burden based on incidence and transmission potential
        total_burden = 0
        
        for condition in infectious_conditions:
            # Higher weight for notifiable diseases
            notifiable_weight = 2.0 if condition.is_notifiable else 1.0
            
            # Include case fatality rate impact
            mortality_weight = 1 + (condition.case_fatality_rate or 0) / 100
            
            condition_burden = (condition.incidence_rate or 0) * notifiable_weight * mortality_weight
            total_burden += condition_burden
        
        return round(total_burden / len(infectious_conditions), 2)
    
    def _identify_top_conditions(self, conditions: List[HealthCondition], limit: int = 10) -> List[Dict]:
        """Identify top conditions by various metrics"""
        
        # Sort by different criteria
        by_prevalence = sorted(conditions, key=lambda x: x.prevalence_rate or 0, reverse=True)[:limit]
        by_cases = sorted(conditions, key=lambda x: x.total_cases, reverse=True)[:limit]
        by_mortality = sorted(conditions, key=lambda x: x.mortality_rate or 0, reverse=True)[:limit]
        
        top_conditions = []
        
        for condition in by_cases[:5]:  # Top 5 by case count
            top_conditions.append({
                'condition_name': condition.get_condition_name('en'),
                'condition_code': condition.condition_code,
                'total_cases': condition.total_cases,
                'prevalence_rate': condition.prevalence_rate,
                'category': condition.condition_category,
                'ranking_criteria': 'case_volume'
            })
        
        return top_conditions
    
    def _calculate_mortality_indicators(self, conditions: List[HealthCondition]) -> Dict:
        """Calculate key mortality indicators"""
        
        total_deaths = sum(c.deaths_annual for c in conditions if c.deaths_annual)
        total_cases = sum(c.total_cases for c in conditions)
        
        # Calculate overall case fatality rate
        overall_cfr = (total_deaths / total_cases * 100) if total_cases > 0 else 0
        
        # Identify leading causes of death
        leading_causes = sorted(
            [(c.get_condition_name('en'), c.deaths_annual or 0) for c in conditions],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            'total_deaths_annual': total_deaths,
            'overall_case_fatality_rate': round(overall_cfr, 2),
            'leading_causes_of_death': leading_causes,
            'mortality_rate_per_100k': round((total_deaths / 100000), 2)  # Simplified calculation
        }
    
    def _analyze_health_trends(self, region_id: int, current_conditions: List[HealthCondition]) -> Dict:
        """Analyze health trends compared to previous periods"""
        
        # Get previous year data for comparison
        previous_year = datetime.now().year - 1
        previous_conditions = db.session.query(HealthCondition).filter(
            HealthCondition.region_id == region_id,
            HealthCondition.data_year == previous_year,
            HealthCondition.is_active == True
        ).all()
        
        if not previous_conditions:
            return {'note': 'Insufficient historical data for trend analysis'}
        
        # Create comparison by condition code
        current_dict = {c.condition_code: c for c in current_conditions}
        previous_dict = {c.condition_code: c for c in previous_conditions}
        
        trends = {
            'increasing_conditions': [],
            'decreasing_conditions': [],
            'emerging_conditions': [],
            'overall_trend': 'stable'
        }
        
        total_change = 0
        comparison_count = 0
        
        for code in current_dict:
            current = current_dict[code]
            if code in previous_dict:
                previous = previous_dict[code]
                change_percentage = ((current.total_cases - previous.total_cases) / 
                                   max(previous.total_cases, 1)) * 100
                
                if change_percentage > 10:
                    trends['increasing_conditions'].append({
                        'condition': current.get_condition_name('en'),
                        'change_percentage': round(change_percentage, 1)
                    })
                elif change_percentage < -10:
                    trends['decreasing_conditions'].append({
                        'condition': current.get_condition_name('en'),
                        'change_percentage': round(change_percentage, 1)
                    })
                
                total_change += change_percentage
                comparison_count += 1
            else:
                trends['emerging_conditions'].append(current.get_condition_name('en'))
        
        # Determine overall trend
        if comparison_count > 0:
            avg_change = total_change / comparison_count
            if avg_change > 5:
                trends['overall_trend'] = 'worsening'
            elif avg_change < -5:
                trends['overall_trend'] = 'improving'
        
        return trends
    
    def _assess_outbreak_risk(self, condition: HealthCondition, region_id: int) -> Dict:
        """Assess outbreak risk for a specific condition"""
        
        # Get historical data for expected case calculation
        historical_data = db.session.query(HealthCondition).filter(
            HealthCondition.region_id == region_id,
            HealthCondition.condition_code == condition.condition_code,
            HealthCondition.data_year >= (datetime.now().year - 3),
            HealthCondition.data_year < datetime.now().year,
            HealthCondition.is_active == True
        ).all()
        
        if not historical_data:
            return {'is_outbreak': False, 'confidence': 0}
        
        # Calculate expected cases (average of previous years)
        historical_cases = [c.total_cases for c in historical_data]
        expected_cases = np.mean(historical_cases)
        std_dev = np.std(historical_cases) if len(historical_cases) > 1 else expected_cases * 0.2
        
        # Check if current cases exceed threshold
        threshold_cases = expected_cases * self.outbreak_threshold
        current_cases = condition.total_cases
        
        is_outbreak = current_cases > threshold_cases
        
        # Calculate confidence level
        z_score = (current_cases - expected_cases) / max(std_dev, 1)
        confidence = min(abs(z_score) * 20, 95)  # Simplified confidence calculation
        
        # Determine severity
        if current_cases > expected_cases * 3:
            severity = 'critical'
        elif current_cases > expected_cases * 2:
            severity = 'high'
        elif current_cases > expected_cases * 1.5:
            severity = 'moderate'
        else:
            severity = 'low'
        
        # Generate recommendations
        recommendations = self._generate_outbreak_recommendations(condition, severity)
        
        return {
            'is_outbreak': is_outbreak,
            'severity': severity,
            'expected_cases': int(expected_cases),
            'confidence': round(confidence, 1),
            'recommendations': recommendations
        }
    
    def _calculate_workforce_impact(self, condition: HealthCondition) -> Dict:
        """Calculate workforce impact of a health condition"""
        
        # Estimate workforce requirements based on condition characteristics
        impact = {
            'categories_affected': [],
            'fte_requirements': {},
            'cost_implications': {},
            'timeline': 'short_term'
        }
        
        # Determine affected workforce categories
        if condition.requires_specialist_care:
            impact['categories_affected'].append('specialists')
        if condition.requires_hospitalization:
            impact['categories_affected'].extend(['doctors', 'nurses'])
        if condition.is_chronic:
            impact['categories_affected'].extend(['primary_care', 'nurses'])
        
        # Calculate FTE requirements (simplified estimation)
        total_cases = condition.total_cases
        
        # Primary care requirements
        primary_care_visits = condition.primary_care_visits or (total_cases * 2)
        primary_care_fte = primary_care_visits / 4000  # Assuming 4000 visits per FTE per year
        
        # Specialist requirements
        specialist_visits = condition.specialist_visits or (total_cases * 0.3)
        specialist_fte = specialist_visits / 2000  # Assuming 2000 visits per specialist per year
        
        # Nursing requirements
        nursing_encounters = (condition.primary_care_visits or 0) + (condition.specialist_visits or 0)
        nursing_fte = nursing_encounters / 3000  # Assuming 3000 encounters per nurse per year
        
        impact['fte_requirements'] = {
            'primary_care': round(primary_care_fte, 2),
            'specialists': round(specialist_fte, 2),
            'nurses': round(nursing_fte, 2)
        }
        
        # Cost implications (simplified)
        avg_salary_doctor = 300000  # SAR per year
        avg_salary_nurse = 150000   # SAR per year
        
        total_cost = (
            primary_care_fte * avg_salary_doctor +
            specialist_fte * avg_salary_doctor * 1.5 +  # Specialists earn more
            nursing_fte * avg_salary_nurse
        )
        
        impact['cost_implications'] = {
            'annual_personnel_cost': round(total_cost, 2),
            'cost_per_case': round(total_cost / max(total_cases, 1), 2)
        }
        
        # Timeline assessment
        if condition.is_infectious or condition.priority_level == 'high':
            impact['timeline'] = 'immediate'
        elif condition.is_chronic:
            impact['timeline'] = 'long_term'
        else:
            impact['timeline'] = 'short_term'
        
        return impact
    
    def _calculate_prevention_potential(self, condition: HealthCondition) -> Dict:
        """Calculate prevention potential for a condition"""
        
        # Prevention potential varies by condition type
        prevention_rates = {
            'lifestyle': 60,    # 60% preventable through lifestyle changes
            'vaccination': 90,  # 90% preventable through vaccination
            'screening': 40,    # 40% preventable through early screening
            'environmental': 30 # 30% preventable through environmental changes
        }
        
        # Determine intervention type and potential
        if condition.lifestyle_related:
            intervention_type = 'lifestyle_modification'
            preventable_percentage = prevention_rates['lifestyle']
        elif condition.is_infectious and not condition.condition_code.startswith('COVID'):
            intervention_type = 'vaccination_program'
            preventable_percentage = prevention_rates['vaccination']
        else:
            intervention_type = 'screening_program'
            preventable_percentage = prevention_rates['screening']
        
        preventable_cases = int(condition.total_cases * (preventable_percentage / 100))
        
        # Calculate cost effectiveness (simplified)
        treatment_cost_per_case = condition.direct_cost_per_case or 5000
        prevention_cost_per_case = treatment_cost_per_case * 0.1  # Prevention is 10% of treatment cost
        
        cost_effectiveness = treatment_cost_per_case / prevention_cost_per_case
        
        # Workforce impact of prevention
        prevented_visits = preventable_cases * (condition.average_consultations_per_year or 2)
        workforce_reduction = prevented_visits / 3000  # Visits per FTE per year
        
        return {
            'preventable_percentage': preventable_percentage,
            'preventable_cases': preventable_cases,
            'intervention_type': intervention_type,
            'cost_effectiveness': round(cost_effectiveness, 2),
            'workforce_impact': {
                'prevented_visits': prevented_visits,
                'fte_reduction_potential': round(workforce_reduction, 2)
            }
        }
    
    def _calculate_prevention_savings(self, conditions: List[HealthCondition]) -> Dict:
        """Calculate total savings from prevention programs"""
        
        total_savings = 0
        total_prevention_cost = 0
        
        for condition in conditions:
            if condition.direct_cost_per_case:
                prevention_potential = self._calculate_prevention_potential(condition)
                prevented_cases = prevention_potential['preventable_cases']
                
                # Savings from prevented treatment costs
                treatment_savings = prevented_cases * condition.direct_cost_per_case
                
                # Cost of prevention program
                prevention_cost = prevented_cases * (condition.direct_cost_per_case * 0.1)
                
                total_savings += treatment_savings
                total_prevention_cost += prevention_cost
        
        net_savings = total_savings - total_prevention_cost
        roi = (net_savings / total_prevention_cost) if total_prevention_cost > 0 else 0
        
        return {
            'total_treatment_savings': round(total_savings, 2),
            'total_prevention_cost': round(total_prevention_cost, 2),
            'net_savings': round(net_savings, 2),
            'return_on_investment': round(roi, 2)
        }
    
    def _calculate_workforce_reduction_potential(self, conditions: List[HealthCondition]) -> Dict:
        """Calculate potential workforce reduction through prevention"""
        
        reduction_potential = {
            'primary_care': 0,
            'specialists': 0,
            'nurses': 0
        }
        
        for condition in conditions:
            prevention_potential = self._calculate_prevention_potential(condition)
            prevented_visits = prevention_potential['workforce_impact']['prevented_visits']
            
            # Distribute visit reductions across workforce categories
            primary_care_reduction = prevented_visits * 0.6 / 4000  # 60% primary care
            specialist_reduction = prevented_visits * 0.3 / 2000    # 30% specialist
            nursing_reduction = prevented_visits * 0.8 / 3000       # 80% nursing
            
            reduction_potential['primary_care'] += primary_care_reduction
            reduction_potential['specialists'] += specialist_reduction
            reduction_potential['nurses'] += nursing_reduction
        
        # Round the results
        for category in reduction_potential:
            reduction_potential[category] = round(reduction_potential[category], 2)
        
        return reduction_potential
    
    def _analyze_condition_trend(self, data_points: List[Dict]) -> Dict:
        """Analyze trend for a specific condition over time"""
        
        years = [dp['year'] for dp in data_points]
        cases = [dp['cases'] for dp in data_points]
        
        # Calculate linear trend
        if len(data_points) >= 3:
            slope = np.polyfit(years, cases, 1)[0]
            
            # Determine trend direction
            if slope > 10:
                direction = 'increasing'
            elif slope < -10:
                direction = 'decreasing'
            else:
                direction = 'stable'
            
            # Calculate percentage change
            first_year_cases = data_points[0]['cases']
            last_year_cases = data_points[-1]['cases']
            percentage_change = ((last_year_cases - first_year_cases) / 
                               max(first_year_cases, 1)) * 100
            
            return {
                'direction': direction,
                'slope': round(slope, 2),
                'percentage_change': round(percentage_change, 2),
                'years_analyzed': len(data_points),
                'data_quality': 'sufficient'
            }
        else:
            return {
                'direction': 'unknown',
                'data_quality': 'insufficient',
                'years_analyzed': len(data_points)
            }
    
    def _analyze_overall_health_trends(self, historical_data: List[HealthCondition]) -> Dict:
        """Analyze overall health trends across all conditions"""
        
        # Group by year
        yearly_data = {}
        for condition in historical_data:
            year = condition.data_year
            if year not in yearly_data:
                yearly_data[year] = {'total_cases': 0, 'conditions_count': 0}
            
            yearly_data[year]['total_cases'] += condition.total_cases
            yearly_data[year]['conditions_count'] += 1
        
        # Calculate trends
        years = sorted(yearly_data.keys())
        if len(years) >= 3:
            total_cases_trend = [yearly_data[year]['total_cases'] for year in years]
            slope = np.polyfit(years, total_cases_trend, 1)[0]
            
            return {
                'overall_disease_burden_trend': 'increasing' if slope > 0 else 'decreasing',
                'annual_case_change': round(slope, 2),
                'years_analyzed': len(years),
                'trend_reliability': 'high' if len(years) >= 5 else 'moderate'
            }
        
        return {'note': 'Insufficient data for overall trend analysis'}
    
    def _generate_outbreak_recommendations(self, condition: HealthCondition, severity: str) -> List[str]:
        """Generate outbreak response recommendations"""
        
        recommendations = []
        
        if severity in ['critical', 'high']:
            recommendations.extend([
                "Implement immediate outbreak response protocols",
                "Increase surveillance and case finding activities",
                "Mobilize additional healthcare workforce",
                "Coordinate with public health authorities"
            ])
        
        if condition.is_infectious:
            recommendations.extend([
                "Implement infection control measures",
                "Consider isolation and quarantine protocols",
                "Review vaccination strategies if applicable"
            ])
        
        if condition.is_notifiable:
            recommendations.append("Report to relevant health authorities immediately")
        
        recommendations.extend([
            "Monitor trends closely with daily reporting",
            "Prepare for potential healthcare surge capacity",
            "Communicate with healthcare facilities and staff"
        ])
        
        return recommendations
    
    def _calculate_health_comparison_metrics(self, regional_comparisons: Dict) -> Dict:
        """Calculate health comparison metrics across regions"""
        
        if not regional_comparisons:
            return {}
        
        chronic_burdens = [profile.chronic_disease_burden for profile in regional_comparisons.values()]
        infectious_burdens = [profile.infectious_disease_burden for profile in regional_comparisons.values()]
        
        return {
            'chronic_disease_variance': round(np.var(chronic_burdens), 2),
            'infectious_disease_variance': round(np.var(infectious_burdens), 2),
            'average_chronic_burden': round(np.mean(chronic_burdens), 2),
            'average_infectious_burden': round(np.mean(infectious_burdens), 2),
            'health_equity_index': self._calculate_health_equity_index(regional_comparisons)
        }
    
    def _rank_regions_by_health_indicators(self, regional_comparisons: Dict) -> Dict:
        """Rank regions by health indicators"""
        
        rankings = {}
        
        # Rank by chronic disease burden (lower is better)
        chronic_ranking = sorted(
            regional_comparisons.items(),
            key=lambda x: x[1].chronic_disease_burden
        )
        rankings['lowest_chronic_burden'] = [region for region, _ in chronic_ranking]
        
        # Rank by infectious disease burden (lower is better)
        infectious_ranking = sorted(
            regional_comparisons.items(),
            key=lambda x: x[1].infectious_disease_burden
        )
        rankings['lowest_infectious_burden'] = [region for region, _ in infectious_ranking]
        
        return rankings
    
    def _analyze_health_disparities(self, regional_comparisons: Dict) -> Dict:
        """Analyze health disparities across regions"""
        
        chronic_burdens = [profile.chronic_disease_burden for profile in regional_comparisons.values()]
        infectious_burdens = [profile.infectious_disease_burden for profile in regional_comparisons.values()]
        
        return {
            'chronic_disease_disparity': {
                'ratio_highest_to_lowest': round(max(chronic_burdens) / max(min(chronic_burdens), 0.1), 2),
                'coefficient_of_variation': round((np.std(chronic_burdens) / np.mean(chronic_burdens)) * 100, 2)
            },
            'infectious_disease_disparity': {
                'ratio_highest_to_lowest': round(max(infectious_burdens) / max(min(infectious_burdens), 0.1), 2),
                'coefficient_of_variation': round((np.std(infectious_burdens) / np.mean(infectious_burdens)) * 100, 2)
            }
        }
    
    def _identify_best_practices(self, regional_comparisons: Dict) -> Dict:
        """Identify best practices from top-performing regions"""
        
        # Find region with lowest overall disease burden
        best_region = min(
            regional_comparisons.items(),
            key=lambda x: x[1].chronic_disease_burden + x[1].infectious_disease_burden
        )
        
        return {
            'best_performing_region': best_region[0],
            'chronic_disease_burden': best_region[1].chronic_disease_burden,
            'infectious_disease_burden': best_region[1].infectious_disease_burden,
            'recommended_practices': [
                "Study prevention programs in best-performing regions",
                "Implement successful health promotion strategies",
                "Adapt effective surveillance systems",
                "Share best practices across regions"
            ]
        }
    
    def _calculate_health_equity_index(self, regional_comparisons: Dict) -> float:
        """Calculate health equity index across regions"""
        
        # Simplified health equity calculation
        chronic_burdens = [profile.chronic_disease_burden for profile in regional_comparisons.values()]
        
        if not chronic_burdens:
            return 0
        
        # Calculate coefficient of variation (lower means more equitable)
        cv = (np.std(chronic_burdens) / np.mean(chronic_burdens)) * 100
        
        # Convert to equity index (higher means more equitable)
        equity_index = max(0, 100 - cv)
        
        return round(equity_index, 2)
    
    def _create_empty_profile(self, region_id: int) -> EpidemiologicalProfile:
        """Create empty epidemiological profile when data is unavailable"""
        return EpidemiologicalProfile(
            region_id=region_id,
            total_conditions=0,
            chronic_disease_burden=0.0,
            infectious_disease_burden=0.0,
            top_conditions=[],
            mortality_indicators={},
            health_trends={}
        ) 