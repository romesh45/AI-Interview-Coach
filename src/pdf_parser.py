import os

def extract_text_from_pdf(file_path: str) -> dict:
    """Extract text from a PDF file using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()

        text = text.strip()
        if not text:
            return {"error": "PDF appears to be empty or contains only images. Please paste your resume text instead."}

        return {"text": text}

    except ImportError:
        return {"error": "PDF parsing library not available. Please paste your resume text instead."}
    except Exception as e:
        return {"error": f"Failed to read PDF: {str(e)}"}
