"""
Population Service
Handles demographic analysis, population projections, and health needs assessment
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from app import db
from app.models.region import Region
from app.models.population import PopulationData
from app.models.health_status import HealthCondition


@dataclass
class DemographicProfile:
    """Demographic profile for a region"""
    total_population: int
    age_distribution: Dict[str, float]
    gender_distribution: Dict[str, float]
    nationality_distribution: Dict[str, float]
    education_distribution: Dict[str, float]
    dependency_ratio: float
    median_age: float


@dataclass
class PopulationProjection:
    """Population projection result"""
    year: int
    total_population: int
    age_groups: Dict[str, int]
    confidence_interval: Tuple[int, int]
    growth_rate: float
    assumptions: Dict


class PopulationService:
    """
    Service for population analysis and demographic projections
    Provides insights for healthcare workforce planning
    """
    
    def __init__(self):
        self.projection_confidence = 95.0
        
    def get_demographic_profile(self, region_id: int, year: Optional[int] = None) -> DemographicProfile:
        """
        Get comprehensive demographic profile for a region
        """
        if year is None:
            year = datetime.now().year
            
        population_data = PopulationData.get_latest_by_region(region_id)
        if not population_data:
            return self._create_empty_profile()
        
        # Calculate age distribution
        age_distribution = population_data.get_age_group_percentages()
        
        # Calculate gender distribution
        total_pop = population_data.total_population
        gender_distribution = {
            'male': round((population_data.male_count / total_pop) * 100, 1) if total_pop > 0 else 0,
            'female': round((population_data.female_count / total_pop) * 100, 1) if total_pop > 0 else 0
        }
        
        # Calculate nationality distribution
        nationality_distribution = {
            'saudi': round(population_data.saudi_percentage, 1),
            'non_saudi': round(100 - population_data.saudi_percentage, 1)
        }
        
        # Get education distribution
        education_distribution = population_data.get_education_distribution()
        
        return DemographicProfile(
            total_population=population_data.total_population,
            age_distribution=age_distribution,
            gender_distribution=gender_distribution,
            nationality_distribution=nationality_distribution,
            education_distribution=education_distribution,
            dependency_ratio=population_data.dependency_ratio,
            median_age=population_data.median_age_estimate
        )
    
    def project_population_growth(self, region_id: int, years: int = 10) -> List[PopulationProjection]:
        """
        Project population growth using demographic and economic factors
        """
        population_data = PopulationData.get_latest_by_region(region_id)
        if not population_data:
            return []
        
        projections = []
        current_population = population_data.total_population
        
        # Calculate base growth rate
        base_growth_rate = self._calculate_growth_rate(population_data)
        
        for year in range(1, years + 1):
            # Apply cohort component method for detailed projections
            projected_data = self._cohort_component_projection(population_data, year, base_growth_rate)
            
            # Calculate confidence intervals
            confidence_interval = self._calculate_confidence_interval(
                projected_data['total_population'], year
            )
            
            projections.append(PopulationProjection(
                year=datetime.now().year + year,
                total_population=projected_data['total_population'],
                age_groups=projected_data['age_groups'],
                confidence_interval=confidence_interval,
                growth_rate=projected_data['growth_rate'],
                assumptions=projected_data['assumptions']
            ))
        
        return projections
    
    def analyze_demographic_transition(self, region_id: int) -> Dict:
        """
        Analyze demographic transition patterns and implications
        """
        population_data = PopulationData.get_latest_by_region(region_id)
        if not population_data:
            return {}
        
        # Calculate demographic indicators
        birth_rate = population_data.birth_rate or 20.0  # per 1000
        death_rate = population_data.death_rate or 4.0   # per 1000
        
        # Analyze age structure
        age_groups = population_data.get_age_group_percentages()
        
        # Determine demographic stage
        demographic_stage = self._determine_demographic_stage(birth_rate, death_rate, age_groups)
        
        # Calculate demographic dividend
        working_age_ratio = age_groups.get('15-64', 60)  # Default 60%
        demographic_dividend = self._calculate_demographic_dividend(working_age_ratio, population_data.dependency_ratio)
        
        # Health implications
        health_implications = self._analyze_health_implications(age_groups, population_data)
        
        return {
            'demographic_stage': demographic_stage,
            'birth_rate': birth_rate,
            'death_rate': death_rate,
            'natural_increase_rate': birth_rate - death_rate,
            'demographic_dividend': demographic_dividend,
            'health_implications': health_implications,
            'workforce_implications': self._analyze_workforce_implications(age_groups),
            'recommendations': self._generate_demographic_recommendations(demographic_stage, age_groups)
        }
    
    def assess_health_needs_by_demographics(self, region_id: int) -> Dict:
        """
        Assess healthcare needs based on demographic composition
        """
        population_data = PopulationData.get_latest_by_region(region_id)
        if not population_data:
            return {}
        
        age_distribution = population_data.get_age_group_percentages()
        health_factors = population_data.calculate_healthcare_demand_factors()
        
        # Calculate age-specific health needs
        pediatric_needs = self._calculate_pediatric_needs(age_distribution, population_data.total_population)
        adult_needs = self._calculate_adult_needs(age_distribution, population_data.total_population)
        geriatric_needs = self._calculate_geriatric_needs(age_distribution, population_data.total_population)
        
        # Maternal health needs
        maternal_needs = self._calculate_maternal_needs(population_data)
        
        # Chronic disease burden
        chronic_disease_needs = self._assess_chronic_disease_burden(region_id, population_data)
        
        return {
            'pediatric_needs': pediatric_needs,
            'adult_needs': adult_needs,
            'geriatric_needs': geriatric_needs,
            'maternal_needs': maternal_needs,
            'chronic_disease_needs': chronic_disease_needs,
            'total_healthcare_demand_index': health_factors.get('healthcare_demand_index', 1.0),
            'priority_areas': self._identify_priority_health_areas(
                pediatric_needs, adult_needs, geriatric_needs, chronic_disease_needs
            )
        }
    
    def track_migration_patterns(self, region_id: int) -> Dict:
        """
        Track internal and external migration patterns
        """
        population_data = PopulationData.get_latest_by_region(region_id)
        if not population_data:
            return {}
        
        # Calculate migration rates
        internal_net_migration = (population_data.internal_migration_in - 
                                population_data.internal_migration_out)
        international_net_migration = (population_data.international_migration_in - 
                                     population_data.international_migration_out)
        
        # Migration impact on workforce
        workforce_impact = self._assess_migration_workforce_impact(
            internal_net_migration, international_net_migration, population_data.total_population
        )
        
        return {
            'internal_migration': {
                'inflow': population_data.internal_migration_in,
                'outflow': population_data.internal_migration_out,
                'net_migration': internal_net_migration,
                'rate_per_1000': round((internal_net_migration / population_data.total_population) * 1000, 2)
            },
            'international_migration': {
                'inflow': population_data.international_migration_in,
                'outflow': population_data.international_migration_out,
                'net_migration': international_net_migration,
                'rate_per_1000': round((international_net_migration / population_data.total_population) * 1000, 2)
            },
            'workforce_impact': workforce_impact,
            'urbanization_trends': self._analyze_urbanization_trends(population_data)
        }
    
    def compare_regional_demographics(self, region_ids: List[int]) -> Dict:
        """
        Compare demographic profiles across multiple regions
        """
        regional_profiles = {}
        
        for region_id in region_ids:
            region = Region.find_by_id(region_id)
            if region:
                profile = self.get_demographic_profile(region_id)
                regional_profiles[region.name_en] = profile
        
        # Calculate comparative metrics
        comparison_metrics = self._calculate_comparative_metrics(regional_profiles)
        
        return {
            'regional_profiles': regional_profiles,
            'comparison_metrics': comparison_metrics,
            'rankings': self._rank_regions_by_indicators(regional_profiles),
            'convergence_analysis': self._analyze_demographic_convergence(regional_profiles)
        }
    
    # Private helper methods
    
    def _calculate_growth_rate(self, population_data: PopulationData) -> float:
        """Calculate population growth rate based on demographic factors"""
        
        if population_data.natural_increase_rate:
            base_rate = population_data.natural_increase_rate / 1000
        else:
            # Estimate from birth and death rates
            birth_rate = population_data.birth_rate or 20.0
            death_rate = population_data.death_rate or 4.0
            base_rate = (birth_rate - death_rate) / 1000
        
        # Adjust for migration
        net_migration_rate = 0
        if population_data.total_population > 0:
            total_migration = (population_data.internal_migration_in + 
                             population_data.international_migration_in -
                             population_data.internal_migration_out -
                             population_data.international_migration_out)
            net_migration_rate = total_migration / population_data.total_population
        
        return base_rate + net_migration_rate
    
    def _cohort_component_projection(self, population_data: PopulationData, years: int, growth_rate: float) -> Dict:
        """Detailed cohort component population projection"""
        
        # Simplified cohort component method
        total_population = population_data.total_population * ((1 + growth_rate) ** years)
        
        # Project age groups (simplified - would be more detailed in production)
        current_age_groups = population_data.get_age_group_percentages()
        projected_age_groups = {}
        
        for age_group, percentage in current_age_groups.items():
            # Apply age-specific projection factors
            projection_factor = self._get_age_projection_factor(age_group, years)
            projected_count = int((percentage / 100) * total_population * projection_factor)
            projected_age_groups[age_group] = projected_count
        
        return {
            'total_population': int(total_population),
            'age_groups': projected_age_groups,
            'growth_rate': growth_rate,
            'assumptions': {
                'base_growth_rate': growth_rate,
                'projection_method': 'cohort_component',
                'years_projected': years
            }
        }
    
    def _get_age_projection_factor(self, age_group: str, years: int) -> float:
        """Get age-specific projection factor"""
        
        # Age-specific factors (would be data-driven in production)
        factors = {
            '0-14': 0.95,    # Declining birth rates
            '15-29': 1.0,    # Stable
            '30-44': 1.05,   # Slight increase
            '45-59': 1.1,    # Increase due to aging
            '60+': 1.3       # Significant increase due to aging
        }
        
        base_factor = factors.get(age_group, 1.0)
        return base_factor + (years * 0.01)  # Small annual adjustment
    
    def _calculate_confidence_interval(self, projected_population: int, years: int) -> Tuple[int, int]:
        """Calculate confidence interval for population projection"""
        
        # Confidence interval widens with projection period
        uncertainty_factor = 0.05 + (years * 0.01)  # 5% base + 1% per year
        
        margin = projected_population * uncertainty_factor
        lower_bound = int(projected_population - margin)
        upper_bound = int(projected_population + margin)
        
        return (lower_bound, upper_bound)
    
    def _determine_demographic_stage(self, birth_rate: float, death_rate: float, age_groups: Dict) -> str:
        """Determine demographic transition stage"""
        
        natural_increase = birth_rate - death_rate
        elderly_percentage = age_groups.get('60+', 10)
        
        if birth_rate > 30 and death_rate > 15:
            return "Stage 1: High Stationary"
        elif birth_rate > 25 and death_rate < 10:
            return "Stage 2: Early Expanding"
        elif birth_rate < 20 and death_rate < 10:
            return "Stage 3: Late Expanding"
        elif birth_rate < 15 and elderly_percentage > 15:
            return "Stage 4: Low Stationary"
        else:
            return "Stage 5: Declining"
    
    def _calculate_demographic_dividend(self, working_age_ratio: float, dependency_ratio: float) -> Dict:
        """Calculate demographic dividend potential"""
        
        # Demographic dividend occurs when working age population is large relative to dependents
        dividend_index = working_age_ratio / (dependency_ratio + 1)
        
        if dividend_index > 1.2:
            phase = "Peak Dividend"
        elif dividend_index > 0.8:
            phase = "Early Dividend"
        else:
            phase = "Pre-Dividend"
        
        return {
            'dividend_index': round(dividend_index, 2),
            'phase': phase,
            'working_age_ratio': working_age_ratio,
            'dependency_ratio': dependency_ratio,
            'economic_potential': "High" if dividend_index > 1.0 else "Moderate"
        }
    
    def _analyze_health_implications(self, age_groups: Dict, population_data: PopulationData) -> Dict:
        """Analyze health implications of demographic structure"""
        
        elderly_percentage = age_groups.get('60+', 10)
        children_percentage = age_groups.get('0-14', 20)
        
        implications = {
            'chronic_disease_burden': "High" if elderly_percentage > 15 else "Moderate",
            'maternal_health_needs': "High" if age_groups.get('15-44', 40) > 35 else "Moderate",
            'pediatric_needs': "High" if children_percentage > 25 else "Moderate",
            'healthcare_infrastructure_pressure': elderly_percentage + (children_percentage * 0.5)
        }
        
        return implications
    
    def _analyze_workforce_implications(self, age_groups: Dict) -> Dict:
        """Analyze workforce implications of demographic structure"""
        
        working_age = age_groups.get('15-64', 60)
        youth = age_groups.get('15-29', 20)
        
        return {
            'workforce_availability': "High" if working_age > 65 else "Moderate",
            'skill_development_potential': "High" if youth > 25 else "Moderate",
            'retirement_wave_approaching': age_groups.get('50-64', 15) > 20,
            'healthcare_workforce_sustainability': working_age / (age_groups.get('60+', 10) + 1)
        }
    
    def _generate_demographic_recommendations(self, stage: str, age_groups: Dict) -> List[str]:
        """Generate policy recommendations based on demographic analysis"""
        
        recommendations = []
        
        if "Stage 4" in stage or "Stage 5" in stage:
            recommendations.extend([
                "Implement policies to support aging population",
                "Invest in geriatric healthcare infrastructure",
                "Consider immigration policies to supplement workforce",
                "Develop age-friendly urban planning"
            ])
        
        if age_groups.get('0-14', 20) < 15:
            recommendations.append("Consider family-friendly policies to support birth rates")
        
        if age_groups.get('60+', 10) > 20:
            recommendations.extend([
                "Strengthen elderly care services",
                "Prepare for increased healthcare demand",
                "Develop long-term care workforce"
            ])
        
        return recommendations
    
    def _calculate_pediatric_needs(self, age_distribution: Dict, total_population: int) -> Dict:
        """Calculate pediatric healthcare needs"""
        
        pediatric_population = int((age_distribution.get('0-14', 20) / 100) * total_population)
        
        return {
            'target_population': pediatric_population,
            'primary_care_visits_annual': pediatric_population * 4,  # 4 visits per child per year
            'vaccination_requirements': pediatric_population * 12,   # Multiple vaccines
            'specialist_referrals': int(pediatric_population * 0.15), # 15% need specialist care
            'emergency_visits': int(pediatric_population * 0.8)      # 80% emergency visits annually
        }
    
    def _calculate_adult_needs(self, age_distribution: Dict, total_population: int) -> Dict:
        """Calculate adult healthcare needs"""
        
        adult_population = int(((age_distribution.get('15-44', 40) + age_distribution.get('45-59', 20)) / 100) * total_population)
        
        return {
            'target_population': adult_population,
            'primary_care_visits_annual': adult_population * 2,      # 2 visits per adult per year
            'preventive_screenings': int(adult_population * 0.6),   # 60% receive screenings
            'chronic_disease_management': int(adult_population * 0.3), # 30% have chronic conditions
            'occupational_health_services': int(adult_population * 0.7) # 70% working population
        }
    
    def _calculate_geriatric_needs(self, age_distribution: Dict, total_population: int) -> Dict:
        """Calculate geriatric healthcare needs"""
        
        elderly_population = int((age_distribution.get('60+', 10) / 100) * total_population)
        
        return {
            'target_population': elderly_population,
            'primary_care_visits_annual': elderly_population * 6,    # 6 visits per elderly per year
            'specialist_care_needs': int(elderly_population * 0.8), # 80% need specialist care
            'long_term_care_needs': int(elderly_population * 0.2),  # 20% need long-term care
            'emergency_services': int(elderly_population * 1.5),    # 1.5 emergency visits per year
            'home_healthcare_needs': int(elderly_population * 0.3)  # 30% need home care
        }
    
    def _calculate_maternal_needs(self, population_data: PopulationData) -> Dict:
        """Calculate maternal healthcare needs"""
        
        # Women of reproductive age (15-49)
        reproductive_age_women = int(population_data.female_count * 0.5)  # Approximate 50%
        births_annual = int(reproductive_age_women * (population_data.birth_rate or 20) / 1000)
        
        return {
            'reproductive_age_women': reproductive_age_women,
            'estimated_births_annual': births_annual,
            'prenatal_care_visits': births_annual * 12,              # 12 visits per pregnancy
            'delivery_services': births_annual,
            'postnatal_care': births_annual * 6,                     # 6 postnatal visits
            'family_planning_services': int(reproductive_age_women * 0.4) # 40% use services
        }
    
    def _assess_chronic_disease_burden(self, region_id: int, population_data: PopulationData) -> Dict:
        """Assess chronic disease burden and healthcare needs"""
        
        # This would typically pull from HealthCondition model
        return {
            'diabetes_burden': population_data.diabetes_prevalence or 10.0,
            'hypertension_burden': population_data.hypertension_prevalence or 25.0,
            'obesity_burden': population_data.obesity_prevalence or 30.0,
            'estimated_patients_needing_care': int(population_data.total_population * 0.4), # 40% with chronic conditions
            'care_intensity': "High",
            'specialist_needs': int(population_data.total_population * 0.15) # 15% need specialist care
        }
    
    def _identify_priority_health_areas(self, pediatric: Dict, adult: Dict, geriatric: Dict, chronic: Dict) -> List[str]:
        """Identify priority healthcare areas based on demographic needs"""
        
        priorities = []
        
        if pediatric['target_population'] > adult['target_population'] * 0.3:
            priorities.append("Pediatric and Maternal Health")
        
        if geriatric['target_population'] > adult['target_population'] * 0.2:
            priorities.append("Geriatric and Long-term Care")
        
        if chronic['estimated_patients_needing_care'] > adult['target_population'] * 0.35:
            priorities.append("Chronic Disease Management")
        
        priorities.append("Primary Care Strengthening")
        priorities.append("Emergency Services")
        
        return priorities
    
    def _assess_migration_workforce_impact(self, internal_migration: int, international_migration: int, total_population: int) -> Dict:
        """Assess migration impact on healthcare workforce"""
        
        net_migration = internal_migration + international_migration
        migration_rate = (net_migration / total_population) * 100 if total_population > 0 else 0
        
        return {
            'net_migration_effect': net_migration,
            'migration_rate_percentage': round(migration_rate, 2),
            'workforce_impact': "Positive" if net_migration > 0 else "Negative",
            'healthcare_demand_change': abs(net_migration * 0.02),  # 2% of migrants need immediate healthcare
            'cultural_competency_needs': "High" if abs(international_migration) > 1000 else "Moderate"
        }
    
    def _analyze_urbanization_trends(self, population_data: PopulationData) -> Dict:
        """Analyze urbanization trends and healthcare implications"""
        
        urban_percentage = (population_data.urban_population / population_data.total_population * 100) if population_data.total_population > 0 else 50
        
        return {
            'urban_percentage': round(urban_percentage, 1),
            'rural_percentage': round(100 - urban_percentage, 1),
            'urbanization_level': "High" if urban_percentage > 80 else "Moderate" if urban_percentage > 60 else "Low",
            'healthcare_access_disparity': "High" if urban_percentage < 70 else "Moderate",
            'infrastructure_needs': "Urban Focus" if urban_percentage > 75 else "Balanced Urban-Rural"
        }
    
    def _calculate_comparative_metrics(self, regional_profiles: Dict) -> Dict:
        """Calculate comparative metrics across regions"""
        
        if not regional_profiles:
            return {}
        
        populations = [profile.total_population for profile in regional_profiles.values()]
        dependency_ratios = [profile.dependency_ratio for profile in regional_profiles.values()]
        median_ages = [profile.median_age for profile in regional_profiles.values()]
        
        return {
            'population_variance': round(np.var(populations), 2),
            'average_dependency_ratio': round(np.mean(dependency_ratios), 2),
            'median_age_range': {
                'min': round(min(median_ages), 1),
                'max': round(max(median_ages), 1),
                'average': round(np.mean(median_ages), 1)
            },
            'demographic_diversity_index': self._calculate_diversity_index(regional_profiles)
        }
    
    def _rank_regions_by_indicators(self, regional_profiles: Dict) -> Dict:
        """Rank regions by key demographic indicators"""
        
        rankings = {}
        
        # Rank by population size
        pop_ranking = sorted(regional_profiles.items(), key=lambda x: x[1].total_population, reverse=True)
        rankings['by_population'] = [region for region, _ in pop_ranking]
        
        # Rank by dependency ratio (lower is better)
        dep_ranking = sorted(regional_profiles.items(), key=lambda x: x[1].dependency_ratio)
        rankings['by_dependency_ratio'] = [region for region, _ in dep_ranking]
        
        # Rank by median age
        age_ranking = sorted(regional_profiles.items(), key=lambda x: x[1].median_age, reverse=True)
        rankings['by_median_age'] = [region for region, _ in age_ranking]
        
        return rankings
    
    def _analyze_demographic_convergence(self, regional_profiles: Dict) -> Dict:
        """Analyze demographic convergence patterns"""
        
        if len(regional_profiles) < 2:
            return {}
        
        dependency_ratios = [profile.dependency_ratio for profile in regional_profiles.values()]
        median_ages = [profile.median_age for profile in regional_profiles.values()]
        
        return {
            'dependency_ratio_convergence': {
                'coefficient_of_variation': round((np.std(dependency_ratios) / np.mean(dependency_ratios)) * 100, 2),
                'convergence_status': "Converging" if np.std(dependency_ratios) < 10 else "Diverging"
            },
            'age_structure_convergence': {
                'age_range': round(max(median_ages) - min(median_ages), 1),
                'convergence_status': "Converging" if (max(median_ages) - min(median_ages)) < 5 else "Diverging"
            }
        }
    
    def _calculate_diversity_index(self, regional_profiles: Dict) -> float:
        """Calculate demographic diversity index across regions"""
        
        # Simplified diversity index based on population distribution
        populations = [profile.total_population for profile in regional_profiles.values()]
        total_pop = sum(populations)
        
        if total_pop == 0:
            return 0
        
        # Calculate Herfindahl index (measure of concentration)
        herfindahl = sum((pop / total_pop) ** 2 for pop in populations)
        diversity_index = 1 - herfindahl
        
        return round(diversity_index, 3)
    
    def _create_empty_profile(self) -> DemographicProfile:
        """Create empty demographic profile when data is unavailable"""
        return DemographicProfile(
            total_population=0,
            age_distribution={},
            gender_distribution={},
            nationality_distribution={},
            education_distribution={},
            dependency_ratio=0,
            median_age=0
        ) 