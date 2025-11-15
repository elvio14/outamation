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
        ocr_reader = easyocr.Reader(['en'])  # Move outside the loop
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                page_text = text
                used_ocr = False
            else:
                images = convert_from_path(pdf_path, dpi=300, first_page=i+1, last_page=i+1)
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

import gradio as gr

with gr.Blocks(title="PDF Processing App") as demo:
    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(label="Chat History", height=500)
            user_input = gr.Textbox(
                placeholder="Enter your RAG prompt here...",
                label="RAG Prompt Input"
            )
            send_btn = gr.Button("📤 Send")
            output_box = gr.Textbox(
                label="RAG/Chat Output",
                interactive=False,
                lines=10
            )
        with gr.Column(scale=1):
            pdf_input = gr.File(label="📄 Upload PDF", file_types=[".pdf"])
            process_btn = gr.Button("🔄 Process Document")
            clear_btn = gr.Button("🗑️ Clear Chat")

    # Store extracted text for chat context
    extracted_text_state = gr.State("")

    def process_pdf(file):
        if file is None:
            return gr.update(value="No file uploaded."), ""
        pages = extract_text_from_pdf(file.name)
        if not pages:
            return gr.update(value="Failed to process PDF."), ""
        # Compose a summary for the user and store all page data as state
        summary = f"PDF processed! {len(pages)} pages extracted.\n"
        for p in pages:
            meta = p['metadata']
            summary += f"Page {meta['page_number']} | Start: {meta['is_starting_page']} | Type: {meta['document_type']} | Used OCR: {meta['used_ocr']}\n"
        return gr.update(value=summary), pages

    def handle_chat(message, history, extracted_text):
        if not extracted_text:
            answer = "Please process a PDF first."
        elif isinstance(extracted_text, list):
            # Show metadata for each page as a mock RAG answer
            answer = "RAG Metadata per page:\n"
            for p in extracted_text:
                meta = p['metadata']
                answer += f"Page {meta['page_number']}: Start={meta['is_starting_page']}, Type={meta['document_type']}, Used OCR={meta['used_ocr']}\n"
            answer += "\nSample text from first page:\n" + (extracted_text[0]['text'][:500] if extracted_text[0]['text'] else "[No text]")
        else:
            answer = f"Extracted text (truncated): {str(extracted_text)[:500]}..."
        # Only update the output box, not the chatbot
        return answer

    process_btn.click(
        process_pdf,
        inputs=pdf_input,
        outputs=[user_input, extracted_text_state]
    )
    send_btn.click(
        handle_chat,
        inputs=[user_input, chatbot, extracted_text_state],
        outputs=output_box
    )
    user_input.submit(
        handle_chat,
        inputs=[user_input, chatbot, extracted_text_state],
        outputs=output_box
    )
    clear_btn.click(lambda: [], outputs=[chatbot])

demo.launch(debug=True)