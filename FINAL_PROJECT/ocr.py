import easyocr
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
import os

def pdf_has_text(pdf_path):
    """Check if the PDF contains extractable text."""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text = page.extract_text()
            if text and text.strip():
                return True
        return False
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return False

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using PyPDF2 or easyOCR if needed."""
    """
    Extract text and metadata from each page of a PDF. If a page has no extractable text, use easyOCR.
    Returns a list of dicts: [{"page": int, "text": str, "metadata": dict}, ...]
    """
    results = []
    try:
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                page_text = text
                used_ocr = False
            else:
                # Use easyOCR if no text
                images = convert_from_path(pdf_path, dpi=300, first_page=i+1, last_page=i+1)
                ocr_reader = easyocr.Reader(['en'])
                image_path = f"temp_page_{i+1}.png"
                images[0].save(image_path, "PNG")
                ocr_result = ocr_reader.readtext(image_path, detail=0, paragraph=True)
                page_text = "\n".join(ocr_result)
                os.remove(image_path)
                used_ocr = True
            # Example metadata extraction (customize as needed)
            metadata = {
                "page_number": i+1,
                "is_starting_page": i == 0,
                "document_type": "unknown",  # Placeholder, can use heuristics/LLM
                "document_id": os.path.basename(pdf_path),
                "used_ocr": used_ocr
            }
            results.append({"page": i+1, "text": page_text, "metadata": metadata})
        return results
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return []