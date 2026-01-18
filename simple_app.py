from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
import os
import shutil
import uuid
import json
from typing import List

app = FastAPI(title="Legacy Code Analyzer")

# Create directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("reports", exist_ok=True)

@app.get("/")
def home():
    return HTMLResponse("""
    <html>
        <head><title>Legacy Analyzer</title></head>
        <body>
            <h1>GenAI Legacy Code Analyzer</h1>
            <form action="/analyze" method="post" enctype="multipart/form-data">
                <input type="file" name="files" multiple><br><br>
                <button type="submit">Analyze</button>
            </form>
        </body>
    </html>
    """)

@app.post("/analyze")
async def analyze(files: List[UploadFile] = File(...)):
    session_id = str(uuid.uuid4())
    session_dir = f"uploads/{session_id}"
    os.makedirs(session_dir, exist_ok=True)
    
    results = []
    
    for file in files:
        # Save file
        file_path = os.path.join(session_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Read file
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(5000)
        
        # Simple analysis
        results.append({
            "filename": file.filename,
            "size": len(content),
            "analysis": f"File contains {len(content.split())} words"
        })
    
    return JSONResponse({
        "session_id": session_id,
        "results": results,
        "message": "Analysis complete"
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)