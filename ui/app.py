from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Optional
import os
import shutil
import uuid
from pathlib import Path
import json
import asyncio
import logging
from datetime import datetime
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GenAI Legacy Code Understanding & Risk Analyzer",
    version="1.0.0",
    description="""AI-powered analysis of legacy code for:
    • Business rule extraction and structuring
    • Migration risk assessment
    • Modernization strategy recommendations
    • System architecture documentation"""
)

# Create necessary directories
UPLOAD_DIR = "data/uploads"
OUTPUT_DIR = "data/outputs"
REPORTS_DIR = "data/reports"
STATIC_DIR = "ui/static"
TEMPLATES_DIR = "ui/templates"

for directory in [UPLOAD_DIR, OUTPUT_DIR, REPORTS_DIR, STATIC_DIR, TEMPLATES_DIR]:
    os.makedirs(directory, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Session storage
sessions = {}

# ========== IMPORT ALL MODULES ==========
try:
    from config.settings import settings
    CONFIG_LOADED = True
    logger.info("✅ Config loaded")
except ImportError as e:
    CONFIG_LOADED = False
    logger.warning(f"⚠️ Config not available: {e}")

try:
    from src.llm_integration.groq_client import GroqClient
    GROQ_CLIENT_AVAILABLE = True
    logger.info("✅ GroqClient loaded")
except ImportError as e:
    GROQ_CLIENT_AVAILABLE = False
    logger.warning(f"⚠️ GroqClient not available: {e}")

try:
    from src.analyzers.cobol_analyzer import COBOLAnalyzer
    COBOL_ANALYZER_AVAILABLE = True
    logger.info("✅ COBOLAnalyzer loaded")
except ImportError as e:
    COBOL_ANALYZER_AVAILABLE = False
    logger.warning(f"⚠️ COBOLAnalyzer not available: {e}")

try:
    from src.extractors.business_rule_extractor import BusinessRuleExtractor
    BUSINESS_RULE_EXTRACTOR_AVAILABLE = True
    logger.info("✅ BusinessRuleExtractor loaded")
except ImportError as e:
    BUSINESS_RULE_EXTRACTOR_AVAILABLE = False
    logger.warning(f"⚠️ BusinessRuleExtractor not available: {e}")

try:
    from src.risk_assessment.migration_risk import MigrationRiskAssessor
    MIGRATION_RISK_AVAILABLE = True
    logger.info("✅ MigrationRiskAssessor loaded")
except ImportError as e:
    MIGRATION_RISK_AVAILABLE = False
    logger.warning(f"⚠️ MigrationRiskAssessor not available: {e}")

try:
    from src.risk_assessment.modernization_strategy import ModernizationStrategyRecommender
    MODERNIZATION_AVAILABLE = True
    logger.info("✅ ModernizationStrategyRecommender loaded")
except ImportError as e:
    MODERNIZATION_AVAILABLE = False
    logger.warning(f"⚠️ ModernizationStrategyRecommender not available: {e}")

# ========== HELPER FUNCTIONS ==========
def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower()

def is_supported_file(filename: str) -> bool:
    ext = get_file_extension(filename)
    supported = {'.cobol', '.cbl', '.cob', '.java', '.py', '.c', '.cpp', '.cs', '.vb', '.txt'}
    return ext in supported

def analyze_file_with_groq(file_path: str, analysis_type: str):
    """Analyze file using Groq API"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(10000)
        
        if GROQ_CLIENT_AVAILABLE:
            groq_client = GroqClient()
            return groq_client.analyze_code(content, analysis_type)
        else:
            return {"error": "Groq client not available"}
    except Exception as e:
        logger.error(f"Error analyzing file {file_path}: {e}")
        return {"error": str(e)}

# ========== ROUTES ==========
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main index.html"""
    index_path = os.path.join(TEMPLATES_DIR, "index.html")
    if os.path.exists(index_path):
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        return HTMLResponse("""
        <html>
            <body>
                <h1>Legacy Code Analyzer</h1>
                <p>Create ui/templates/index.html for full UI</p>
                <a href="/upload">Upload Files</a>
            </body>
        </html>
        """)

@app.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    analysis_type: str = Form("business_rules")
):
    """Handle file upload and analysis"""
    try:
        # Create session
        session_id = str(uuid.uuid4())
        session_dir = os.path.join(UPLOAD_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Save uploaded files
        saved_files = []
        for file in files:
            filename = file.filename
            file_path = os.path.join(session_dir, filename)
            
            if is_supported_file(filename):
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                saved_files.append(filename)
        
        if not saved_files:
            raise HTTPException(status_code=400, detail="No supported files uploaded")
        
        # Initialize session
        sessions[session_id] = {
            "session_id": session_id,
            "files": saved_files,
            "analysis_type": analysis_type,
            "status": "processing",
            "start_time": datetime.now().isoformat(),
            "results": {
                "file_analyses": [],
                "business_rules": {},
                "risk_assessment": {},
                "modernization_strategies": {},
                "summary": {}
            },
            "errors": []
        }
        
        # Start analysis in background
        asyncio.create_task(process_comprehensive_analysis(session_id, session_dir, analysis_type))
        
        return JSONResponse({
            "session_id": session_id,
            "message": f"Analysis started for {len(saved_files)} files",
            "redirect_url": f"/results/{session_id}"
        })
        
    except Exception as e:
        logger.error(f"Upload error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_comprehensive_analysis(session_id: str, session_dir: str, analysis_type: str):
    """Complete analysis pipeline"""
    session = sessions.get(session_id)
    if not session:
        return
    
    try:
        all_file_analyses = []
        all_business_rules = []
        
        # ========== PHASE 1: FILE ANALYSIS ==========
        for filename in session["files"]:
            file_path = os.path.join(session_dir, filename)
            ext = get_file_extension(filename)
            
            file_analysis = {
                "filename": filename,
                "file_type": ext,
                "file_size": os.path.getsize(file_path)
            }
            
            # COBOL-specific analysis
            if ext in ['.cobol', '.cbl', '.cob'] and COBOL_ANALYZER_AVAILABLE:
                try:
                    analyzer = COBOLAnalyzer()
                    cobol_result = analyzer.analyze_file(file_path)
                    file_analysis.update(cobol_result)
                except Exception as e:
                    file_analysis["cobol_error"] = str(e)
            
            # Groq AI analysis for all files
            if analysis_type in ["business_rules", "full_analysis"]:
                try:
                    groq_result = analyze_file_with_groq(file_path, "business_rules")
                    file_analysis["groq_analysis"] = groq_result
                    
                    # Extract business rules from Groq response
                    if isinstance(groq_result, dict) and "business_rules" in groq_result:
                        for rule in groq_result["business_rules"]:
                            rule["source_file"] = filename
                            rule["language"] = "COBOL" if ext in ['.cobol', '.cbl', '.cob'] else "Unknown"
                            all_business_rules.append(rule)
                except Exception as e:
                    file_analysis["groq_error"] = str(e)
            
            all_file_analyses.append(file_analysis)
        
        session["results"]["file_analyses"] = all_file_analyses
        
        # ========== PHASE 2: BUSINESS RULES EXTRACTION ==========
        if analysis_type in ["business_rules", "full_analysis"] and BUSINESS_RULE_EXTRACTOR_AVAILABLE:
            try:
                extractor = BusinessRuleExtractor()
                business_rules = extractor.extract_from_directory(session_dir)
                session["results"]["business_rules"] = business_rules
                
                # Combine with Groq extracted rules
                if all_business_rules:
                    combined_rules = business_rules.get("business_rules", []) + all_business_rules
                    business_rules["total_rules_extracted"] = len(combined_rules)
                    business_rules["business_rules"] = combined_rules
            except Exception as e:
                session["errors"].append(f"Business rule extraction error: {str(e)}")
        
        # ========== PHASE 3: RISK ASSESSMENT ==========
        if analysis_type in ["risk_assessment", "full_analysis"] and MIGRATION_RISK_AVAILABLE:
            try:
                risk_assessor = MigrationRiskAssessor()
                analysis_data = session["results"].get("business_rules", {})
                risk_assessment = risk_assessor.assess_risks(analysis_data)
                session["results"]["risk_assessment"] = risk_assessment
            except Exception as e:
                session["errors"].append(f"Risk assessment error: {str(e)}")
        
        # ========== PHASE 4: MODERNIZATION STRATEGIES ==========
        if analysis_type in ["modernization", "full_analysis"] and MODERNIZATION_AVAILABLE:
            try:
                strategy_recommender = ModernizationStrategyRecommender()
                biz_rules = session["results"].get("business_rules", {})
                risk_data = session["results"].get("risk_assessment", {})
                strategies = strategy_recommender.recommend_strategies(biz_rules, risk_data)
                session["results"]["modernization_strategies"] = strategies
            except Exception as e:
                session["errors"].append(f"Modernization strategy error: {str(e)}")
        
        # ========== PHASE 5: GENERATE SUMMARY ==========
        total_rules = len(all_business_rules) + session["results"].get("business_rules", {}).get("total_rules_extracted", 0)
        
        session["results"]["summary"] = {
            "total_files": len(session["files"]),
            "total_business_rules_extracted": total_rules,
            "analysis_type": analysis_type,
            "modules_executed": {
                "groq_analysis": GROQ_CLIENT_AVAILABLE,
                "cobol_analyzer": COBOL_ANALYZER_AVAILABLE,
                "business_rule_extractor": BUSINESS_RULE_EXTRACTOR_AVAILABLE,
                "risk_assessment": MIGRATION_RISK_AVAILABLE,
                "modernization_strategy": MODERNIZATION_AVAILABLE
            },
            "completion_time": datetime.now().isoformat()
        }
        
        # Generate report
        generate_comprehensive_report(session_id)
        
        session["status"] = "completed"
        session["end_time"] = datetime.now().isoformat()
        
        logger.info(f"✅ Analysis completed for session {session_id}")
        logger.info(f"   Files: {len(session['files'])}")
        logger.info(f"   Business rules extracted: {total_rules}")
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {traceback.format_exc()}")
        session["status"] = "failed"
        session["error"] = str(e)

def generate_comprehensive_report(session_id: str):
    """Generate detailed JSON report"""
    session = sessions.get(session_id)
    if not session:
        return
    
    report = {
        "project": "GenAI Legacy Code Understanding & Risk Analyzer",
        "session_info": {
            "session_id": session_id,
            "analysis_type": session["analysis_type"],
            "start_time": session["start_time"],
            "end_time": session.get("end_time"),
            "status": session["status"]
        },
        "analysis_results": session["results"],
        "metrics": {
            "files_analyzed": len(session["files"]),
            "business_rules_extracted": session["results"].get("summary", {}).get("total_business_rules_extracted", 0),
            "risk_score": session["results"].get("risk_assessment", {}).get("overall_risk_score", 0),
            "recommended_strategies": len(session["results"].get("modernization_strategies", {}).get("strategies", []))
        },
        "errors": session.get("errors", [])
    }
    
    report_file = os.path.join(REPORTS_DIR, f"{session_id}.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    session["report_file"] = report_file

@app.get("/results/{session_id}")
async def show_results(request: Request, session_id: str):
    """Display analysis results with template"""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Return the template with session data
    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "session_id": session_id,
            "session_data": session
        }
    )

@app.get("/api/results/{session_id}")
async def get_results_api(session_id: str):
    """API endpoint for results"""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return JSONResponse(session)

@app.get("/download/{session_id}")
async def download_report(session_id: str):
    """Download analysis report"""
    session = sessions.get(session_id)
    if not session or "report_file" not in session:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if not os.path.exists(session["report_file"]):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    return FileResponse(
        session["report_file"],
        media_type='application/json',
        filename=f"legacy_analysis_report_{session_id}.json"
    )

@app.get("/api/status")
async def api_status():
    """API status check"""
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "modules": {
            "groq_client": GROQ_CLIENT_AVAILABLE,
            "cobol_analyzer": COBOL_ANALYZER_AVAILABLE,
            "business_rule_extractor": BUSINESS_RULE_EXTRACTOR_AVAILABLE,
            "migration_risk": MIGRATION_RISK_AVAILABLE,
            "modernization_strategy": MODERNIZATION_AVAILABLE
        },
        "sessions_active": len([s for s in sessions.values() if s["status"] == "processing"]),
        "sessions_completed": len([s for s in sessions.values() if s["status"] == "completed"])
    }

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint"""
    return {
        "message": "API is working",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)