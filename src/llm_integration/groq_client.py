import json
import requests
from typing import Dict, Any, List
import time
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        if not self.api_key or self.api_key == "your_groq_api_key_here":
            raise ValueError("Please set GROQ_API_KEY in .env file")
        
        # Use llama-3.1-8b-instant as default
        self.model = "llama-3.1-8b-instant"
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"GroqClient initialized with model: {self.model}")
    
    def analyze_code(self, code: str, analysis_type: str) -> Dict[str, Any]:
        """Analyze code using Groq LLM"""
        
        # Limit code size
        if len(code) > 8000:
            code = code[:8000] + "\n...[truncated for analysis]"
        
        prompts = {
            "business_rules": """You are a legacy code analysis expert. Extract business rules from this code.

Return JSON with this exact structure:
{
    "business_rules": [
        {
            "id": "BR001",
            "description": "Clear description of business rule",
            "logic": "Technical implementation",
            "complexity": "low/medium/high",
            "inputs": [],
            "outputs": [],
            "dependencies": []
        }
    ],
    "summary": "Brief summary",
    "total_rules_extracted": 1
}

Focus on extracting:
1. Business logic and rules
2. Data transformations
3. Decision points
4. Calculation logic
5. Validation rules

Return ONLY valid JSON.""",
            
            "risk_assessment": """Assess migration risks in legacy code. Return JSON with:
{
    "risks": [
        {
            "category": "technical/business/operational",
            "description": "Risk description",
            "severity": "low/medium/high/critical",
            "impact": "Potential impact",
            "mitigation": "Mitigation strategy"
        }
    ],
    "overall_risk_score": 0-100,
    "recommendations": []
}""",
            
            "modernization": """Recommend modernization strategies. Return JSON with:
{
    "strategies": [
        {
            "name": "strategy_name",
            "type": "refactor/rewrite/replatform",
            "effort": "low/medium/high",
            "timeline": "estimate",
            "risks": [],
            "benefits": []
        }
    ],
    "recommended_strategy": "name",
    "rationale": "explanation"
}"""
        }
        
        prompt = prompts.get(analysis_type, prompts["business_rules"])
        
        messages = [
            {"role": "system", "content": "You are a legacy code analysis expert. Return ONLY valid JSON."},
            {"role": "user", "content": f"{prompt}\n\nCode:\n```\n{code}\n```"}
        ]
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 2000,
            "response_format": {"type": "json_object"}
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Parse JSON response
                try:
                    # Clean content
                    content = content.strip()
                    if content.startswith("```json"):
                        content = content[7:]
                    if content.startswith("```"):
                        content = content[3:]
                    if content.endswith("```"):
                        content = content[:-3]
                    
                    return json.loads(content)
                except json.JSONDecodeError:
                    # Try to extract JSON
                    try:
                        start = content.find('{')
                        end = content.rfind('}') + 1
                        if start >= 0 and end > start:
                            return json.loads(content[start:end])
                    except:
                        return {"raw_analysis": content[:500]}
            else:
                return {"error": f"API error {response.status_code}", "details": response.text[:200]}
                
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def batch_analyze(self, code_chunks: List[str], analysis_type: str) -> List[Dict[str, Any]]:
        """Analyze multiple chunks with rate limiting"""
        results = []
        for i, chunk in enumerate(code_chunks):
            logger.info(f"Analyzing chunk {i+1}/{len(code_chunks)}")
            result = self.analyze_code(chunk, analysis_type)
            results.append(result)
            time.sleep(0.5)  # Rate limiting
        return results