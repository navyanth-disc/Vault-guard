"""
rag/loader.py
Loads official regulatory circulars from data/rbi_regulatory_corpus/
and provides 100% Google Cloud Native multimodal text extraction for live PDF/TXT file uploads.

100% Google Cloud Native Architecture:
1. Google Gemini 2.5 Flash Native Multimodal Token Processing (types.Part.from_bytes) on Vertex AI.
2. Zero Third-Party OCR or PDF Libraries (Zero pdfplumber / PyPDF / Tesseract).
3. Universal standard library byte decoding fallback.
"""

import os
import io
import glob

def _get_genai_client():
    """Initializes 100% native Google GenAI Client with Vertex AI ADC support."""
    try:
        from google import genai
        project = os.environ.get("GCP_PROJECT_ID")
        location = os.environ.get("GCP_REGION", "asia-south1")
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            return genai.Client(api_key=api_key)
        if project:
            return genai.Client(vertexai=True, project=project, location=location)
        return genai.Client()
    except Exception:
        return None

def extract_text_from_bytes(file_bytes: bytes, filename: str) -> str:
    """
    Extracts text content from uploaded PDF or TXT bytes.
    100% Native Google Gemini 2.5 Flash multimodal inspection on Vertex AI.
    """
    fname_lower = filename.lower()
    
    if fname_lower.endswith(".pdf"):
        # 1. Native Google Cloud Gemini 2.5 Flash Multimodal Extraction (Zero 3rd-party OCR)
        client = _get_genai_client()
        if client:
            try:
                from google.genai import types
                pdf_part = types.Part.from_bytes(data=file_bytes, mime_type="application/pdf")
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        pdf_part,
                        "Extract and return the full text content of this regulatory document verbatim. Output pure text only."
                    ]
                )
                if response.text and len(response.text.strip()) > 50:
                    return response.text.strip()
            except Exception:
                pass

    # 2. Universal Python Standard Library decoding
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
