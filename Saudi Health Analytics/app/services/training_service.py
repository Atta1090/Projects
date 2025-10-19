"""
Training Service
Education capacity tracking, graduate output analysis, and curriculum alignment
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from app import db
from app.models.region import Region
from app.models.healthcare_worker import HealthcareWorkerCategory


@dataclass
class TrainingCapacity:
    """Training capacity information"""
    institution_name: str
    program_type: str
    annual_capacity: int
    current_enrollment: int
    graduation_rate: float
    employment_rate: float
    quality_indicators: Dict


@dataclass
class GraduateProjection:
    """Graduate output projection"""
    year: int
    category: str
    expected_graduates: int
    regional_distribution: Dict[str, int]
    quality_metrics: Dict
    employment_prospects: Dict


@dataclass
class SkillGapAnalysis:
    """Skills gap analysis result"""
    category: str
    current_skills: List[str]
    required_skills: List[str]
    skill_gaps: List[str]
    training_recommendations: List[str]
    priority_level: str


class TrainingService:
    """
    Service for managing healthcare education and training programs
    Supports workforce planning through education capacity analysis
    """
    
    def __init__(self):
        # Saudi healthcare education institutions (simplified data)
        self.training_institutions = self._initialize_training_data()
        
    def get_training_capacity_overview(self, region_id: Optional[int] = None) -> Dict:
        """
        Get comprehensive overview of training capacity
        """
        if region_id:
            region = Region.find_by_id(region_id)
            region_name = region.name_en if region else "Unknown"
            capacity_data = self._get_regional_capacity(region_id)
        else:
            region_name = "National"
            capacity_data = self._get_national_capacity()
        
        return {
            'region': region_name,
            'total_institutions': capacity_data['total_institutions'],
            'total_annual_capacity': capacity_data['total_capacity'],
            'programs_by_category': capacity_data['programs_by_category'],
            'capacity_utilization': capacity_data['utilization'],
            'quality_metrics': capacity_data['quality'],
            'expansion_potential': capacity_data['expansion_potential']
        }
    
    def project_graduate_output(self, years: int = 5) -> List[GraduateProjection]:
        """
        Project graduate output for healthcare categories
        """
        projections = []
        current_year = datetime.now().year
        
        # Get healthcare categories
        categories = HealthcareWorkerCategory.get_main_categories()
        
        for category in categories:
            for year in range(1, years + 1):
                projection_year = current_year + year
                
                # Calculate expected graduates
                base_graduates = self._calculate_base_graduates(category.code)
                growth_factor = self._calculate_growth_factor(category.code, year)
                expected_graduates = int(base_graduates * growth_factor)
                
                # Regional distribution
                regional_dist = self._project_regional_distribution(category.code, expected_graduates)
                
                # Quality and employment metrics
                quality_metrics = self._calculate_quality_metrics(category.code)
                employment_prospects = self._assess_employment_prospects(category.code, year)
                
                projections.append(GraduateProjection(
                    year=projection_year,
                    category=category.name_en,
                    expected_graduates=expected_graduates,
                    regional_distribution=regional_dist,
                    quality_metrics=quality_metrics,
                    employment_prospects=employment_prospects
                ))
        
        return projections
    
    def analyze_curriculum_alignment(self, category_id: int) -> Dict:
        """
        Analyze curriculum alignment with workforce needs
        """
        category = HealthcareWorkerCategory.find_by_id(category_id)
        if not category:
            return {'error': 'Category not found'}
        
        # Current curriculum analysis
        current_curriculum = self._get_current_curriculum(category.code)
        
        # Required competencies for workforce
        required_competencies = self._get_required_competencies(category.code)
        
        # Gap analysis
        curriculum_gaps = self._identify_curriculum_gaps(current_curriculum, required_competencies)
        
        # Recommendations
        alignment_recommendations = self._generate_curriculum_recommendations(curriculum_gaps)
        
        return {
            'category': category.name_en,
            'current_curriculum': current_curriculum,
            'required_competencies': required_competencies,
            'alignment_score': self._calculate_alignment_score(current_curriculum, required_competencies),
            'curriculum_gaps': curriculum_gaps,
            'recommendations': alignment_recommendations,
            'implementation_timeline': self._estimate_implementation_timeline(curriculum_gaps)
        }
    
    def assess_skills_gaps(self, region_id: int) -> List[SkillGapAnalysis]:
        """
        Assess skills gaps in the healthcare workforce
        """
        skill_gaps = []
        
        # Get healthcare categories
        categories = HealthcareWorkerCategory.get_main_categories()
        
        for category in categories:
            # Current skills in workforce
            current_skills = self._assess_current_skills(region_id, category.id)
            
            # Required skills for future needs
            required_skills = self._identify_required_skills(category.code)
            
            # Identify gaps
            gaps = self._identify_skill_gaps(current_skills, required_skills)
            
            if gaps:
                priority = self._assess_gap_priority(category.code, gaps)
                recommendations = self._generate_training_recommendations(category.code, gaps)
                
                skill_gaps.append(SkillGapAnalysis(
                    category=category.name_en,
                    current_skills=current_skills,
                    required_skills=required_skills,
                    skill_gaps=gaps,
                    training_recommendations=recommendations,
                    priority_level=priority
                ))
        
        return skill_gaps
    
    def evaluate_training_quality(self) -> Dict:
        """
        Evaluate training program quality across institutions
        """
        quality_assessment = {
            'overall_quality_score': 0,
            'institution_rankings': [],
            'quality_indicators': {},
            'improvement_areas': [],
            'best_practices': []
        }
        
        # Assess each institution
        institution_scores = []
        for institution in self.training_institutions:
            score = self._calculate_institution_quality_score(institution)
            institution_scores.append({
                'name': institution['name'],
                'score': score,
                'strengths': institution.get('strengths', []),
                'weaknesses': institution.get('weaknesses', [])
            })
        
        # Overall metrics
        quality_assessment['overall_quality_score'] = sum(s['score'] for s in institution_scores) / len(institution_scores)
        quality_assessment['institution_rankings'] = sorted(institution_scores, key=lambda x: x['score'], reverse=True)
        
        # Quality indicators
        quality_assessment['quality_indicators'] = self._calculate_quality_indicators()
        
        # Improvement recommendations
        quality_assessment['improvement_areas'] = self._identify_improvement_areas(institution_scores)
        quality_assessment['best_practices'] = self._identify_best_practices(institution_scores)
        
        return quality_assessment
    
    def plan_capacity_expansion(self, target_year: int = 2030) -> Dict:
        """
        Plan capacity expansion to meet future workforce needs
        """
        current_year = datetime.now().year
        years_to_target = target_year - current_year
        
        # Get workforce projections
        workforce_needs = self._get_future_workforce_needs(target_year)
        
        # Current capacity
        current_capacity = self._get_national_capacity()
        
        # Calculate required expansion
        expansion_plan = {}
        
        for category_code, future_need in workforce_needs.items():
            current_output = self._calculate_base_graduates(category_code)
            required_output = future_need / 4  # Assuming 4-year average career preparation
            
            if required_output > current_output:
                expansion_needed = required_output - current_output
                expansion_plan[category_code] = {
                    'current_annual_output': current_output,
                    'required_annual_output': int(required_output),
                    'expansion_needed': int(expansion_needed),
                    'expansion_percentage': round((expansion_needed / current_output) * 100, 1),
                    'investment_required': self._calculate_expansion_cost(category_code, expansion_needed),
                    'timeline': self._estimate_expansion_timeline(expansion_needed),
                    'recommended_strategies': self._recommend_expansion_strategies(category_code, expansion_needed)
                }
        
        # Overall expansion summary
        total_investment = sum(plan['investment_required'] for plan in expansion_plan.values())
        
        return {
            'target_year': target_year,
            'planning_horizon': years_to_target,
            'expansion_by_category': expansion_plan,
            'total_investment_required': total_investment,
            'implementation_phases': self._create_implementation_phases(expansion_plan),
            'success_factors': self._identify_success_factors(),
            'risk_assessment': self._assess_expansion_risks()
        }
    
    def track_graduate_employment(self) -> Dict:
        """
        Track employment outcomes of healthcare graduates
        """
        employment_data = {
            'overall_employment_rate': 0,
            'employment_by_category': {},
            'geographic_distribution': {},
            'employer_satisfaction': {},
            'career_progression': {},
            'retention_rates': {}
        }
        
        categories = HealthcareWorkerCategory.get_main_categories()
        
        for category in categories:
            category_employment = self._track_category_employment(category.code)
            employment_data['employment_by_category'][category.name_en] = category_employment
        
        # Calculate overall employment rate
        total_graduates = sum(data['graduates'] for data in employment_data['employment_by_category'].values())
        total_employed = sum(data['employed'] for data in employment_data['employment_by_category'].values())
        
        employment_data['overall_employment_rate'] = round((total_employed / total_graduates) * 100, 1) if total_graduates > 0 else 0
        
        # Geographic distribution
        employment_data['geographic_distribution'] = self._analyze_graduate_geographic_distribution()
        
        # Employer satisfaction
        employment_data['employer_satisfaction'] = self._assess_employer_satisfaction()
        
        # Career progression tracking
        employment_data['career_progression'] = self._track_career_progression()
        
        # Retention rates
        employment_data['retention_rates'] = self._calculate_retention_rates()
        
        return employment_data
    
    # Private helper methods
    
    def _initialize_training_data(self) -> List[Dict]:
        """Initialize training institution data"""
        return [
            {
                'name': 'King Saud University - College of Medicine',
                'location': 'Riyadh',
                'programs': ['Medicine', 'Nursing', 'Pharmacy'],
                'annual_capacity': {'Medicine': 200, 'Nursing': 150, 'Pharmacy': 80},
                'quality_score': 9.2,
                'strengths': ['Research Excellence', 'Modern Facilities', 'International Accreditation'],
                'weaknesses': ['Limited Clinical Rotations']
            },
            {
                'name': 'King Abdulaziz University - Faculty of Medicine',
                'location': 'Jeddah',
                'programs': ['Medicine', 'Nursing', 'Pharmacy', 'Medical Technology'],
                'annual_capacity': {'Medicine': 180, 'Nursing': 120, 'Pharmacy': 70, 'Medical Technology': 60},
                'quality_score': 8.8,
                'strengths': ['Clinical Training', 'Industry Partnerships'],
                'weaknesses': ['Faculty Shortage']
            },
            {
                'name': 'King Faisal University - College of Medicine',
                'location': 'Dammam',
                'programs': ['Medicine', 'Nursing', 'Pharmacy'],
                'annual_capacity': {'Medicine': 150, 'Nursing': 100, 'Pharmacy': 60},
                'quality_score': 8.5,
                'strengths': ['Regional Focus', 'Community Engagement'],
                'weaknesses': ['Resource Constraints']
            },
            {
                'name': 'Princess Nourah University - Health Sciences',
                'location': 'Riyadh',
                'programs': ['Nursing', 'Pharmacy', 'Medical Technology'],
                'annual_capacity': {'Nursing': 200, 'Pharmacy': 90, 'Medical Technology': 80},
                'quality_score': 8.7,
                'strengths': ['Women-focused Programs', 'Innovation'],
                'weaknesses': ['Limited Research Funding']
            }
        ]
    
    def _get_regional_capacity(self, region_id: int) -> Dict:
        """Get training capacity for a specific region"""
        region = Region.find_by_id(region_id)
        if not region:
            return {}
        
        # Filter institutions by region (simplified)
        regional_institutions = [
            inst for inst in self.training_institutions 
            if self._institution_in_region(inst, region.name_en)
        ]
        
        total_capacity = 0
        programs_by_category = {}
        
        for institution in regional_institutions:
            for program, capacity in institution['annual_capacity'].items():
                total_capacity += capacity
                if program not in programs_by_category:
                    programs_by_category[program] = 0
                programs_by_category[program] += capacity
        
        return {
            'total_institutions': len(regional_institutions),
            'total_capacity': total_capacity,
            'programs_by_category': programs_by_category,
            'utilization': 85.0,  # Simplified
            'quality': 8.5,       # Average quality score
            'expansion_potential': 'Medium'
        }
    
    def _get_national_capacity(self) -> Dict:
        """Get national training capacity"""
        total_capacity = 0
        programs_by_category = {}
        
        for institution in self.training_institutions:
            for program, capacity in institution['annual_capacity'].items():
                total_capacity += capacity
                if program not in programs_by_category:
                    programs_by_category[program] = 0
                programs_by_category[program] += capacity
        
        return {
            'total_institutions': len(self.training_institutions),
            'total_capacity': total_capacity,
            'programs_by_category': programs_by_category,
            'utilization': 87.0,
            'quality': sum(inst['quality_score'] for inst in self.training_institutions) / len(self.training_institutions),
            'expansion_potential': 'High'
        }
    
    def _calculate_base_graduates(self, category_code: str) -> int:
        """Calculate base number of graduates for a category"""
        category_mapping = {
            'DOC': 'Medicine',
            'NUR': 'Nursing',
            'PHAR': 'Pharmacy',
            'TECH': 'Medical Technology'
        }
        
        program_name = category_mapping.get(category_code, 'Medicine')
        total_graduates = 0
        
        for institution in self.training_institutions:
            if program_name in institution['annual_capacity']:
                total_graduates += institution['annual_capacity'][program_name]
        
        # Apply graduation rate (typically 85-90%)
        return int(total_graduates * 0.87)
    
    def _calculate_growth_factor(self, category_code: str, year: int) -> float:
        """Calculate growth factor for graduate projections"""
        # Base growth rates by category
        growth_rates = {
            'DOC': 0.03,    # 3% annual growth
            'NUR': 0.05,    # 5% annual growth
            'PHAR': 0.04,   # 4% annual growth
            'TECH': 0.06    # 6% annual growth
        }
        
        annual_growth = growth_rates.get(category_code, 0.03)
        return (1 + annual_growth) ** year
    
    def _project_regional_distribution(self, category_code: str, total_graduates: int) -> Dict[str, int]:
        """Project regional distribution of graduates"""
        # Regional distribution patterns (simplified)
        distribution_patterns = {
            'Riyadh': 0.35,
            'Makkah': 0.25,
            'Eastern Province': 0.20,
            'Other Regions': 0.20
        }
        
        regional_distribution = {}
        for region, percentage in distribution_patterns.items():
            regional_distribution[region] = int(total_graduates * percentage)
        
        return regional_distribution
    
    def _calculate_quality_metrics(self, category_code: str) -> Dict:
        """Calculate quality metrics for graduates"""
        return {
            'licensing_exam_pass_rate': 92.0,
            'employer_satisfaction_score': 8.3,
            'competency_assessment_score': 8.5,
            'international_recognition': True
        }
    
    def _assess_employment_prospects(self, category_code: str, projection_year: int) -> Dict:
        """Assess employment prospects for graduates"""
        # Employment demand projections
        demand_projections = {
            'DOC': 0.95,    # 95% employment rate
            'NUR': 0.98,    # 98% employment rate
            'PHAR': 0.90,   # 90% employment rate
            'TECH': 0.92    # 92% employment rate
        }
        
        base_employment_rate = demand_projections.get(category_code, 0.90)
        
        # Adjust for future market conditions
        market_adjustment = max(0.80, base_employment_rate - (projection_year * 0.01))
        
        return {
            'employment_rate': round(market_adjustment * 100, 1),
            'average_salary': self._estimate_graduate_salary(category_code),
            'job_market_outlook': 'Favorable' if market_adjustment > 0.90 else 'Moderate',
            'skills_demand': 'High'
        }
    
    def _get_current_curriculum(self, category_code: str) -> Dict:
        """Get current curriculum structure"""
        curricula = {
            'DOC': {
                'core_subjects': ['Anatomy', 'Physiology', 'Pathology', 'Pharmacology', 'Clinical Medicine'],
                'clinical_hours': 2000,
                'research_component': True,
                'internship_duration': 12,  # months
                'specialization_tracks': ['Internal Medicine', 'Surgery', 'Pediatrics', 'Family Medicine']
            },
            'NUR': {
                'core_subjects': ['Nursing Fundamentals', 'Medical-Surgical Nursing', 'Pediatric Nursing', 'Community Health'],
                'clinical_hours': 1200,
                'research_component': True,
                'internship_duration': 6,   # months
                'specialization_tracks': ['Critical Care', 'Pediatric', 'Community Health', 'Mental Health']
            },
            'PHAR': {
                'core_subjects': ['Pharmaceutical Chemistry', 'Pharmacology', 'Clinical Pharmacy', 'Drug Development'],
                'clinical_hours': 800,
                'research_component': True,
                'internship_duration': 6,   # months
                'specialization_tracks': ['Clinical Pharmacy', 'Industrial Pharmacy', 'Hospital Pharmacy']
            }
        }
        
        return curricula.get(category_code, {})
    
    def _get_required_competencies(self, category_code: str) -> Dict:
        """Get required competencies for workforce"""
        competencies = {
            'DOC': {
                'clinical_skills': ['Diagnosis', 'Treatment Planning', 'Patient Communication', 'Emergency Care'],
                'technology_skills': ['Electronic Health Records', 'Telemedicine', 'Medical Imaging'],
                'soft_skills': ['Leadership', 'Teamwork', 'Cultural Competency', 'Ethics'],
                'emerging_areas': ['Precision Medicine', 'AI in Healthcare', 'Digital Health']
            },
            'NUR': {
                'clinical_skills': ['Patient Assessment', 'Care Planning', 'Medication Administration', 'Patient Education'],
                'technology_skills': ['Electronic Documentation', 'Medical Devices', 'Health Informatics'],
                'soft_skills': ['Communication', 'Empathy', 'Critical Thinking', 'Stress Management'],
                'emerging_areas': ['Telehealth', 'Chronic Disease Management', 'Population Health']
            }
        }
        
        return competencies.get(category_code, {})
    
    def _identify_curriculum_gaps(self, current: Dict, required: Dict) -> List[str]:
        """Identify gaps between current curriculum and required competencies"""
        gaps = []
        
        if not current or not required:
            return gaps
        
        # Check for missing technology skills
        current_tech = set(current.get('technology_skills', []))
        required_tech = set(required.get('technology_skills', []))
        tech_gaps = required_tech - current_tech
        
        if tech_gaps:
            gaps.extend([f"Technology: {skill}" for skill in tech_gaps])
        
        # Check for emerging areas
        current_emerging = set(current.get('emerging_areas', []))
        required_emerging = set(required.get('emerging_areas', []))
        emerging_gaps = required_emerging - current_emerging
        
        if emerging_gaps:
            gaps.extend([f"Emerging: {area}" for area in emerging_gaps])
        
        # Check clinical hours adequacy
        required_hours = {'DOC': 2500, 'NUR': 1500, 'PHAR': 1000}
        category_code = 'DOC'  # Would determine from context
        if current.get('clinical_hours', 0) < required_hours.get(category_code, 1000):
            gaps.append("Insufficient clinical hours")
        
        return gaps
    
    def _generate_curriculum_recommendations(self, gaps: List[str]) -> List[str]:
        """Generate recommendations to address curriculum gaps"""
        recommendations = []
        
        for gap in gaps:
            if 'Technology' in gap:
                recommendations.append(f"Integrate {gap.split(': ')[1]} training into curriculum")
            elif 'Emerging' in gap:
                recommendations.append(f"Develop {gap.split(': ')[1]} specialization track")
            elif 'clinical hours' in gap:
                recommendations.append("Increase clinical rotation duration and variety")
        
        # General recommendations
        recommendations.extend([
            "Enhance industry partnerships for practical training",
            "Update curriculum every 2-3 years based on market needs",
            "Implement competency-based assessment methods",
            "Strengthen simulation-based learning opportunities"
        ])
        
        return recommendations
    
    def _calculate_alignment_score(self, current: Dict, required: Dict) -> float:
        """Calculate curriculum alignment score"""
        if not current or not required:
            return 0.0
        
        # Compare core competencies
        current_skills = set()
        required_skills = set()
        
        for category in ['clinical_skills', 'technology_skills', 'soft_skills']:
            current_skills.update(current.get(category, []))
            required_skills.update(required.get(category, []))
        
        if not required_skills:
            return 100.0
        
        overlap = len(current_skills.intersection(required_skills))
        alignment_score = (overlap / len(required_skills)) * 100
        
        return round(alignment_score, 1)
    
    def _estimate_implementation_timeline(self, gaps: List[str]) -> Dict:
        """Estimate timeline for implementing curriculum changes"""
        
        minor_changes = [gap for gap in gaps if any(term in gap.lower() for term in ['technology', 'update', 'enhance'])]
        major_changes = [gap for gap in gaps if any(term in gap.lower() for term in ['emerging', 'clinical hours', 'specialization'])]
        
        return {
            'minor_changes': {
                'items': minor_changes,
                'timeline': '6-12 months',
                'complexity': 'Low'
            },
            'major_changes': {
                'items': major_changes,
                'timeline': '18-24 months',
                'complexity': 'High'
            },
            'total_implementation_time': '24-36 months'
        }
    
    def _assess_current_skills(self, region_id: int, category_id: int) -> List[str]:
        """Assess current skills in the workforce"""
        # This would typically involve surveys or assessments
        # Returning simplified data
        skill_sets = {
            1: ['Clinical Assessment', 'Basic Technology', 'Communication'],  # Doctors
            2: ['Patient Care', 'Documentation', 'Teamwork'],                # Nurses
            3: ['Drug Dispensing', 'Patient Counseling', 'Inventory']        # Pharmacists
        }
        
        return skill_sets.get(category_id, ['Basic Skills'])
    
    def _identify_required_skills(self, category_code: str) -> List[str]:
        """Identify skills required for future healthcare delivery"""
        required_skills = {
            'DOC': ['AI-Assisted Diagnosis', 'Telemedicine', 'Precision Medicine', 'Population Health'],
            'NUR': ['Digital Health', 'Chronic Care Management', 'Health Coaching', 'Data Analytics'],
            'PHAR': ['Pharmacogenomics', 'Clinical Decision Support', 'Medication Therapy Management']
        }
        
        return required_skills.get(category_code, ['Advanced Skills'])
    
    def _identify_skill_gaps(self, current: List[str], required: List[str]) -> List[str]:
        """Identify skill gaps"""
        current_set = set(current)
        required_set = set(required)
        return list(required_set - current_set)
    
    def _assess_gap_priority(self, category_code: str, gaps: List[str]) -> str:
        """Assess priority level of skill gaps"""
        critical_skills = {
            'DOC': ['AI-Assisted Diagnosis', 'Telemedicine'],
            'NUR': ['Digital Health', 'Chronic Care Management'],
            'PHAR': ['Pharmacogenomics']
        }
        
        critical_gaps = set(gaps).intersection(set(critical_skills.get(category_code, [])))
        
        if critical_gaps:
            return 'High'
        elif len(gaps) > 3:
            return 'Medium'
        else:
            return 'Low'
    
    def _generate_training_recommendations(self, category_code: str, gaps: List[str]) -> List[str]:
        """Generate training recommendations for skill gaps"""
        recommendations = []
        
        for gap in gaps:
            if 'AI' in gap or 'Digital' in gap:
                recommendations.append(f"Implement {gap} certification program")
            elif 'Management' in gap:
                recommendations.append(f"Develop {gap} leadership track")
            else:
                recommendations.append(f"Create specialized training for {gap}")
        
        # General recommendations
        recommendations.extend([
            "Partner with technology companies for hands-on training",
            "Establish continuing education requirements",
            "Create mentorship programs for skill development"
        ])
        
        return recommendations
    
    def _calculate_institution_quality_score(self, institution: Dict) -> float:
        """Calculate quality score for an institution"""
        return institution.get('quality_score', 7.0)
    
    def _calculate_quality_indicators(self) -> Dict:
        """Calculate overall quality indicators"""
        return {
            'average_graduation_rate': 87.5,
            'licensing_exam_pass_rate': 92.3,
            'employer_satisfaction': 8.2,
            'accreditation_compliance': 94.0
        }
    
    def _identify_improvement_areas(self, institution_scores: List[Dict]) -> List[str]:
        """Identify areas for improvement"""
        return [
            "Faculty development and training",
            "Infrastructure modernization",
            "Clinical training partnerships",
            "Research capacity building",
            "Student support services"
        ]
    
    def _identify_best_practices(self, institution_scores: List[Dict]) -> List[str]:
        """Identify best practices from top institutions"""
        return [
            "Integration of simulation-based learning",
            "Strong industry partnerships",
            "Continuous curriculum updates",
            "Faculty exchange programs",
            "Quality assurance systems"
        ]
    
    def _get_future_workforce_needs(self, target_year: int) -> Dict[str, int]:
        """Get projected workforce needs by category"""
        # Simplified projections
        return {
            'DOC': 5000,
            'NUR': 8000,
            'PHAR': 2000,
            'TECH': 3000
        }
    
    def _calculate_expansion_cost(self, category_code: str, additional_capacity: int) -> float:
        """Calculate cost of capacity expansion"""
        # Cost per additional student capacity per year
        costs_per_student = {
            'DOC': 50000,   # SAR
            'NUR': 30000,   # SAR
            'PHAR': 40000,  # SAR
            'TECH': 25000   # SAR
        }
        
        unit_cost = costs_per_student.get(category_code, 35000)
        return additional_capacity * unit_cost
    
    def _estimate_expansion_timeline(self, additional_capacity: int) -> str:
        """Estimate timeline for capacity expansion"""
        if additional_capacity < 100:
            return "2-3 years"
        elif additional_capacity < 300:
            return "3-5 years"
        else:
            return "5-7 years"
    
    def _recommend_expansion_strategies(self, category_code: str, expansion_needed: int) -> List[str]:
        """Recommend strategies for capacity expansion"""
        strategies = [
            "Establish new campuses in underserved regions",
            "Expand existing program capacity",
            "Develop online and hybrid learning programs",
            "Create public-private partnerships",
            "Attract international faculty and students"
        ]
        
        if expansion_needed > 200:
            strategies.append("Build new specialized training centers")
        
        return strategies
    
    def _create_implementation_phases(self, expansion_plan: Dict) -> List[Dict]:
        """Create implementation phases for expansion"""
        return [
            {
                'phase': 'Phase 1 (Years 1-2)',
                'focus': 'Infrastructure and Faculty Development',
                'activities': ['Facility construction', 'Faculty recruitment', 'Curriculum development']
            },
            {
                'phase': 'Phase 2 (Years 3-4)',
                'focus': 'Program Launch and Quality Assurance',
                'activities': ['Student enrollment', 'Clinical partnerships', 'Quality monitoring']
            },
            {
                'phase': 'Phase 3 (Years 5+)',
                'focus': 'Full Operation and Continuous Improvement',
                'activities': ['Capacity optimization', 'Performance evaluation', 'Expansion refinement']
            }
        ]
    
    def _identify_success_factors(self) -> List[str]:
        """Identify success factors for expansion"""
        return [
            "Strong government support and funding",
            "Industry collaboration and partnerships",
            "Quality faculty recruitment and retention",
            "Modern infrastructure and technology",
            "Effective regulatory framework",
            "Student financial support programs"
        ]
    
    def _assess_expansion_risks(self) -> Dict:
        """Assess risks associated with expansion"""
        return {
            'high_risk': ['Faculty shortage', 'Funding constraints'],
            'medium_risk': ['Market saturation', 'Quality control'],
            'low_risk': ['Student demand', 'Infrastructure development'],
            'mitigation_strategies': [
                "Develop faculty pipeline programs",
                "Secure multi-year funding commitments",
                "Implement robust quality assurance systems",
                "Conduct regular market analysis"
            ]
        }
    
    def _track_category_employment(self, category_code: str) -> Dict:
        """Track employment data for a specific category"""
        # Simplified employment tracking data
        employment_data = {
            'DOC': {'graduates': 800, 'employed': 760, 'employment_rate': 95.0},
            'NUR': {'graduates': 1200, 'employed': 1176, 'employment_rate': 98.0},
            'PHAR': {'graduates': 400, 'employed': 360, 'employment_rate': 90.0},
            'TECH': {'graduates': 600, 'employed': 552, 'employment_rate': 92.0}
        }
        
        return employment_data.get(category_code, {'graduates': 0, 'employed': 0, 'employment_rate': 0})
    
    def _analyze_graduate_geographic_distribution(self) -> Dict:
        """Analyze geographic distribution of employed graduates"""
        return {
            'Riyadh': 35,
            'Makkah': 25,
            'Eastern Province': 20,
            'Other Regions': 20
        }
    
    def _assess_employer_satisfaction(self) -> Dict:
        """Assess employer satisfaction with graduates"""
        return {
            'overall_satisfaction': 8.3,
            'technical_skills': 8.5,
            'soft_skills': 8.0,
            'work_readiness': 8.2,
            'areas_for_improvement': ['Technology skills', 'Leadership capabilities']
        }
    
    def _track_career_progression(self) -> Dict:
        """Track career progression of graduates"""
        return {
            'promotion_rate_year_2': 25,
            'promotion_rate_year_5': 60,
            'leadership_positions': 15,
            'specialization_completion': 40
        }
    
    def _calculate_retention_rates(self) -> Dict:
        """Calculate retention rates in the healthcare sector"""
        return {
            'year_1_retention': 92,
            'year_3_retention': 85,
            'year_5_retention': 78,
            'sector_retention': 82
        }
    
    def _institution_in_region(self, institution: Dict, region_name: str) -> bool:
        """Check if institution is in a specific region"""
        # Simplified mapping
        location_mapping = {
            'Riyadh': ['Riyadh'],
            'Makkah': ['Jeddah', 'Makkah'],
            'Eastern Province': ['Dammam', 'Dhahran', 'Khobar']
        }
        
        institution_location = institution.get('location', '')
        return institution_location in location_mapping.get(region_name, [])
    
    def _estimate_graduate_salary(self, category_code: str) -> int:
        """Estimate starting salary for graduates"""
        salaries = {
            'DOC': 180000,   # SAR per year
            'NUR': 120000,   # SAR per year
            'PHAR': 140000,  # SAR per year
            'TECH': 100000   # SAR per year
        }
        
        return salaries.get(category_code, 120000) 