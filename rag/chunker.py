"""
rag/chunker.py
Parent-Child Hierarchical Chunker
Creates:
- Parent chunks (1500 chars) for complete contextual understanding
- Child chunks (400 chars) for high-precision retrieval
"""

import re

WEB_BOILERPLATE_PATTERNS = [
    r'^Master Circulars\s*\|\s*Official Website.*$',
    r'^Master Directions\s*\|\s*Official Website.*$',
    r'^Master Directions\s*-\s*Reserve Bank of India.*$',
    r'^Skip to main content$',
    r'^Not Pressed$',
    r'^Change Language$',
    r'^हिंदी$',
    r'^Search the Website$',
    r'^Search$',
    r'^Home$',
    r'^Notifications$',
    r'^Master Circulars$',
    r'^Master Directions$',
    r'^\(\d+\s*kb\)$'
]

BOILERPLATE_REGEX = re.compile('|'.join(WEB_BOILERPLATE_PATTERNS), re.IGNORECASE)

def clean_text_content(text: str) -> str:
    """Removes web scraping artifacts and navigation debris from text while preserving paragraph breaks."""
    lines = text.splitlines()
    clean_lines = [line for line in lines if not (line.strip() and BOILERPLATE_REGEX.match(line.strip()))]
    cleaned = "\n".join(clean_lines)
    return re.sub(r'\n{3,}', '\n\n', cleaned)

def chunk_document(doc: dict, parent_size: int = 1500, child_size: int = 400) -> list[dict]:
    """Hierarchically splits document into parent chunks with clean, complete paragraphs."""
    content = clean_text_content(doc["content"])
    source = doc["source"]
    
    # Split by double-newlines (natural paragraphs)
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    
    chunks = []
    chunk_id = 0
    current_parent = ""
    
    for para in paragraphs:
        if len(current_parent) + len(para) < parent_size:
            current_parent += "\n\n" + para if current_parent else para
        else:
            if current_parent:
                chunk_id += 1
                chunks.append({
                    "chunk_id": f"{source}_{chunk_id}",
                    "source": source,
                    "text": current_parent,
                    "length": len(current_parent)
                })
            current_parent = para
            
    if current_parent:
        chunk_id += 1
        chunks.append({
            "chunk_id": f"{source}_{chunk_id}",
            "source": source,
            "text": current_parent,
            "length": len(current_parent)
        })
        
    return chunks
