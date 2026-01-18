import os
import json
from typing import Dict, List, Any
from pathlib import Path
from src.analyzers.cobol_analyzer import COBOLAnalyzer
from src.llm_integration.groq_client import GroqClient
import logging

logger = logging.getLogger(__name__)

class BusinessRuleExtractor:
    def __init__(self, output_dir: str = "data/outputs/business_rules"):
        self.cobol_analyzer = COBOLAnalyzer()
        self.groq_client = GroqClient()
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def extract_from_directory(self, directory_path: str) -> Dict[str, Any]:
        """Extract business rules from all files in directory"""
        all_rules = []
        file_analyses = []
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = Path(file).suffix.lower()
                
                if file_ext in ['.cobol', '.cbl', '.cob']:
                    logger.info(f"Analyzing COBOL file: {file}")
                    analysis = self.cobol_analyzer.analyze_file(file_path)
                    
                    if "business_rules" in analysis:
                        rules = analysis["business_rules"]
                        if isinstance(rules, dict) and "business_rules" in rules:
                            for rule in rules["business_rules"]:
                                rule["source_file"] = file
                                rule["language"] = "COBOL"
                                all_rules.append(rule)
                    
                    file_analyses.append({
                        "file": file,
                        "metrics": analysis.get("metrics", {}),
                        "dependencies": analysis.get("dependencies", {})
                    })
        
        # Create comprehensive report
        report = self._generate_report(all_rules, file_analyses)
        
        # Save results
        self._save_results(all_rules, report)
        
        return {
            "total_rules_extracted": len(all_rules),
            "files_analyzed": len(file_analyses),
            "business_rules": all_rules[:100],  # Limit for response
            "report_summary": report,
            "output_files": [
                f"{self.output_dir}/business_rules.json",
                f"{self.output_dir}/analysis_report.json"
            ]
        }
    
    def _generate_report(self, rules: List[Dict], file_analyses: List[Dict]) -> Dict[str, Any]:
        """Generate analysis report"""
        # Categorize rules by complexity
        complexity_dist = {"low": 0, "medium": 0, "high": 0}
        for rule in rules:
            complexity = rule.get("complexity", "medium").lower()
            if complexity in complexity_dist:
                complexity_dist[complexity] += 1
        
        # Calculate aggregate metrics
        total_complexity = sum(
            file_analysis["metrics"].get("cyclomatic_complexity", 0)
            for file_analysis in file_analyses
        )
        
        avg_maintainability = sum(
            file_analysis["metrics"].get("maintainability_index", 0)
            for file_analysis in file_analyses
        ) / len(file_analyses) if file_analyses else 0
        
        return {
            "total_rules": len(rules),
            "complexity_distribution": complexity_dist,
            "average_cyclomatic_complexity": round(total_complexity / len(file_analyses), 2) if file_analyses else 0,
            "average_maintainability_index": round(avg_maintainability, 2),
            "files_analyzed": len(file_analyses),
            "recommendations": self._generate_recommendations(rules, file_analyses)
        }
    
    def _generate_recommendations(self, rules: List[Dict], file_analyses: List[Dict]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Check for high complexity
        high_complex_files = [
            fa["file"] for fa in file_analyses
            if fa["metrics"].get("cyclomatic_complexity", 0) > 10
        ]
        
        if high_complex_files:
            recommendations.append(
                f"Refactor {len(high_complex_files)} files with high cyclomatic complexity"
            )
        
        # Check for low maintainability
        low_maintain_files = [
            fa["file"] for fa in file_analyses
            if fa["metrics"].get("maintainability_index", 100) < 50
        ]
        
        if low_maintain_files:
            recommendations.append(
                f"Improve maintainability in {len(low_maintain_files)} files"
            )
        
        # Check for business rule complexity
        high_complex_rules = [r for r in rules if r.get("complexity", "medium") == "high"]
        if high_complex_rules:
            recommendations.append(
                f"Document and test {len(high_complex_rules)} high-complexity business rules"
            )
        
        return recommendations
    
    def _save_results(self, rules: List[Dict], report: Dict[str, Any]):
        """Save extracted rules and report to files"""
        # Save business rules
        rules_file = f"{self.output_dir}/business_rules.json"
        with open(rules_file, 'w', encoding='utf-8') as f:
            json.dump(rules, f, indent=2, ensure_ascii=False)
        
        # Save report
        report_file = f"{self.output_dir}/analysis_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Create CSV summary
        csv_file = f"{self.output_dir}/rules_summary.csv"
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write("ID,Description,Complexity,Source File,Language\n")
            for rule in rules:
                f.write(f'{rule.get("id", "N/A")},')
                f.write(f'"{rule.get("description", "").replace(",", ";")}",')
                f.write(f'{rule.get("complexity", "N/A")},')
                f.write(f'{rule.get("source_file", "N/A")},')
                f.write(f'{rule.get("language", "N/A")}\n')
        
        logger.info(f"Results saved to {self.output_dir}")