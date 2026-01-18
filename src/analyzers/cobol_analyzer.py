import re
from typing import Dict, List, Any, Tuple
import logging
from src.llm_integration.groq_client import GroqClient

logger = logging.getLogger(__name__)

class COBOLAnalyzer:
    def __init__(self):
        self.groq_client = GroqClient()
        self.cobol_patterns = {
            'division': r'(IDENTIFICATION|ENVIRONMENT|DATA|PROCEDURE)\s+DIVISION',
            'section': r'[A-Z0-9-]+\s+SECTION\.',
            'paragraph': r'[A-Z0-9-]+\s*\..*',
            'copybook': r'COPY\s+([A-Z0-9-]+)\.',
            'call': r'CALL\s+[\'"]([A-Z0-9-]+)[\'"]',
            'sql': r'EXEC\s+SQL\s+(.*?)\s+END-EXEC',
            'business_logic': r'(COMPUTE|MOVE|IF|ELSE|PERFORM|UNTIL|VARYING|EVALUATE)'
        }
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a COBOL file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Basic structure analysis
            structure = self._extract_structure(content)
            
            # Extract business rules using Groq
            business_rules = self.groq_client.analyze_code(content[:5000], "business_rules")
            
            # Extract dependencies
            dependencies = self._extract_dependencies(content)
            
            # Calculate metrics
            metrics = self._calculate_metrics(content)
            
            return {
                "file_name": file_path.split('/')[-1],
                "structure": structure,
                "business_rules": business_rules,
                "dependencies": dependencies,
                "metrics": metrics,
                "analysis_type": "COBOL"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing COBOL file {file_path}: {e}")
            return {"error": str(e)}
    
    def _extract_structure(self, content: str) -> Dict[str, List]:
        """Extract COBOL program structure"""
        structure = {
            "divisions": [],
            "sections": [],
            "paragraphs": [],
            "copybooks": [],
            "calls": []
        }
        
        # Find divisions
        divisions = re.findall(self.cobol_patterns['division'], content, re.IGNORECASE)
        structure["divisions"] = [d[0] for d in divisions]
        
        # Find sections
        sections = re.findall(self.cobol_patterns['section'], content)
        structure["sections"] = sections
        
        # Find paragraphs
        paragraphs = re.findall(self.cobol_patterns['paragraph'], content)
        structure["paragraphs"] = paragraphs[:50]
        
        # Find copybooks
        copybooks = re.findall(self.cobol_patterns['copybook'], content, re.IGNORECASE)
        structure["copybooks"] = list(set(copybooks))
        
        # Find CALL statements
        calls = re.findall(self.cobol_patterns['call'], content, re.IGNORECASE)
        structure["calls"] = list(set(calls))
        
        return structure
    
    def _extract_dependencies(self, content: str) -> Dict[str, List]:
        """Extract dependencies from COBOL code"""
        dependencies = {
            "internal": [],
            "external": [],
            "databases": [],
            "files": []
        }
        
        # Extract file operations
        file_patterns = [
            r'SELECT\s+([A-Z0-9-]+)\s+ASSIGN\s+TO\s+([A-Z0-9-]+)',
            r'FD\s+([A-Z0-9-]+)',
            r'OPEN\s+(INPUT|OUTPUT|I-O|EXTEND)\s+([A-Z0-9-]+)'
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    dependencies["files"].append(match[-1])
                else:
                    dependencies["files"].append(match)
        
        # Extract SQL dependencies
        sql_matches = re.findall(self.cobol_patterns['sql'], content, re.IGNORECASE | re.DOTALL)
        for sql in sql_matches:
            if 'FROM' in sql.upper():
                table_match = re.search(r'FROM\s+([A-Z0-9-]+)', sql, re.IGNORECASE)
                if table_match:
                    dependencies["databases"].append(table_match.group(1))
        
        return dependencies
    
    def _calculate_metrics(self, content: str) -> Dict[str, float]:
        """Calculate complexity metrics for COBOL code"""
        lines = content.split('\n')
        total_lines = len(lines)
        
        # Count comments (lines starting with *)
        comment_lines = sum(1 for line in lines if line.strip().startswith('*'))
        
        # Count executable lines
        exec_lines = sum(1 for line in lines 
                        if line.strip() 
                        and not line.strip().startswith('*')
                        and not line.strip().startswith('/'))
        
        # Count control statements
        control_statements = sum(
            1 for line in lines 
            if any(keyword in line.upper() 
                  for keyword in ['IF ', 'PERFORM ', 'UNTIL ', 'VARYING ', 'EVALUATE '])
        )
        
        # Calculate cyclomatic complexity
        cyclomatic = control_statements + 1
        
        # Calculate comment percentage
        comment_percentage = (comment_lines / total_lines * 100) if total_lines > 0 else 0
        
        # Calculate maintainability index (simplified)
        maintainability = max(0, min(100, 100 - (cyclomatic * 2)))
        
        return {
            "total_lines": total_lines,
            "executable_lines": exec_lines,
            "comment_lines": comment_lines,
            "comment_percentage": round(comment_percentage, 2),
            "control_statements": control_statements,
            "cyclomatic_complexity": cyclomatic,
            "maintainability_index": maintainability
        }