import io
from typing import List
from PIL import Image
import pytesseract
from PyPDF2 import PdfReader


def extract_text_from_file(uploaded_file) -> str:
    """Extract text from an uploaded file supporting PDF and images."""
    if uploaded_file is None:
        return ""
    # Streamlit uploaded file exposes file type
    file_type = getattr(uploaded_file, "type", "")
    try:
        if file_type == "application/pdf" or uploaded_file.name.lower().endswith(".pdf"):
            reader = PdfReader(uploaded_file)
            text_parts = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(text_parts)
        else:
            image = Image.open(uploaded_file)
            return pytesseract.image_to_string(image)
    except Exception:
        try:
            content = uploaded_file.read()
            uploaded_file.seek(0)
            return content.decode("utf-8", errors="ignore")
        except Exception:
            return ""


def extract_text_from_files(files: List) -> str:
    """Extract and concatenate text from multiple uploaded files."""
    texts = []
    for f in files or []:
        text = extract_text_from_file(f)
        if text:
            texts.append(text)
    return "\n".join(texts)
