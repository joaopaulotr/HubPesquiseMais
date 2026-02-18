import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
    
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "100"))
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    
    # GPT Settings
    GPT_MAX_TOKENS = int(os.getenv("GPT_MAX_TOKENS", "500"))
    GPT_MAX_TOKENS_VIDEO = int(os.getenv("GPT_MAX_TOKENS_VIDEO", "700"))
    GPT_MAX_INPUT_CHARS = int(os.getenv("GPT_MAX_INPUT_CHARS", "3000"))
    GPT_MAX_INPUT_CHARS_VIDEO = int(os.getenv("GPT_MAX_INPUT_CHARS_VIDEO", "2000"))
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
    OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
    
    ALLOW_ORIGINS = ["http://localhost:5173", "http://localhost:3000", "http://localhost:8080"]

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
