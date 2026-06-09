import fitz  # PyMuPDF
from app.utils.logger import get_logger

logger = get_logger(__name__)

def parse_resume_pdf(file_path: str) -> str:
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        
        cleaned_text = " ".join(text.split())
        return cleaned_text
    except Exception as e:
        logger.error(f"Error reading PDF {file_path}: {e}")
        return ""