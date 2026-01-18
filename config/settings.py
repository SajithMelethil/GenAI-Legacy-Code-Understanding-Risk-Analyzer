import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Groq API Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    
    # Use llama-3.1-8b-instant as default
    GROQ_MODEL = "llama-3.1-8b-instant"
    
    # Application Settings
    APP_NAME = "GenAI Legacy Code Understanding & Risk Analyzer"
    VERSION = "1.0.0"
    
    # File Processing
    SUPPORTED_EXTENSIONS = {
        '.cobol', '.cbl', '.cob',  # COBOL
        '.java', '.jar',  # Java
        '.py', '.pyc',    # Python
        '.c', '.cpp', '.h', '.hpp',  # C/C++
        '.cs',    # C#
        '.vb', '.vbs',  # Visual Basic
        '.txt'          # Text files
    }

settings = Settings()