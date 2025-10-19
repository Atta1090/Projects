"""
Workforce Calculator Service
Enhanced business logic for healthcare workforce planning calculations
Implements advanced supply/demand projections, gap analysis, and scenario modeling
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from app import db
from app.models.region import Region
from app.models.healthcare_worker import HealthcareWorkerCategory
from app.models.workforce import WorkforceStock
from app.models.population import PopulationData
from app.models.health_status import HealthCondition
from app.models.service_standards import ServiceStandard


@dataclass
class ProjectionResult:
    """Data class for projection results"""
    year: int
    value: float
    confidence_lower: float
    confidence_upper: float
    assumptions: Dict


@dataclass
class GapAnalysisResult:
    """Data class for gap analysis results"""
    year: int
    supply: float
    demand: float
    gap: float
    gap_percentage: float
    severity: str  # 'surplus', 'balanced', 'shortage', 'critical_shortage'
    recommendations: List[str]


@dataclass
class TrendAnalysisResult:
    """Data class for historical trend analysis"""
    trend_direction: str  # 'increasing', 'decreasing', 'stable'
    annual_growth_rate: float
    r_squared: float
    confidence_level: float
    seasonal_patterns: Dict
    anomalies_detected: List[Dict]


@dataclass
class RiskAssessmentResult:
    """Data class for risk assessment"""
    overall_risk_score: float  # 0-10 scale
    risk_factors: List[Dict]
    mitigation_strategies: List[str]
    probability_scenarios: Dict


class WorkforceCalculatorService:
    """
    Enhanced service for workforce planning calculations
    Implements sophisticated algorithms for supply/demand forecasting with advanced analytics
    """
    
    def __init__(self):
        self.confidence_level = 95.0
        self.monte_carlo_iterations = 1000
        
    def calculate_supply_projection(self, region_id: int, category_id: int, years: int = 10) -> List[ProjectionResult]:
        """
        Enhanced workforce supply projection with advanced modeling
        Supports up to 15-year projections with sophisticated algorithms
        """
        
        # Get current workforce data
        current_workforce = WorkforceStock.get_latest_by_region_category(region_id, category_id)
        if not current_workforce:
            return self._create_empty_projections(years)
        
        # Get category parameters
        category = HealthcareWorkerCategory.find_by_id(category_id)
        if not category:
            return self._create_empty_projections(years)
        
        # Enhanced base parameters with Saudi-specific factors
        initial_stock = current_workforce.current_count
        base_attrition_rate = self._calculate_dynamic_attrition_rate(region_id, category_id)
        
        # Get enhanced graduation and recruitment rates
        graduation_rate = self._estimate_enhanced_graduation_rate(region_id, category_id)
        recruitment_rate = self._estimate_enhanced_recruitment_rate(region_id, category_id)
        
        # Saudi Vision 2030 impact factors
        vision_2030_factors = self._get_vision_2030_impact_factors(category_id, years)
        
        projections = []
        current_stock = initial_stock
        
        for year in range(1, years + 1):
            # Dynamic attrition rate (changes over time)
            dynamic_attrition = base_attrition_rate * (1 + 0.01 * year)  # Slight increase over time
            
            # Vision 2030 adjustments
            vision_factor = vision_2030_factors.get(f'year_{year}', 1.0)
            
            # Enhanced supply formula with multiple factors
            stock_after_attrition = current_stock * (1 - dynamic_attrition)
            
            # Graduation with quality and capacity constraints
            new_graduates = self._calculate_realistic_graduates(graduation_rate, year, region_id)
            
            # International recruitment with policy constraints
            international_recruits = self._calculate_international_recruitment(recruitment_rate, year, category_id)
            
            # Internal transfers and career progression
            internal_growth = self._calculate_internal_growth(current_stock, category_id, year)
            
            # Technology impact on workforce needs
            technology_adjustment = self._calculate_technology_impact(category_id, year)
            
            projected_stock = (stock_after_attrition + new_graduates + international_recruits + internal_growth) * technology_adjustment * vision_factor
            
            # Enhanced Monte Carlo simulation with multiple variables
            confidence_bounds = self._enhanced_monte_carlo_supply_simulation(
                current_stock, dynamic_attrition, graduation_rate, recruitment_rate, 
                year, category_id, vision_factor
            )
            
            # Enhanced assumptions tracking
            assumptions = {
                'base_attrition_rate': base_attrition_rate,
                'dynamic_attrition_rate': dynamic_attrition,
                'graduation_rate': graduation_rate,
                'recruitment_rate': recruitment_rate,
                'vision_2030_factor': vision_factor,
                'technology_adjustment': technology_adjustment,
                'base_stock': initial_stock,
                'methodology': 'Enhanced Monte Carlo with Saudi Vision 2030 factors',
                'data_quality_score': current_workforce.data_quality_score if hasattr(current_workforce, 'data_quality_score') else 0.9,
                'annual_growth_rate': (projected_stock / current_stock - 1) if current_stock > 0 else 0,
                'timestamp': datetime.now().isoformat()
            }
            
            projections.append(ProjectionResult(
                year=datetime.now().year + year,
                value=round(projected_stock),
                confidence_lower=round(confidence_bounds[0]),
                confidence_upper=round(confidence_bounds[1]),
                assumptions=assumptions
            ))
            
            current_stock = projected_stock
        
        return projections
    
    def calculate_demand_projection(self, region_id: int, category_id: int, years: int = 10) -> List[ProjectionResult]:
        """
        Enhanced workforce demand projection with advanced demographic and health modeling
        """
        
        # Get region and population data
        region = Region.find_by_id(region_id)
        if not region:
            return self._create_empty_projections(years)
        
        population_data = PopulationData.get_latest_by_region(region_id)
        if not population_data:
            return self._create_empty_projections(years)
        
        # Get healthcare category and service standards
        category = HealthcareWorkerCategory.find_by_id(category_id)
        if not category:
            return self._create_empty_projections(years)
        
        projections = []
        
        for year in range(1, years + 1):
            # Enhanced population projection with demographic transition
            projected_population = self._enhanced_population_projection(population_data, year, region_id)
            
            # Advanced health demand factors
            health_demand_factor = self._calculate_advanced_health_demand_factor(region_id, year)
            
            # Technology and service delivery evolution
            service_evolution_factor = self._calculate_service_evolution_factor(category_id, year)
            
            # Saudi-specific healthcare utilization patterns
            utilization_factor = self._calculate_saudi_utilization_patterns(region_id, category_id, year)
            
            # Enhanced service requirements calculation
            service_requirements = self._calculate_advanced_service_requirements(
                category_id, projected_population, year
            )
            
            # Apply workforce standards with quality adjustments
            workforce_needed = self._apply_enhanced_workforce_standards(
                category_id, service_requirements, health_demand_factor, 
                service_evolution_factor, utilization_factor
            )
            
            # Policy and regulatory impact
            policy_impact = self._calculate_policy_impact(category_id, year)
            workforce_needed *= policy_impact
            
            # Enhanced confidence intervals for demand
            confidence_bounds = self._enhanced_monte_carlo_demand_simulation(
                projected_population, health_demand_factor, service_requirements, year, category_id
            )
            
            # Enhanced assumptions with detailed factors
            assumptions = {
                'projected_population': projected_population,
                'health_demand_factor': health_demand_factor,
                'service_evolution_factor': service_evolution_factor,
                'utilization_factor': utilization_factor,
                'policy_impact': policy_impact,
                'service_requirements': service_requirements,
                'category': category.name_en,
                'methodology': 'Advanced demographic and health modeling',
                'demand_drivers': [
                    'Population aging',
                    'Chronic disease prevalence',
                    'Service quality improvements',
                    'Technology adoption',
                    'Saudi Vision 2030 health goals'
                ],
                'confidence_methodology': 'Monte Carlo with demographic uncertainty',
                'timestamp': datetime.now().isoformat()
            }
            
            projections.append(ProjectionResult(
                year=datetime.now().year + year,
                value=round(workforce_needed),
                confidence_lower=round(confidence_bounds[0]),
                confidence_upper=round(confidence_bounds[1]),
                assumptions=assumptions
            ))
        
        return projections
    
    def generate_gap_analysis(self, region_id: int, category_id: int, years: int = 10) -> List[GapAnalysisResult]:
        """
        Enhanced comprehensive gap analysis with advanced recommendations
        """
        
        supply_projections = self.calculate_supply_projection(region_id, category_id, years)
        demand_projections = self.calculate_demand_projection(region_id, category_id, years)
        
        gap_analysis = []
        
        for i in range(len(supply_projections)):
            supply = supply_projections[i]
            demand = demand_projections[i]
            
            gap = supply.value - demand.value
            gap_percentage = (gap / demand.value * 100) if demand.value > 0 else 0
            
            # Enhanced severity assessment with multiple criteria
            severity, recommendations = self._enhanced_gap_severity_assessment(
                gap, gap_percentage, category_id, region_id, supply.year
            )
            
            gap_analysis.append(GapAnalysisResult(
                year=supply.year,
                supply=supply.value,
                demand=demand.value,
                gap=gap,
                gap_percentage=round(gap_percentage, 2),
                severity=severity,
                recommendations=recommendations
            ))
        
        return gap_analysis
    
    def analyze_historical_trends(self, region_id: int, category_id: int) -> TrendAnalysisResult:
        """
        Analyze historical trends in workforce data
        """
        # Get historical data (simulated for demo)
        historical_data = self._get_historical_workforce_data(region_id, category_id)
        
        if len(historical_data) < 3:
            return TrendAnalysisResult(
                trend_direction='insufficient_data',
                annual_growth_rate=0.0,
                r_squared=0.0,
                confidence_level=0.0,
                seasonal_patterns={},
                anomalies_detected=[]
            )
        
        # Calculate trend statistics
        years = list(range(len(historical_data)))
        values = historical_data
        
        # Linear regression for trend
        trend_slope = np.polyfit(years, values, 1)[0]
        trend_direction = 'increasing' if trend_slope > 0.02 else 'decreasing' if trend_slope < -0.02 else 'stable'
        
        # Calculate R-squared
        trend_line = np.polyval(np.polyfit(years, values, 1), years)
        ss_res = np.sum((values - trend_line) ** 2)
        ss_tot = np.sum((values - np.mean(values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Annual growth rate
        annual_growth_rate = trend_slope / np.mean(values) if np.mean(values) > 0 else 0
        
        # Detect anomalies (simplified)
        std_dev = np.std(values)
        mean_val = np.mean(values)
        anomalies = []
        for i, val in enumerate(values):
            if abs(val - mean_val) > 2 * std_dev:
                anomalies.append({
                    'year': 2024 - len(values) + i,
                    'value': val,
                    'deviation': abs(val - mean_val),
                    'type': 'outlier'
                })
        
        return TrendAnalysisResult(
            trend_direction=trend_direction,
            annual_growth_rate=round(annual_growth_rate * 100, 2),  # Convert to percentage
            r_squared=round(r_squared, 3),
            confidence_level=85.0,
            seasonal_patterns={'quarterly_variation': 0.05},
            anomalies_detected=anomalies
        )
    
    def assess_projection_risks(self, region_id: int, category_id: int, years: int) -> RiskAssessmentResult:
        """
        Assess risks associated with workforce projections
        """
        risk_factors = []
        overall_risk_score = 0.0
        
        # Demographic risk factors
        population_data = PopulationData.get_latest_by_region(region_id)
        if population_data:
            aging_rate = population_data.age_60_plus / population_data.total_population
            if aging_rate > 0.15:  # 15% elderly population
                risk_factors.append({
                    'factor': 'Aging Population',
                    'severity': 'high' if aging_rate > 0.20 else 'medium',
                    'impact': 'Increased healthcare demand',
                    'score': 7.5 if aging_rate > 0.20 else 5.0
                })
                overall_risk_score += 7.5 if aging_rate > 0.20 else 5.0
        
        # Economic risk factors
        risk_factors.append({
            'factor': 'Economic Volatility',
            'severity': 'medium',
            'impact': 'Budget constraints affecting recruitment',
            'score': 4.0
        })
        overall_risk_score += 4.0
        
        # Technology disruption risk
        category = HealthcareWorkerCategory.find_by_id(category_id)
        if category and category.category_code in ['MTC', 'PHA']:  # More susceptible to automation
            risk_factors.append({
                'factor': 'Technology Disruption',
                'severity': 'medium',
                'impact': 'Automation may reduce workforce needs',
                'score': 5.5
            })
            overall_risk_score += 5.5
        
        # Training capacity constraints
        risk_factors.append({
            'factor': 'Training Capacity Limitations',
            'severity': 'medium',
            'impact': 'Limited ability to scale workforce quickly',
            'score': 4.5
        })
        overall_risk_score += 4.5
        
        # Normalize risk score to 0-10 scale
        overall_risk_score = min(overall_risk_score / len(risk_factors), 10.0)
        
        # Mitigation strategies
        mitigation_strategies = [
            'Diversify recruitment sources including international partnerships',
            'Invest in technology training and reskilling programs',
            'Develop flexible workforce deployment strategies',
            'Strengthen public-private partnerships in healthcare delivery',
            'Implement predictive analytics for early warning systems'
        ]
        
        # Probability scenarios
        probability_scenarios = {
            'best_case': {'probability': 0.25, 'description': 'All risk factors mitigated successfully'},
            'most_likely': {'probability': 0.50, 'description': 'Some challenges but manageable impact'},
            'worst_case': {'probability': 0.25, 'description': 'Multiple risk factors materialize simultaneously'}
        }
        
        return RiskAssessmentResult(
            overall_risk_score=round(overall_risk_score, 2),
            risk_factors=risk_factors,
            mitigation_strategies=mitigation_strategies,
            probability_scenarios=probability_scenarios
        )
    
    def sensitivity_analysis(self, region_id: int, category_id: int, parameters: List[str]) -> Dict:
        """
        Perform sensitivity analysis on key parameters
        """
        base_projections = self.calculate_supply_projection(region_id, category_id, 5)
        base_final_value = base_projections[-1].value if base_projections else 0
        
        sensitivity_results = {}
        
        for param in parameters:
            param_variations = {}
            
            # Test parameter variations (-20%, -10%, +10%, +20%)
            for variation in [-0.2, -0.1, 0.1, 0.2]:
                # Simulate modified calculation (simplified)
                if param == 'graduation_rate':
                    modified_value = base_final_value * (1 + variation * 0.3)  # Graduation has moderate impact
                elif param == 'attrition_rate':
                    modified_value = base_final_value * (1 - variation * 0.4)  # Attrition has high impact
                elif param == 'population_growth':
                    modified_value = base_final_value * (1 + variation * 0.2)  # Population has lower impact on supply
                elif param == 'technology_adoption':
                    modified_value = base_final_value * (1 - variation * 0.15)  # Technology reduces workforce needs
                else:
                    modified_value = base_final_value * (1 + variation * 0.1)  # Default impact
                
                impact_percentage = ((modified_value - base_final_value) / base_final_value * 100) if base_final_value > 0 else 0
                
                param_variations[f'{variation*100:+.0f}%'] = {
                    'modified_value': round(modified_value),
                    'impact_percentage': round(impact_percentage, 2),
                    'elasticity': round(impact_percentage / (variation * 100), 3) if variation != 0 else 0
                }
            
            sensitivity_results[param] = param_variations
        
        return {
            'base_value': base_final_value,
            'sensitivity_analysis': sensitivity_results,
            'most_sensitive_parameter': max(parameters, key=lambda p: max(abs(v['elasticity']) for v in sensitivity_results[p].values())),
            'analysis_methodology': 'Elasticity-based sensitivity analysis with ±20% parameter variations'
        }
    
    def identify_risk_factors(self, region_id: int, category_id: int, years: int) -> List[Dict]:
        """
        Identify specific risk factors for workforce planning
        """
        risk_factors = []
        
        # Get current data
        current_workforce = WorkforceStock.get_latest_by_region_category(region_id, category_id)
        category = HealthcareWorkerCategory.find_by_id(category_id)
        
        if current_workforce:
            # High attrition risk
            if current_workforce.attrition_rate > 15.0:
                risk_factors.append({
                    'risk_type': 'High Attrition Rate',
                    'current_value': current_workforce.attrition_rate,
                    'threshold': 15.0,
                    'severity': 'high',
                    'impact': 'Accelerated workforce depletion',
                    'timeframe': 'immediate',
                    'mitigation': 'Improve retention programs and working conditions'
                })
            
            # Aging workforce risk
            if hasattr(current_workforce, 'age_50_plus') and current_workforce.age_50_plus:
                aging_percentage = (current_workforce.age_50_plus / current_workforce.current_count * 100) if current_workforce.current_count > 0 else 0
                if aging_percentage > 30:
                    risk_factors.append({
                        'risk_type': 'Aging Workforce',
                        'current_value': aging_percentage,
                        'threshold': 30.0,
                        'severity': 'medium',
                        'impact': 'Mass retirements in 5-10 years',
                        'timeframe': 'medium-term',
                        'mitigation': 'Accelerate recruitment and knowledge transfer programs'
                    })
        
        if category and category.is_critical_shortage:
            risk_factors.append({
                'risk_type': 'Critical Specialty Shortage',
                'current_value': 'Critical',
                'threshold': 'Normal',
                'severity': 'critical',
                'impact': 'Service delivery disruption',
                'timeframe': 'immediate',
                'mitigation': 'Emergency recruitment and temporary staffing solutions'
            })
        
        # Add contextual risk factors
        risk_factors.extend([
            {
                'risk_type': 'Economic Uncertainty',
                'current_value': 'Moderate',
                'threshold': 'Low',
                'severity': 'medium',
                'impact': 'Budget constraints on hiring and training',
                'timeframe': 'short-term',
                'mitigation': 'Diversify funding sources and optimize resource allocation'
            },
            {
                'risk_type': 'Technological Disruption',
                'current_value': 'Accelerating',
                'threshold': 'Stable',
                'severity': 'medium',
                'impact': 'Changing skill requirements and job displacement',
                'timeframe': 'long-term',
                'mitigation': 'Continuous learning programs and skill development initiatives'
            }
        ])
        
        return risk_factors
    
    # Enhanced helper methods
    def _calculate_dynamic_attrition_rate(self, region_id: int, category_id: int) -> float:
        """Calculate dynamic attrition rate based on multiple factors"""
        base_rate = 0.08  # 8% base attrition
        
        # Regional factors
        region = Region.find_by_id(region_id)
        if region:
            # Urban regions typically have higher attrition due to more opportunities
            urban_factor = (region.urban_population / region.total_population) * 0.02
            base_rate += urban_factor
        
        # Category-specific factors
        category = HealthcareWorkerCategory.find_by_id(category_id)
        if category:
            if category.is_critical_shortage:
                base_rate += 0.03  # Higher attrition in shortage areas due to burnout
            if category.average_salary and category.average_salary < 100000:  # Below average salary
                base_rate += 0.02
        
        return min(base_rate, 0.25)  # Cap at 25%
    
    def _estimate_enhanced_graduation_rate(self, region_id: int, category_id: int) -> float:
        """Enhanced graduation rate estimation with capacity constraints"""
        base_rates = {
            'PHY': 200,   # Physicians
            'NUR': 400,   # Nurses  
            'PHA': 100,   # Pharmacists
            'MTC': 250,   # Medical Technicians
            'DEN': 80,    # Dentists
            'MHS': 60,    # Mental Health Specialists
            'EMP': 40,    # Emergency Medicine
            'PHT': 120    # Physiotherapists
        }
        
        category = HealthcareWorkerCategory.find_by_id(category_id)
        if not category:
            return 50
        
        base_rate = base_rates.get(category.category_code, 75)
        
        # Regional adjustment based on training capacity
        region = Region.find_by_id(region_id)
        if region:
            # Larger regions have more training institutions
            population_factor = min(region.total_population / 1000000, 2.0)  # Max 2x factor
            base_rate *= population_factor
        
        # Quality and capacity constraints
        capacity_utilization = 0.85  # Assuming 85% capacity utilization
        quality_factor = 0.92  # 92% graduation success rate
        
        return base_rate * capacity_utilization * quality_factor
    
    def _estimate_enhanced_recruitment_rate(self, region_id: int, category_id: int) -> float:
        """Enhanced recruitment rate with policy and economic factors"""
        base_rates = {
            'PHY': 120,   # International physician recruitment
            'NUR': 180,   # International nursing recruitment
            'PHA': 60,    # Pharmacist recruitment
            'MTC': 100,   # Technician recruitment
            'DEN': 40,    # Dentist recruitment
            'MHS': 80,    # Mental health recruitment (high demand)
            'EMP': 50,    # Emergency medicine recruitment
            'PHT': 70     # Physiotherapist recruitment
        }
        
        category = HealthcareWorkerCategory.find_by_id(category_id)
        if not category:
            return 25
        
        base_rate = base_rates.get(category.category_code, 50)
        
        # Saudi Vision 2030 localization impact
        saudization_factor = 0.7 if category.category_code in ['PHY', 'NUR'] else 0.9
        
        # Economic attractiveness factor
        region = Region.find_by_id(region_id)
        economic_factor = 1.2 if region and region.gdp_per_capita > 70000 else 1.0
        
        return base_rate * saudization_factor * economic_factor
    
    def _get_vision_2030_impact_factors(self, category_id: int, years: int) -> Dict:
        """Get Saudi Vision 2030 impact factors for different years"""
        factors = {}
        
        # Vision 2030 targets progressive implementation
        base_factor = 1.0
        annual_increment = 0.02  # 2% annual improvement target
        
        for year in range(1, years + 1):
            # Accelerated improvement in early years, stabilizing later
            if year <= 6:  # Up to 2030
                factor = base_factor + (annual_increment * year)
            else:  # Post-2030 stabilization
                factor = base_factor + (annual_increment * 6) + (0.01 * (year - 6))
            
            factors[f'year_{year}'] = min(factor, 1.5)  # Cap at 50% improvement
        
        return factors
    
    def _calculate_realistic_graduates(self, graduation_rate: float, year: int, region_id: int) -> float:
        """Calculate realistic graduate numbers with capacity and quality constraints"""
        # Base graduation with year-over-year growth
        base_graduates = graduation_rate * (1 + 0.03 * min(year, 5))  # 3% annual growth for 5 years
        
        # Capacity constraints
        capacity_factor = min(1.0 + 0.05 * year, 1.3)  # Gradual capacity expansion, max 30%
        
        # Quality maintenance factor
        quality_factor = max(0.9, 1.0 - 0.01 * year)  # Slight quality pressure with rapid expansion
        
        return base_graduates * capacity_factor * quality_factor
    
    def _calculate_international_recruitment(self, recruitment_rate: float, year: int, category_id: int) -> float:
        """Calculate international recruitment with policy and market constraints"""
        # Saudization policy impact (gradual reduction in international recruitment)
        saudization_reduction = 0.03 * year  # 3% annual reduction
        policy_factor = max(0.5, 1.0 - saudization_reduction)  # Minimum 50% of original rate
        
        # Market competition factor
        competition_factor = 1.0 - 0.02 * year  # Increasing global competition
        
        # Economic attractiveness
        economic_factor = 1.0 + 0.01 * year  # Improving economic conditions
        
        return recruitment_rate * policy_factor * competition_factor * economic_factor
    
    def _calculate_internal_growth(self, current_stock: float, category_id: int, year: int) -> float:
        """Calculate internal growth from career progression and specialization"""
        # Career progression and internal mobility
        internal_growth_rate = 0.02  # 2% annual internal growth
        
        # Specialization and advancement opportunities
        advancement_factor = 1.0 + 0.01 * year  # Improving career pathways
        
        return current_stock * internal_growth_rate * advancement_factor
    
    def _calculate_technology_impact(self, category_id: int, year: int) -> float:
        """Calculate technology impact on workforce requirements"""
        category = HealthcareWorkerCategory.find_by_id(category_id)
        if not category:
            return 1.0
        
        # Different categories have different technology susceptibility
        tech_impact_rates = {
            'PHY': 0.005,   # Moderate positive impact (AI assistance)
            'NUR': 0.002,   # Low impact (human-centric care)
            'PHA': -0.01,   # Moderate negative impact (automation)
            'MTC': -0.015,  # Higher negative impact (automated testing)
            'DEN': 0.003,   # Low positive impact (precision tools)
            'MHS': 0.001,   # Minimal impact (human interaction crucial)
            'EMP': 0.008,   # Positive impact (decision support systems)
            'PHT': 0.002    # Low positive impact (rehabilitation tech)
        }
        
        annual_impact = tech_impact_rates.get(category.category_code, 0.0)
        cumulative_impact = 1.0 + (annual_impact * year)
        
        return max(0.7, min(cumulative_impact, 1.3))  # Bound between 70%-130%
    
    def _enhanced_monte_carlo_supply_simulation(self, initial_stock: int, attrition_rate: float, 
                                              graduation_rate: float, recruitment_rate: float, 
                                              years: int, category_id: int, vision_factor: float) -> Tuple[float, float]:
        """Enhanced Monte Carlo simulation with additional variables"""
        
        simulations = []
        
        for _ in range(self.monte_carlo_iterations):
            # Enhanced parameter variations
            sim_attrition = np.random.normal(attrition_rate, attrition_rate * 0.25)
            sim_graduation = np.random.normal(graduation_rate, graduation_rate * 0.35)
            sim_recruitment = np.random.normal(recruitment_rate, recruitment_rate * 0.45)
            sim_vision_factor = np.random.normal(vision_factor, vision_factor * 0.1)
            
            # Economic uncertainty factor
            economic_shock = np.random.normal(1.0, 0.05)  # ±5% economic variation
            
            # Policy uncertainty
            policy_factor = np.random.uniform(0.9, 1.1)  # ±10% policy variation
            
            # Ensure non-negative values with realistic bounds
            sim_attrition = max(0.01, min(sim_attrition, 0.4))  # 1%-40%
            sim_graduation = max(0, sim_graduation * economic_shock)
            sim_recruitment = max(0, sim_recruitment * policy_factor)
            sim_vision_factor = max(0.8, min(sim_vision_factor, 1.5))
            
            # Run enhanced projection
            current_stock = initial_stock
            for year in range(years):
                technology_factor = self._calculate_technology_impact(category_id, year + 1)
                
                stock_after_attrition = current_stock * (1 - sim_attrition)
                new_graduates = sim_graduation * (year + 1)
                new_recruits = sim_recruitment * (year + 1)
                
                current_stock = (stock_after_attrition + new_graduates + new_recruits) * technology_factor * sim_vision_factor
            
            simulations.append(current_stock)
        
        # Calculate enhanced confidence intervals
        confidence_level = (100 - self.confidence_level) / 2
        lower_bound = np.percentile(simulations, confidence_level)
        upper_bound = np.percentile(simulations, 100 - confidence_level)
        
        return (lower_bound, upper_bound)
    
    def _enhanced_monte_carlo_demand_simulation(self, population: int, demand_factor: float, 
                                              service_requirements: float, years: int, category_id: int) -> Tuple[float, float]:
        """Enhanced Monte Carlo simulation for demand projections"""
        
        simulations = []
        
        for _ in range(self.monte_carlo_iterations):
            # Enhanced demand parameter variations
            sim_population = np.random.normal(population, population * 0.05)  # ±5% population uncertainty
            sim_demand_factor = np.random.normal(demand_factor, demand_factor * 0.12)  # ±12% demand variation
            sim_services = np.random.normal(service_requirements, service_requirements * 0.15)  # ±15% service variation
            
            # Health trend variations
            health_trend = np.random.normal(1.0, 0.08)  # ±8% health trend variation
            
            # Policy and service delivery changes
            service_policy_factor = np.random.uniform(0.9, 1.15)  # Service expansion/contraction
            
            # Technology impact on service delivery
            tech_efficiency = np.random.normal(1.0, 0.06)  # Technology efficiency variation
            
            # Ensure positive values with realistic bounds
            sim_population = max(population * 0.8, sim_population)
            sim_demand_factor = max(0.5, min(sim_demand_factor, 3.0))
            sim_services = max(0, sim_services * health_trend * service_policy_factor)
            
            # Calculate demand with enhanced factors
            workforce_needed = (sim_services * sim_demand_factor) / (3000 * tech_efficiency)  # Adjusted baseline
            simulations.append(workforce_needed)
        
        # Calculate confidence intervals
        confidence_level = (100 - self.confidence_level) / 2
        lower_bound = np.percentile(simulations, confidence_level)
        upper_bound = np.percentile(simulations, 100 - confidence_level)
        
        return (lower_bound, upper_bound)
    
    def _enhanced_gap_severity_assessment(self, gap: float, gap_percentage: float, 
                                        category_id: int, region_id: int, year: int) -> Tuple[str, List[str]]:
        """Enhanced gap severity assessment with contextual recommendations"""
        
        category = HealthcareWorkerCategory.find_by_id(category_id)
        region = Region.find_by_id(region_id)
        
        category_name = category.name_en if category else "Healthcare Workers"
        region_name = region.name_en if region else "Region"
        
        # Enhanced severity assessment with multiple criteria
        severity_score = 0
        
        # Base gap severity
        if gap_percentage < -25:
            severity_score += 5
        elif gap_percentage < -15:
            severity_score += 4
        elif gap_percentage < -5:
            severity_score += 3
        elif gap_percentage < 5:
            severity_score += 2
        else:
            severity_score += 1
        
        # Critical specialty factor
        if category and category.is_critical_shortage:
            severity_score += 1
        
        # Regional factors
        if region:
            # Remote regions have higher severity due to access challenges
            if region.population_density < 10:  # Low density = remote
                severity_score += 1
            # High population regions have system-wide impact
            if region.total_population > 5000000:
                severity_score += 1
        
        # Time factor (future shortages are more critical)
        if year > datetime.now().year + 5:
            severity_score += 1
        
        # Determine severity level
        if severity_score >= 7:
            severity = "critical_shortage"
        elif severity_score >= 5:
            severity = "shortage"
        elif severity_score >= 3:
            severity = "balanced"
        else:
            severity = "surplus"
        
        # Generate contextual recommendations
        recommendations = self._generate_contextual_recommendations(
            severity, gap, gap_percentage, category_id, region_id, year
        )
        
        return severity, recommendations
    
    def _generate_contextual_recommendations(self, severity: str, gap: float, gap_percentage: float,
                                           category_id: int, region_id: int, year: int) -> List[str]:
        """Generate contextual recommendations based on specific situation"""
        
        category = HealthcareWorkerCategory.find_by_id(category_id)
        region = Region.find_by_id(region_id)
        
        category_name = category.name_en if category else "healthcare workers"
        region_name = region.name_en if region else "the region"
        
        recommendations = []
        
        if severity == "critical_shortage":
            recommendations.extend([
                f"🚨 URGENT: Implement emergency {category_name.lower()} recruitment in {region_name}",
                f"🎯 Fast-track training programs with 25% capacity increase",
                f"💼 Establish international recruitment partnerships for immediate deployment",
                f"📋 Activate crisis staffing protocols and temporary assignments",
                f"🔄 Redistribute workforce from surplus regions if available",
                f"💰 Implement retention bonuses and improved compensation packages"
            ])
        elif severity == "shortage":
            recommendations.extend([
                f"📈 Increase {category_name.lower()} recruitment by {abs(gap_percentage):.0f}% in {region_name}",
                f"🎓 Expand training program capacity by 15-20%",
                f"🌍 Explore international recruitment opportunities",
                f"🔄 Optimize current workforce deployment and productivity",
                f"📊 Implement retention strategies to reduce attrition",
                f"🤝 Develop public-private partnerships for workforce sharing"
            ])
        elif severity == "balanced":
            recommendations.extend([
                f"📊 Monitor {category_name.lower()} trends closely in {region_name}",
                f"🎯 Maintain current recruitment and training levels",
                f"🔧 Focus on productivity improvements and workflow optimization",
                f"📈 Prepare for future demand increases",
                f"💡 Invest in technology to enhance service delivery efficiency"
            ])
        else:  # surplus
            recommendations.extend([
                f"✅ {category_name} capacity is adequate in {region_name}",
                f"🔄 Consider redistribution to shortage areas",
                f"📚 Focus on advanced training and specialization",
                f"💼 Explore expansion of services or quality improvements",
                f"🎯 Optimize resource allocation for maximum impact"
            ])
        
        # Add time-specific recommendations
        if year > datetime.now().year + 7:
            recommendations.append(f"⏰ Long-term planning: Review and adjust strategies by {year-3}")
        
        # Add regional-specific recommendations
        if region:
            if region.population_density < 10:
                recommendations.append("🏔️ Consider telemedicine and mobile health services for remote access")
            if region.total_population > 5000000:
                recommendations.append("🏙️ Implement large-scale workforce management systems")
        
        return recommendations[:6]  # Return top 6 recommendations
    
    def _get_historical_workforce_data(self, region_id: int, category_id: int) -> List[float]:
        """Get historical workforce data (simulated for demo purposes)"""
        # In a real system, this would query actual historical data
        # For demo, generate realistic trend data
        
        base_value = 1000
        trend = 0.03  # 3% annual growth
        noise_factor = 0.1
        
        historical_data = []
        for i in range(5):  # 5 years of historical data
            year_value = base_value * ((1 + trend) ** i)
            # Add some realistic noise
            noise = np.random.normal(0, year_value * noise_factor)
            historical_data.append(year_value + noise)
        
        return historical_data 