"""
rag/loader.py
Loads official regulatory circulars from data/rbi_regulatory_corpus/
and provides multimodal text extraction for live PDF/TXT file uploads.

100% Google Cloud Native Priority:
1. Google Gemini 1.5 Flash Native Multimodal Token Processing (types.Part.from_bytes).
2. Optional local dev fallback (pdfplumber if available).
3. Universal standard library byte decoding (Zero external dependency requirement).
"""

import os
import io
import glob

def extract_text_from_bytes(file_bytes: bytes, filename: str) -> str:
    """
    Extracts text content from uploaded PDF or TXT bytes.
    Prioritizes 100% Native Google Gemini 1.5 Flash multimodal inspection.
    """
    fname_lower = filename.lower()
    
    if fname_lower.endswith(".pdf"):
        # 1. Native Google Cloud Gemini 1.5 Flash Multimodal Extraction (Zero 3rd-party OCR)
        if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or os.environ.get("GCP_PROJECT_ID"):
            try:
                from google import genai
                from google.genai import types
                client = genai.Client()
                pdf_part = types.Part.from_bytes(data=file_bytes, mime_type="application/pdf")
                response = client.models.generate_content(
                    model="gemini-1.5-flash-002",
                    contents=[
                        pdf_part,
                        "Extract and return the full text content of this regulatory document verbatim. Output pure text only."
                    ]
                )
                if response.text and len(response.text.strip()) > 50:
                    return response.text.strip()
            except Exception:
                pass

        # 2. Local Python Library Fallback (if installed in dev environment)
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                extracted_pages = []
                for idx, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        extracted_pages.append(f"--- Page {idx+1} ---\n{page_text}")
                if extracted_pages:
                    return "\n\n".join(extracted_pages)
        except Exception:
            pass

    # 3. Universal Python Standard Library decoding
    return file_bytes.decode("utf-8", errors="ignore")

def load_regulatory_corpus(corpus_dir: str = "data/rbi_regulatory_corpus") -> list[dict]:
    """Loads all text circulars and acts with metadata."""
    corpus_files = glob.glob(os.path.join(corpus_dir, "*.txt"))
    documents = []
    
    for filepath in sorted(corpus_files):
        filename = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
            
        documents.append({
            "source": filename,
            "path": filepath,
            "char_count": len(text),
            "content": text
        })
        
    return documents
