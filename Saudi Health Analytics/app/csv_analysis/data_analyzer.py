"""
Data Analyzer for CSV Files
Performs simple analysis without complex AI
Easy to understand and implement
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json


class DataAnalyzer:
    """Simple data analysis for healthcare workforce planning"""
    
    def __init__(self):
        self.analysis_results = {}
    
    def analyze_workforce_data(self, df):
        """Analyze workforce CSV data and provide insights"""
        analysis = {
            'analysis_type': 'workforce',
            'analysis_date': datetime.now().isoformat(),
            'summary': {},
            'insights': [],
            'recommendations': [],
            'regional_analysis': {},
            'category_analysis': {}
        }
        
        try:
            # Basic Summary
            analysis['summary'] = {
                'total_records': len(df),
                'total_workers': int(df['current_count'].sum()) if 'current_count' in df.columns else 0,
                'total_authorized': int(df['authorized_positions'].sum()) if 'authorized_positions' in df.columns else 0,
                'total_filled': int(df['filled_positions'].sum()) if 'filled_positions' in df.columns else 0,
                'regions_covered': df['region_name'].nunique() if 'region_name' in df.columns else 0,
                'categories_covered': df['worker_category'].nunique() if 'worker_category' in df.columns else 0
            }
            
            # Calculate vacancy rate
            if analysis['summary']['total_authorized'] > 0:
                vacancy_rate = ((analysis['summary']['total_authorized'] - analysis['summary']['total_filled']) 
                              / analysis['summary']['total_authorized']) * 100
                analysis['summary']['vacancy_rate'] = round(vacancy_rate, 2)
            
            # Regional Analysis
            if 'region_name' in df.columns:
                regional_data = df.groupby('region_name').agg({
                    'current_count': 'sum',
                    'authorized_positions': 'sum', 
                    'filled_positions': 'sum'
                }).round(0)
                
                # Calculate gaps for each region
                regional_data['gap'] = regional_data['authorized_positions'] - regional_data['filled_positions']
                regional_data['vacancy_rate'] = ((regional_data['authorized_positions'] - regional_data['filled_positions']) 
                                                / regional_data['authorized_positions'] * 100).round(2)
                
                analysis['regional_analysis'] = regional_data.to_dict('index')
            
            # Category Analysis
            if 'worker_category' in df.columns:
                category_data = df.groupby('worker_category').agg({
                    'current_count': 'sum',
                    'authorized_positions': 'sum',
                    'filled_positions': 'sum'
                }).round(0)
                
                category_data['gap'] = category_data['authorized_positions'] - category_data['filled_positions']
                category_data['vacancy_rate'] = ((category_data['authorized_positions'] - category_data['filled_positions']) 
                                                / category_data['authorized_positions'] * 100).round(2)
                
                analysis['category_analysis'] = category_data.to_dict('index')
            
            # Generate Insights
            analysis['insights'] = self.generate_workforce_insights(df, analysis)
            
            # Generate Recommendations
            analysis['recommendations'] = self.generate_workforce_recommendations(df, analysis)
            
        except Exception as e:
            analysis['error'] = f"Analysis failed: {str(e)}"
        
        return analysis
    
    def analyze_population_data(self, df):
        """Analyze population CSV data"""
        analysis = {
            'analysis_type': 'population',
            'analysis_date': datetime.now().isoformat(),
            'summary': {},
            'insights': [],
            'recommendations': [],
            'age_distribution': {},
            'regional_breakdown': {}
        }
        
        try:
            # Basic Summary
            analysis['summary'] = {
                'total_records': len(df),
                'total_population': int(df['total_population'].sum()) if 'total_population' in df.columns else 0,
                'regions_covered': df['region_name'].nunique() if 'region_name' in df.columns else 0
            }
            
            # Age Distribution Analysis
            if all(col in df.columns for col in ['age_0_14', 'age_15_64', 'age_65_plus']):
                total_pop = analysis['summary']['total_population']
                if total_pop > 0:
                    analysis['age_distribution'] = {
                        'children_0_14': {
                            'count': int(df['age_0_14'].sum()),
                            'percentage': round((df['age_0_14'].sum() / total_pop) * 100, 2)
                        },
                        'working_age_15_64': {
                            'count': int(df['age_15_64'].sum()),
                            'percentage': round((df['age_15_64'].sum() / total_pop) * 100, 2)
                        },
                        'elderly_65_plus': {
                            'count': int(df['age_65_plus'].sum()),
                            'percentage': round((df['age_65_plus'].sum() / total_pop) * 100, 2)
                        }
                    }
            
            # Regional Breakdown
            if 'region_name' in df.columns:
                regional_data = df.groupby('region_name').agg({
                    'total_population': 'sum'
                }).round(0)
                
                # Calculate percentages
                total_pop = regional_data['total_population'].sum()
                if total_pop > 0:
                    regional_data['percentage'] = (regional_data['total_population'] / total_pop * 100).round(2)
                
                analysis['regional_breakdown'] = regional_data.to_dict('index')
            
            # Generate Insights
            analysis['insights'] = self.generate_population_insights(df, analysis)
            
            # Generate Recommendations
            analysis['recommendations'] = self.generate_population_recommendations(df, analysis)
            
        except Exception as e:
            analysis['error'] = f"Analysis failed: {str(e)}"
        
        return analysis
    
    def analyze_health_conditions_data(self, df):
        """Analyze health conditions CSV data"""
        analysis = {
            'analysis_type': 'health_conditions',
            'analysis_date': datetime.now().isoformat(),
            'summary': {},
            'insights': [],
            'recommendations': [],
            'condition_ranking': {},
            'regional_health_profile': {}
        }
        
        try:
            # Basic Summary
            analysis['summary'] = {
                'total_records': len(df),
                'total_cases': int(df['total_cases'].sum()) if 'total_cases' in df.columns else 0,
                'conditions_tracked': df['condition_name'].nunique() if 'condition_name' in df.columns else 0,
                'regions_covered': df['region_name'].nunique() if 'region_name' in df.columns else 0
            }
            
            # Condition Ranking (by total cases)
            if 'condition_name' in df.columns and 'total_cases' in df.columns:
                condition_data = df.groupby('condition_name').agg({
                    'total_cases': 'sum',
                    'prevalence_rate': 'mean'
                }).round(2)
                
                condition_data = condition_data.sort_values('total_cases', ascending=False)
                analysis['condition_ranking'] = condition_data.to_dict('index')
            
            # Regional Health Profile
            if 'region_name' in df.columns:
                regional_health = df.groupby('region_name').agg({
                    'total_cases': 'sum',
                    'prevalence_rate': 'mean'
                }).round(2)
                
                analysis['regional_health_profile'] = regional_health.to_dict('index')
            
            # Generate Insights
            analysis['insights'] = self.generate_health_insights(df, analysis)
            
            # Generate Recommendations
            analysis['recommendations'] = self.generate_health_recommendations(df, analysis)
            
        except Exception as e:
            analysis['error'] = f"Analysis failed: {str(e)}"
        
        return analysis
    
    def analyze_training_data(self, df):
        """Analyze training institutions CSV data"""
        analysis = {
            'analysis_type': 'training',
            'analysis_date': datetime.now().isoformat(),
            'summary': {},
            'insights': [],
            'recommendations': [],
            'program_analysis': {},
            'institution_ranking': {}
        }
        
        try:
            # Basic Summary
            analysis['summary'] = {
                'total_records': len(df),
                'total_capacity': int(df['annual_capacity'].sum()) if 'annual_capacity' in df.columns else 0,
                'total_enrollment': int(df['current_enrollment'].sum()) if 'current_enrollment' in df.columns else 0,
                'total_graduates': int(df['annual_graduates'].sum()) if 'annual_graduates' in df.columns else 0,
                'institutions_count': df['institution_name'].nunique() if 'institution_name' in df.columns else 0,
                'programs_count': df['program_type'].nunique() if 'program_type' in df.columns else 0
            }
            
            # Calculate utilization rate
            if analysis['summary']['total_capacity'] > 0:
                utilization_rate = (analysis['summary']['total_enrollment'] / analysis['summary']['total_capacity']) * 100
                analysis['summary']['utilization_rate'] = round(utilization_rate, 2)
            
            # Program Analysis
            if 'program_type' in df.columns:
                program_data = df.groupby('program_type').agg({
                    'annual_capacity': 'sum',
                    'current_enrollment': 'sum',
                    'annual_graduates': 'sum'
                }).round(0)
                
                # Calculate utilization for each program
                program_data['utilization_rate'] = ((program_data['current_enrollment'] / program_data['annual_capacity']) * 100).round(2)
                
                analysis['program_analysis'] = program_data.to_dict('index')
            
            # Institution Ranking (by quality score if available)
            if 'institution_name' in df.columns:
                institution_cols = ['annual_capacity', 'annual_graduates']
                if 'quality_score' in df.columns:
                    institution_cols.append('quality_score')
                if 'employment_rate' in df.columns:
                    institution_cols.append('employment_rate')
                
                institution_data = df.groupby('institution_name')[institution_cols].mean().round(2)
                
                # Sort by quality score if available, otherwise by graduates
                sort_col = 'quality_score' if 'quality_score' in institution_data.columns else 'annual_graduates'
                institution_data = institution_data.sort_values(sort_col, ascending=False)
                
                analysis['institution_ranking'] = institution_data.to_dict('index')
            
            # Generate Insights
            analysis['insights'] = self.generate_training_insights(df, analysis)
            
            # Generate Recommendations
            analysis['recommendations'] = self.generate_training_recommendations(df, analysis)
            
        except Exception as e:
            analysis['error'] = f"Analysis failed: {str(e)}"
        
        return analysis
    
    def generate_workforce_insights(self, df, analysis):
        """Generate simple insights for workforce data"""
        insights = []
        
        try:
            summary = analysis['summary']
            
            # Overall staffing level
            if summary.get('vacancy_rate', 0) > 15:
                insights.append("🔴 HIGH ALERT: Overall vacancy rate exceeds 15% - critical staffing shortage")
            elif summary.get('vacancy_rate', 0) > 10:
                insights.append("⚠️ WARNING: Vacancy rate above 10% - moderate staffing concerns")
            else:
                insights.append("✅ GOOD: Vacancy rate is manageable")
            
            # Regional insights
            if 'regional_analysis' in analysis:
                high_gap_regions = []
                for region, data in analysis['regional_analysis'].items():
                    if data.get('vacancy_rate', 0) > 20:
                        high_gap_regions.append(region)
                
                if high_gap_regions:
                    insights.append(f"🎯 FOCUS REGIONS: {', '.join(high_gap_regions)} have critical shortages (>20% vacancy)")
            
            # Category insights
            if 'category_analysis' in analysis:
                critical_categories = []
                for category, data in analysis['category_analysis'].items():
                    if data.get('gap', 0) > 500:  # More than 500 positions short
                        critical_categories.append(category)
                
                if critical_categories:
                    insights.append(f"🏥 CRITICAL CATEGORIES: {', '.join(critical_categories)} need immediate attention")
            
        except Exception as e:
            insights.append(f"Error generating insights: {str(e)}")
        
        return insights
    
    def generate_workforce_recommendations(self, df, analysis):
        """Generate simple recommendations for workforce data"""
        recommendations = []
        
        try:
            summary = analysis['summary']
            
            # Overall recommendations
            if summary.get('vacancy_rate', 0) > 15:
                recommendations.append("🚀 URGENT: Launch emergency recruitment campaign")
                recommendations.append("💰 RETENTION: Increase salaries by 10-15% to reduce attrition")
                recommendations.append("🎓 TRAINING: Fast-track graduation of current students")
            
            # Regional recommendations
            if 'regional_analysis' in analysis:
                for region, data in analysis['regional_analysis'].items():
                    if data.get('gap', 0) > 1000:
                        recommendations.append(f"📍 {region}: Open new medical school or expand existing capacity")
                    elif data.get('gap', 0) > 500:
                        recommendations.append(f"📍 {region}: Increase recruitment efforts and consider incentives")
            
            # Category-specific recommendations
            if 'category_analysis' in analysis:
                for category, data in analysis['category_analysis'].items():
                    if data.get('vacancy_rate', 0) > 25:
                        recommendations.append(f"👨‍⚕️ {category}: Consider international recruitment or temporary staff")
            
            # General recommendations
            recommendations.append("📊 DATA: Update workforce data monthly for better planning")
            recommendations.append("🔄 MONITORING: Set up alerts for vacancy rates above 15%")
            
        except Exception as e:
            recommendations.append(f"Error generating recommendations: {str(e)}")
        
        return recommendations
    
    def generate_population_insights(self, df, analysis):
        """Generate insights for population data"""
        insights = []
        
        try:
            age_dist = analysis.get('age_distribution', {})
            
            # Age distribution insights
            if age_dist.get('elderly_65_plus', {}).get('percentage', 0) > 15:
                insights.append("👴 AGING POPULATION: High elderly population will increase healthcare demand")
            
            if age_dist.get('children_0_14', {}).get('percentage', 0) > 30:
                insights.append("👶 YOUNG POPULATION: High child population requires pediatric focus")
            
            working_age_pct = age_dist.get('working_age_15_64', {}).get('percentage', 0)
            if working_age_pct > 65:
                insights.append("💼 DEMOGRAPHIC DIVIDEND: Large working-age population is advantageous")
            elif working_age_pct < 55:
                insights.append("⚠️ DEPENDENCY RATIO: High dependency ratio may strain healthcare system")
            
        except Exception as e:
            insights.append(f"Error generating insights: {str(e)}")
        
        return insights
    
    def generate_population_recommendations(self, df, analysis):
        """Generate recommendations for population data"""
        recommendations = []
        
        try:
            age_dist = analysis.get('age_distribution', {})
            
            # Age-based recommendations
            if age_dist.get('elderly_65_plus', {}).get('percentage', 0) > 15:
                recommendations.append("🏥 GERIATRIC CARE: Expand geriatric medicine and long-term care facilities")
                recommendations.append("💊 CHRONIC DISEASE: Prepare for increased chronic disease management")
            
            if age_dist.get('children_0_14', {}).get('percentage', 0) > 25:
                recommendations.append("👶 PEDIATRIC SERVICES: Expand pediatric healthcare capacity")
                recommendations.append("🏫 SCHOOL HEALTH: Strengthen school health programs")
            
            # Regional recommendations
            if 'regional_breakdown' in analysis:
                high_pop_regions = []
                for region, data in analysis['regional_breakdown'].items():
                    if data.get('percentage', 0) > 20:  # Regions with >20% of population
                        high_pop_regions.append(region)
                
                if high_pop_regions:
                    recommendations.append(f"🏢 INFRASTRUCTURE: Prioritize healthcare infrastructure in {', '.join(high_pop_regions)}")
            
        except Exception as e:
            recommendations.append(f"Error generating recommendations: {str(e)}")
        
        return recommendations
    
    def generate_health_insights(self, df, analysis):
        """Generate insights for health conditions data"""
        insights = []
        
        try:
            if 'condition_ranking' in analysis:
                # Get top 3 conditions by cases
                top_conditions = list(analysis['condition_ranking'].keys())[:3]
                if top_conditions:
                    insights.append(f"🏥 TOP HEALTH ISSUES: {', '.join(top_conditions)} are the major health concerns")
                
                # Check for high prevalence conditions
                for condition, data in analysis['condition_ranking'].items():
                    if data.get('prevalence_rate', 0) > 20:
                        insights.append(f"🚨 HIGH PREVALENCE: {condition} affects over 20% of the population")
            
        except Exception as e:
            insights.append(f"Error generating insights: {str(e)}")
        
        return insights
    
    def generate_health_recommendations(self, df, analysis):
        """Generate recommendations for health conditions data"""
        recommendations = []
        
        try:
            if 'condition_ranking' in analysis:
                for condition, data in analysis['condition_ranking'].items():
                    cases = data.get('total_cases', 0)
                    prevalence = data.get('prevalence_rate', 0)
                    
                    if prevalence > 15:
                        recommendations.append(f"🎯 {condition}: Launch targeted prevention programs")
                    
                    if cases > 1000000:  # Over 1 million cases
                        recommendations.append(f"🏥 {condition}: Increase specialist training capacity")
            
            # General recommendations
            recommendations.append("📊 PREVENTION: Focus on preventive care to reduce disease burden")
            recommendations.append("🔬 RESEARCH: Investigate causes of high-prevalence conditions")
            
        except Exception as e:
            recommendations.append(f"Error generating recommendations: {str(e)}")
        
        return recommendations
    
    def generate_training_insights(self, df, analysis):
        """Generate insights for training data"""
        insights = []
        
        try:
            summary = analysis['summary']
            
            # Utilization insights
            utilization = summary.get('utilization_rate', 0)
            if utilization > 95:
                insights.append("📈 CAPACITY CONSTRAINT: Training institutions at near-maximum capacity")
            elif utilization < 70:
                insights.append("📉 UNDERUTILIZATION: Training capacity is underused")
            else:
                insights.append("✅ BALANCED: Training capacity utilization is optimal")
            
            # Graduate output insights
            graduates = summary.get('total_graduates', 0)
            if graduates > 2000:
                insights.append(f"🎓 HIGH OUTPUT: Producing {graduates:,} graduates annually")
            else:
                insights.append(f"⚠️ LOW OUTPUT: Only {graduates:,} graduates annually may not meet demand")
            
        except Exception as e:
            insights.append(f"Error generating insights: {str(e)}")
        
        return insights
    
    def generate_training_recommendations(self, df, analysis):
        """Generate recommendations for training data"""
        recommendations = []
        
        try:
            summary = analysis['summary']
            
            # Capacity recommendations
            utilization = summary.get('utilization_rate', 0)
            if utilization > 95:
                recommendations.append("🏗️ EXPANSION: Build new training facilities or expand existing ones")
            elif utilization < 70:
                recommendations.append("📢 RECRUITMENT: Increase student recruitment efforts")
            
            # Program-specific recommendations
            if 'program_analysis' in analysis:
                for program, data in analysis['program_analysis'].items():
                    program_util = data.get('utilization_rate', 0)
                    if program_util > 98:
                        recommendations.append(f"📚 {program}: Urgent capacity expansion needed")
                    elif program_util < 60:
                        recommendations.append(f"📚 {program}: Improve marketing and recruitment")
            
            # Quality recommendations
            recommendations.append("⭐ QUALITY: Monitor and improve training quality metrics")
            recommendations.append("💼 EMPLOYMENT: Track graduate employment outcomes")
            
        except Exception as e:
            recommendations.append(f"Error generating recommendations: {str(e)}")
        
        return recommendations
    
    def export_analysis_report(self, analysis, format='json'):
        """Export analysis results to different formats"""
        try:
            if format == 'json':
                return json.dumps(analysis, indent=2, default=str)
            elif format == 'summary':
                # Create a text summary
                report = f"""
HEALTHCARE WORKFORCE ANALYSIS REPORT
Generated: {analysis.get('analysis_date', 'Unknown')}
Analysis Type: {analysis.get('analysis_type', 'Unknown')}

SUMMARY:
{self._format_summary(analysis.get('summary', {}))}

KEY INSIGHTS:
{self._format_list(analysis.get('insights', []))}

RECOMMENDATIONS:
{self._format_list(analysis.get('recommendations', []))}
"""
                return report
        except Exception as e:
            return f"Export error: {str(e)}"
    
    def _format_summary(self, summary):
        """Format summary data for text report"""
        lines = []
        for key, value in summary.items():
            formatted_key = key.replace('_', ' ').title()
            lines.append(f"- {formatted_key}: {value:,}" if isinstance(value, (int, float)) else f"- {formatted_key}: {value}")
        return '\n'.join(lines)
    
    def _format_list(self, items):
        """Format list items for text report"""
        return '\n'.join(f"• {item}" for item in items) 