"""
RecruitAI - Resume Parser
===========================
Extracts plain text from an uploaded resume file (.pdf, .docx, or .txt)
so it can be fed straight into the AI matching engine.
"""

import os


def extract_text_from_resume(file_path: str) -> str:
    """Dispatches to the right extractor based on file extension.
    Raises ValueError for unsupported file types."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return _extract_pdf(file_path)
    elif ext == ".docx":
        return _extract_docx(file_path)
    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported resume file type: {ext}. Please upload a PDF, DOCX, or TXT file.")


def _extract_pdf(file_path: str) -> str:
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        raise RuntimeError("PyPDF2 is not installed. Run: pip install PyPDF2")

    reader = PdfReader(file_path)
    text_parts = []
    for page in reader.pages:
        text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts).strip()


def _extract_docx(file_path: str) -> str:
    try:
        import docx
    except ImportError:
        raise RuntimeError("python-docx is not installed. Run: pip install python-docx")

    doc = docx.Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs).strip()


ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def is_allowed_resume_file(filename: str) -> bool:
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS
