import json
from typing import Dict, List, Any
from datetime import datetime
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class MigrationRiskAssessor:
    def __init__(self):
        self.risk_categories = {
            "technical": [
                "code_complexity",
                "architecture_debt",
                "dependency_management",
                "technology_obsolescence"
            ],
            "business": [
                "business_rule_complexity",
                "data_migration",
                "integration_points",
                "regulatory_compliance"
            ],
            "operational": [
                "performance_requirements",
                "scalability_issues",
                "security_vulnerabilities",
                "monitoring_gaps"
            ]
        }
    
    def assess_risks(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess migration risks based on analysis results"""
        
        risks = []
        risk_scores = {}
        
        # Assess technical risks
        technical_risks = self._assess_technical_risks(analysis_results)
        risks.extend(technical_risks)
        
        # Assess business risks
        business_risks = self._assess_business_risks(analysis_results)
        risks.extend(business_risks)
        
        # Calculate overall risk score
        overall_score = self._calculate_overall_score(risks)
        
        # Generate mitigation strategies
        mitigation = self._generate_mitigation_strategies(risks)
        
        # Recommend modernization approach
        modernization_approach = self._recommend_modernization_approach(
            overall_score, 
            analysis_results
        )
        
        return {
            "assessment_date": datetime.now().isoformat(),
            "overall_risk_score": overall_score,
            "risk_level": self._get_risk_level(overall_score),
            "risks": risks,
            "mitigation_strategies": mitigation,
            "modernization_recommendation": modernization_approach,
            "summary": self._generate_risk_summary(risks, overall_score)
        }
    
    def _assess_technical_risks(self, analysis: Dict[str, Any]) -> List[Dict]:
        """Assess technical risks"""
        risks = []
        
        # Code complexity risk
        complexity = analysis.get("metrics", {}).get("average_cyclomatic_complexity", 0)
        if complexity > 15:
            risks.append({
                "category": "technical",
                "type": "code_complexity",
                "severity": "high",
                "description": f"High cyclomatic complexity ({complexity}) indicates difficult-to-maintain code",
                "impact": "Increased maintenance costs, higher bug probability",
                "confidence": 0.8
            })
        
        # Dependency risk
        dependencies = analysis.get("total_dependencies", 0)
        if dependencies > 20:
            risks.append({
                "category": "technical",
                "type": "dependency_management",
                "severity": "medium",
                "description": f"High number of dependencies ({dependencies}) creates migration complexity",
                "impact": "Potential compatibility issues during migration",
                "confidence": 0.7
            })
        
        return risks
    
    def _assess_business_risks(self, analysis: Dict[str, Any]) -> List[Dict]:
        """Assess business risks"""
        risks = []
        
        # Business rule complexity risk
        high_complex_rules = analysis.get("high_complexity_rules", 0)
        if high_complex_rules > 5:
            risks.append({
                "category": "business",
                "type": "business_rule_complexity",
                "severity": "high",
                "description": f"{high_complex_rules} high-complexity business rules identified",
                "impact": "Risk of misinterpretation or incorrect implementation during migration",
                "confidence": 0.9
            })
        
        return risks
    
    def _calculate_overall_score(self, risks: List[Dict]) -> float:
        """Calculate overall risk score (0-100)"""
        if not risks:
            return 0.0
        
        severity_weights = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.5,
            "low": 0.2
        }
        
        total_weight = 0
        weighted_sum = 0
        
        for risk in risks:
            severity = risk.get("severity", "medium").lower()
            confidence = risk.get("confidence", 0.5)
            weight = severity_weights.get(severity, 0.5)
            
            weighted_sum += weight * confidence * 100
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return min(100, weighted_sum / total_weight)
    
    def _get_risk_level(self, score: float) -> str:
        """Convert score to risk level"""
        if score >= 75:
            return "CRITICAL"
        elif score >= 50:
            return "HIGH"
        elif score >= 25:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_mitigation_strategies(self, risks: List[Dict]) -> List[Dict]:
        """Generate mitigation strategies for identified risks"""
        strategies = []
        
        mitigation_map = {
            "code_complexity": {
                "strategy": "Incremental refactoring",
                "actions": [
                    "Break down complex modules into smaller functions",
                    "Implement comprehensive unit tests",
                    "Document business logic before migration"
                ]
            },
            "dependency_management": {
                "strategy": "Dependency mapping and testing",
                "actions": [
                    "Create dependency graph",
                    "Test integration points",
                    "Plan phased migration"
                ]
            },
            "business_rule_complexity": {
                "strategy": "Business rule validation",
                "actions": [
                    "Create business rule catalog",
                    "Validate with business stakeholders",
                    "Implement rule engine if applicable"
                ]
            }
        }
        
        for risk in risks:
            risk_type = risk.get("type")
            if risk_type in mitigation_map:
                strategies.append({
                    "risk_type": risk_type,
                    "risk_severity": risk.get("severity"),
                    "mitigation_strategy": mitigation_map[risk_type]["strategy"],
                    "recommended_actions": mitigation_map[risk_type]["actions"],
                    "estimated_effort": "medium"
                })
        
        return strategies
    
    def _recommend_modernization_approach(self, risk_score: float, analysis: Dict) -> Dict[str, Any]:
        """Recommend modernization approach based on risk assessment"""
        
        if risk_score >= 70:
            return {
                "approach": "Rewrite",
                "rationale": "High risk and complexity make refactoring impractical",
                "estimated_timeline": "6-12 months",
                "estimated_cost": "high",
                "success_probability": "medium",
                "key_considerations": [
                    "Requires thorough business rule extraction",
                    "Parallel run recommended",
                    "Phased deployment advised"
                ]
            }
        elif risk_score >= 40:
            return {
                "approach": "Refactor + Replatform",
                "rationale": "Moderate risk allows for incremental modernization",
                "estimated_timeline": "3-6 months",
                "estimated_cost": "medium",
                "success_probability": "high",
                "key_considerations": [
                    "Start with least complex modules",
                    "Maintain data consistency",
                    "Continuous testing required"
                ]
            }
        else:
            return {
                "approach": "Refactor",
                "rationale": "Low risk allows for safe refactoring",
                "estimated_timeline": "1-3 months",
                "estimated_cost": "low",
                "success_probability": "very high",
                "key_considerations": [
                    "Improve code structure incrementally",
                    "Add automated tests",
                    "Document as you go"
                ]
            }
    
    def _generate_risk_summary(self, risks: List[Dict], overall_score: float) -> str:
        """Generate human-readable risk summary"""
        risk_by_category = {}
        for risk in risks:
            category = risk.get("category", "unknown")
            if category not in risk_by_category:
                risk_by_category[category] = 0
            risk_by_category[category] += 1
        
        summary = f"Overall Risk Score: {overall_score:.1f}/100 ({self._get_risk_level(overall_score)})\n"
        summary += f"Total Risks Identified: {len(risks)}\n"
        
        for category, count in risk_by_category.items():
            summary += f"{category.capitalize()} Risks: {count}\n"
        
        high_risks = [r for r in risks if r.get("severity") in ["high", "critical"]]
        if high_risks:
            summary += f"\nHigh/Critical Risks: {len(high_risks)}\n"
            for i, risk in enumerate(high_risks[:3], 1):
                summary += f"{i}. {risk.get('description', '')}\n"
        
        return summary