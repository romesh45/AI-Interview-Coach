import os

def extract_text_from_pdf(file_path: str) -> dict:
    """Extract text from a PDF file using pypdf."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += (page.extract_text() or "")

        text = text.strip()
        if not text:
            return {"error": "PDF appears to be empty or contains only images. "
                             "Please paste your resume text instead."}
        return {"text": text}

    except ImportError:
        return {"error": "PDF parsing library not available. "
                         "Please paste your resume text instead."}
    except Exception as e:
        return {"error": f"Failed to read PDF: {str(e)}"}
