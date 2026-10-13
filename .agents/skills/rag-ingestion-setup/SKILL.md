---
name: rag-ingestion-setup
description: >-
  Step-by-step setup for a RAG ingestion pipeline with Qdrant, Ollama, SPLADE,
  and health-check verification. Use when building a document ingestion system,
  setting up a vector database, or preparing infrastructure for a RAG application.
---

# RAG Ingestion Setup Skill

This skill guides the setup and verification of the complete RAG ingestion
infrastructure: Qdrant (vector DB), Ollama (embeddings + LLM), and SPLADE
(sparse embeddings).

## Prerequisites

- Docker installed (for Qdrant)
- Ollama installed (https://ollama.com/download)
- Python 3.10+ with venv

## Instructions

### Step 1: Start Qdrant

```bash
docker run -d --name qdrant \
  -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

**Health check:**
```bash
curl -s http://localhost:6333/healthz
# Expected: "healthy" or similar 200 response
```

### Step 2: Pull Ollama Models

```bash
# Embedding model (768 dimensions)
ollama pull nomic-embed-text

# LLM brain (for agent, not ingestion)
ollama pull llama3.2:3b
```

**Health check:**
```bash
curl -s http://localhost:11434
# Expected: "Ollama is running"

ollama list
# Should show both models
```

### Step 3: Install Python Dependencies

```bash
pip install qdrant-client langchain-ollama fastembed pdfplumber \
            presidio-analyzer presidio-anonymizer langchain-text-splitters
```

### Step 4: Verify Full Stack

Run this verification script to confirm everything is connected:

```python
#!/usr/bin/env python3
"""RAG Infrastructure Health Check"""

def check_qdrant():
    from qdrant_client import QdrantClient
    client = QdrantClient(host="localhost", port=6333)
    collections = client.get_collections()
    print(f"✅ Qdrant: {len(collections.collections)} collections")

def check_ollama_embedding():
    from langchain_ollama import OllamaEmbeddings
    embedder = OllamaEmbeddings(model="nomic-embed-text")
    vec = embedder.embed_query("test")
    print(f"✅ Ollama Embedding: {len(vec)} dimensions")

def check_sparse_embedding():
    from fastembed import SparseTextEmbedding
    model = SparseTextEmbedding(model_name="prithivida/Splade_PP_en_v1")
    result = list(model.embed(["test"]))[0]
    print(f"✅ SPLADE: {len(result.indices)} non-zero terms")

def check_presidio():
    from presidio_analyzer import AnalyzerEngine
    analyzer = AnalyzerEngine()
    results = analyzer.analyze(text="John Smith", entities=["PERSON"], language="en")
    print(f"✅ Presidio: detected {len(results)} entities")

if __name__ == "__main__":
    print("🔍 Running RAG Infrastructure Health Check...\n")
    checks = [check_qdrant, check_ollama_embedding, check_sparse_embedding, check_presidio]
    
    for check in checks:
        try:
            check()
        except Exception as e:
            print(f"❌ {check.__name__}: {e}")
    
    print("\n🏁 Health check complete.")
```

### Step 5: Pipeline Architecture

Once infrastructure is verified, build the pipeline in this order:

```
1. loader_docs.py      → Extract text from PDFs (pdfplumber)
2. preprocessing.py    → Clean text + PII scrubbing + SHA-256 hashing
3. chunking.py         → Parent-Child semantic chunking
4. embedding.py        → Dense (Ollama) + Sparse (SPLADE) embeddings
5. vector_store.py     → Qdrant collection setup + upsert logic
6. ingestion_pipeline.py → Orchestrator (Fail Fast → Load → Process → Store)
```

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `Connection refused :6333` | Qdrant not running | `docker start qdrant` |
| `Connection refused :11434` | Ollama not running | Start Ollama app or `ollama serve` |
| `ModuleNotFoundError` | Package not in venv | `pip install <package>` in venv |
| `model not found` | Ollama model not pulled | `ollama pull nomic-embed-text` |
