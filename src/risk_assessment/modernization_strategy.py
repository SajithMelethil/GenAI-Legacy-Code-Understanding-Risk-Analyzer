import json
from typing import Dict, List, Any, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ModernizationStrategyRecommender:
    def __init__(self):
        self.strategy_templates = {
            "refactor": {
                "name": "Incremental Refactoring",
                "description": "Improve existing code structure while maintaining functionality",
                "applicability": ["Low complexity", "Good test coverage", "Stable requirements"],
                "risks": ["Incomplete refactoring", "Regression bugs", "Scope creep"],
                "success_factors": ["Strong test suite", "Continuous integration", "Team expertise"],
                "estimated_timeline": "1-3 months",
                "estimated_cost": "Low to Medium"
            },
            "rewrite": {
                "name": "Complete Rewrite",
                "description": "Build new system from scratch based on extracted business rules",
                "applicability": ["High technical debt", "Obsolete technology", "Major functionality changes"],
                "risks": ["Cost overruns", "Schedule delays", "Feature gaps"],
                "success_factors": ["Clear requirements", "Parallel run strategy", "Stakeholder commitment"],
                "estimated_timeline": "6-12 months",
                "estimated_cost": "High"
            },
            "replatform": {
                "name": "Replatform to Cloud",
                "description": "Lift and shift to modern cloud infrastructure",
                "applicability": ["Hardware dependency", "Scalability needs", "Cost optimization"],
                "risks": ["Cloud lock-in", "Performance issues", "Security concerns"],
                "success_factors": ["Cloud expertise", "Migration tools", "Compliance checks"],
                "estimated_timeline": "3-6 months",
                "estimated_cost": "Medium"
            },
            "rehost": {
                "name": "Containerization",
                "description": "Package legacy applications in containers",
                "applicability": ["Complex deployment", "Environment consistency", "CI/CD adoption"],
                "risks": ["Container management", "Storage issues", "Networking complexity"],
                "success_factors": ["Container expertise", "Orchestration platform", "Monitoring tools"],
                "estimated_timeline": "2-4 months",
                "estimated_cost": "Medium"
            },
            "retire": {
                "name": "Retire and Replace",
                "description": "Decommission legacy system and replace with commercial solution",
                "applicability": ["Non-core functionality", "High maintenance cost", "Available SaaS alternatives"],
                "risks": ["Vendor lock-in", "Data migration", "Business process changes"],
                "success_factors": ["Vendor evaluation", "Transition plan", "User training"],
                "estimated_timeline": "3-9 months",
                "estimated_cost": "Varies"
            }
        }
    
    def recommend_strategies(self, analysis_results: Dict, risk_assessment: Dict = None) -> Dict[str, Any]:
        """Recommend modernization strategies based on analysis"""
        
        # Extract metrics from analysis
        complexity = analysis_results.get("metrics", {}).get("average_cyclomatic_complexity", 0)
        rule_count = analysis_results.get("total_rules_extracted", 0)
        high_complexity_rules = analysis_results.get("high_complexity_rules", 0)
        dependencies = analysis_results.get("total_dependencies", 0)
        
        # Calculate strategy scores
        strategy_scores = self._calculate_strategy_scores(
            complexity, rule_count, high_complexity_rules, dependencies
        )
        
        # Get risk level if available
        risk_level = risk_assessment.get("risk_level", "MEDIUM") if risk_assessment else "MEDIUM"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(strategy_scores, risk_level)
        
        # Create modernization roadmap
        roadmap = self._create_roadmap(recommendations)
        
        return {
            "assessment_date": datetime.now().isoformat(),
            "analysis_metrics": {
                "complexity_score": complexity,
                "business_rules_count": rule_count,
                "high_complexity_rules": high_complexity_rules,
                "dependencies_count": dependencies
            },
            "strategy_scores": strategy_scores,
            "recommendations": recommendations,
            "modernization_roadmap": roadmap,
            "detailed_strategies": self._get_detailed_strategies(recommendations)
        }
    
    def _calculate_strategy_scores(self, complexity: float, rule_count: int, 
                                 high_complex_rules: int, dependencies: int) -> Dict[str, float]:
        """Calculate suitability scores for each strategy"""
        
        scores = {}
        
        # Refactor score (good for low complexity)
        scores["refactor"] = max(0, 100 - (complexity * 3))
        
        # Rewrite score (good for high complexity)
        scores["rewrite"] = min(100, complexity * 5 + high_complex_rules * 2)
        
        # Replatform score (good for moderate complexity with many dependencies)
        scores["replatform"] = min(100, 40 + (dependencies * 0.5))
        
        # Rehost score (containerization)
        scores["rehost"] = 60  # Generally applicable
        
        # Retire score (if few business rules)
        scores["retire"] = max(0, 100 - (rule_count * 0.5))
        
        return scores
    
    def _generate_recommendations(self, strategy_scores: Dict[str, float], 
                                risk_level: str) -> List[Dict[str, Any]]:
        """Generate recommendations based on scores and risk"""
        
        recommendations = []
        
        # Sort strategies by score
        sorted_strategies = sorted(strategy_scores.items(), key=lambda x: x[1], reverse=True)
        
        for strategy_name, score in sorted_strategies[:3]:  # Top 3 strategies
            template = self.strategy_templates.get(strategy_name, {})
            
            recommendation = {
                "strategy": strategy_name,
                "score": round(score, 1),
                "name": template.get("name", strategy_name),
                "description": template.get("description", ""),
                "suitability": self._get_suitability_level(score),
                "risk_adjustment": self._adjust_for_risk(strategy_name, risk_level),
                "priority": len(recommendations) + 1
            }
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _get_suitability_level(self, score: float) -> str:
        """Convert score to suitability level"""
        if score >= 80:
            return "Highly Suitable"
        elif score >= 60:
            return "Suitable"
        elif score >= 40:
            return "Moderately Suitable"
        else:
            return "Not Recommended"
    
    def _adjust_for_risk(self, strategy: str, risk_level: str) -> Dict[str, Any]:
        """Adjust strategy recommendations based on risk level"""
        
        risk_adjustments = {
            "LOW": {
                "refactor": {"confidence": "High", "timeline_modifier": -0.1},
                "rewrite": {"confidence": "Low", "timeline_modifier": 0},
                "replatform": {"confidence": "Medium", "timeline_modifier": -0.1},
                "rehost": {"confidence": "High", "timeline_modifier": -0.2},
                "retire": {"confidence": "Medium", "timeline_modifier": 0}
            },
            "MEDIUM": {
                "refactor": {"confidence": "Medium", "timeline_modifier": 0},
                "rewrite": {"confidence": "Medium", "timeline_modifier": 0.1},
                "replatform": {"confidence": "High", "timeline_modifier": 0},
                "rehost": {"confidence": "Medium", "timeline_modifier": 0},
                "retire": {"confidence": "Low", "timeline_modifier": 0.2}
            },
            "HIGH": {
                "refactor": {"confidence": "Low", "timeline_modifier": 0.2},
                "rewrite": {"confidence": "High", "timeline_modifier": 0.3},
                "replatform": {"confidence": "Medium", "timeline_modifier": 0.1},
                "rehost": {"confidence": "Low", "timeline_modifier": 0.1},
                "retire": {"confidence": "Medium", "timeline_modifier": 0.1}
            },
            "CRITICAL": {
                "refactor": {"confidence": "Very Low", "timeline_modifier": 0.5},
                "rewrite": {"confidence": "Very High", "timeline_modifier": 0.4},
                "replatform": {"confidence": "Low", "timeline_modifier": 0.3},
                "rehost": {"confidence": "Very Low", "timeline_modifier": 0.3},
                "retire": {"confidence": "Medium", "timeline_modifier": 0.2}
            }
        }
        
        return risk_adjustments.get(risk_level, {}).get(strategy, {
            "confidence": "Medium",
            "timeline_modifier": 0
        })
    
    def _create_roadmap(self, recommendations: List[Dict]) -> Dict[str, Any]:
        """Create phased modernization roadmap"""
        
        phases = []
        
        # Phase 1: Assessment and Planning (Always first)
        phases.append({
            "phase": 1,
            "name": "Assessment & Planning",
            "duration": "2-4 weeks",
            "activities": [
                "Detailed requirements gathering",
                "Stakeholder alignment",
                "Proof of concept",
                "Migration strategy finalization"
            ],
            "deliverables": ["Detailed migration plan", "Risk mitigation strategy", "Success criteria"]
        })
        
        # Add strategy-specific phases
        for i, rec in enumerate(recommendations[:2], start=2):  # Top 2 strategies
            strategy = rec["strategy"]
            
            if strategy == "refactor":
                phases.append({
                    "phase": i,
                    "name": "Incremental Refactoring",
                    "duration": "1-3 months",
                    "activities": [
                        "Create comprehensive test suite",
                        "Refactor high-priority modules",
                        "Continuous integration setup",
                        "Performance testing"
                    ],
                    "deliverables": ["Refactored codebase", "Automated test suite", "CI/CD pipeline"]
                })
            elif strategy == "rewrite":
                phases.append({
                    "phase": i,
                    "name": "Parallel Development",
                    "duration": "3-6 months",
                    "activities": [
                        "New system architecture design",
                        "Core functionality implementation",
                        "Data migration planning",
                        "Integration testing"
                    ],
                    "deliverables": ["New system prototype", "Data migration tools", "Integration test suite"]
                })
            elif strategy == "replatform":
                phases.append({
                    "phase": i,
                    "name": "Cloud Migration",
                    "duration": "2-4 months",
                    "activities": [
                        "Cloud environment setup",
                        "Application containerization",
                        "Database migration",
                        "Security configuration"
                    ],
                    "deliverables": ["Cloud infrastructure", "Containerized apps", "Monitoring setup"]
                })
        
        # Final phase: Deployment and Transition
        phases.append({
            "phase": len(phases) + 1,
            "name": "Deployment & Transition",
            "duration": "1-2 months",
            "activities": [
                "Production deployment",
                "User training",
                "Parallel run (if applicable)",
                "Performance monitoring"
            ],
            "deliverables": ["Production system", "User documentation", "Support plan"]
        })
        
        return {
            "total_phases": len(phases),
            "estimated_timeline": self._calculate_timeline(phases),
            "phases": phases,
            "key_milestones": self._extract_milestones(phases)
        }
    
    def _calculate_timeline(self, phases: List[Dict]) -> str:
        """Calculate total timeline from phases"""
        # Simple estimation - in real implementation, would use more sophisticated logic
        total_months = len(phases) * 1.5  # Approximate
        return f"{total_months:.1f}-{total_months * 1.5:.1f} months"
    
    def _extract_milestones(self, phases: List[Dict]) -> List[Dict]:
        """Extract key milestones from roadmap"""
        milestones = []
        
        for phase in phases:
            if phase["phase"] in [1, len(phases)]:  # First and last phases
                milestones.append({
                    "phase": phase["phase"],
                    "name": phase["name"],
                    "description": f"Completion of {phase['name'].lower()} phase"
                })
        
        return milestones
    
    def _get_detailed_strategies(self, recommendations: List[Dict]) -> Dict[str, Any]:
        """Get detailed information for recommended strategies"""
        
        detailed = {}
        
        for rec in recommendations:
            strategy_name = rec["strategy"]
            template = self.strategy_templates.get(strategy_name, {})
            
            detailed[strategy_name] = {
                "summary": template,
                "pros": self._get_pros(strategy_name),
                "cons": self._get_cons(strategy_name),
                "best_for": template.get("applicability", []),
                "risk_factors": template.get("risks", []),
                "success_metrics": [
                    "Reduced maintenance costs",
                    "Improved system performance",
                    "Enhanced scalability",
                    "Better developer productivity"
                ]
            }
        
        return detailed
    
    def _get_pros(self, strategy: str) -> List[str]:
        """Get pros for each strategy"""
        
        pros_map = {
            "refactor": [
                "Preserves business logic and IP",
                "Lower risk than rewrite",
                "Incremental approach",
                "Immediate improvements visible"
            ],
            "rewrite": [
                "Clean slate architecture",
                "Modern technology stack",
                "Easier to maintain long-term",
                "Better performance potential"
            ],
            "replatform": [
                "Cloud scalability",
                "Reduced infrastructure costs",
                "Disaster recovery benefits",
                "Modern deployment options"
            ],
            "rehost": [
                "Environment consistency",
                "Simplified deployments",
                "Resource optimization",
                "Improved scalability"
            ],
            "retire": [
                "Eliminates maintenance costs",
                "Access to vendor support",
                "Regular updates and patches",
                "Focus on core business"
            ]
        }
        
        return pros_map.get(strategy, ["Varies based on context"])
    
    def _get_cons(self, strategy: str) -> List[str]:
        """Get cons for each strategy"""
        
        cons_map = {
            "refactor": [
                "Technical debt may remain",
                "Can be time-consuming",
                "Requires skilled developers",
                "Risk of incomplete refactoring"
            ],
            "rewrite": [
                "High initial cost",
                "Long timeline",
                "Risk of feature gaps",
                "Requires extensive testing"
            ],
            "replatform": [
                "Cloud vendor lock-in",
                "Learning curve for team",
                "Potential performance issues",
                "Ongoing cloud costs"
            ],
            "rehost": [
                "Container management complexity",
                "Storage and networking challenges",
                "Monitoring overhead",
                "Security considerations"
            ],
            "retire": [
                "Vendor lock-in",
                "Loss of control",
                "Integration challenges",
                "Data migration complexity"
            ]
        }
        
        return cons_map.get(strategy, ["Varies based on context"])