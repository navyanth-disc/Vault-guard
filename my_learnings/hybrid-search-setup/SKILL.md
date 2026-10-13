---
name: hybrid-search-setup
description: >-
  Sets up Hybrid Search with Dense + Sparse vectors, RRF fusion, and FlashRank
  reranking. Use when building a RAG retrieval pipeline, setting up Qdrant for
  semantic search, or implementing a two-stage retrieve-then-rerank system.
---

# Hybrid Search Setup Skill

This skill configures a production-grade retrieval pipeline that combines
Dense (semantic) and Sparse (keyword) search with reranking.

## Architecture Overview

```
User Query
    │
    ├──→ Dense Embedding (Nomic/Ollama, 768d) ──→ Qdrant "text-dense" prefetch
    │                                                        │
    ├──→ Sparse Embedding (SPLADE/FastEmbed)  ──→ Qdrant "text-sparse" prefetch
    │                                                        │
    │                                         ┌──────────────┘
    │                                         ▼
    │                                 RRF Fusion (merge both lists)
    │                                         │
    │                                         ▼
    │                              FlashRank Cross-Encoder Rerank
    │                                         │
    │                                         ▼
    └──────────────────────── Top N Documents returned
```

## Why Hybrid > Dense-Only

| Query Type | Dense (semantic) | Sparse (keyword) | Hybrid |
|---|---|---|---|
| "What's the lowest deposit?" | ✅ "lowest" ≈ "minimum" | ❌ No keyword match | ✅ |
| "SWIFT code BLR123" | ❌ Semantically vague | ✅ Exact keyword match | ✅ |
| General questions | ✅ | ✅ | ✅✅ |

## Instructions

### Step 1: Qdrant Collection with Named Vectors

```python
from qdrant_client.models import (
    VectorParams, Distance, SparseVectorParams, SparseIndexParams,
    ScalarQuantization, ScalarQuantizationConfig, ScalarType
)

client.create_collection(
    collection_name="my_collection",
    vectors_config={
        "text-dense": VectorParams(size=768, distance=Distance.COSINE)
    },
    sparse_vectors_config={
        "text-sparse": SparseVectorParams(
            index=SparseIndexParams(on_disk=False)
        )
    },
    quantization_config=ScalarQuantization(
        scalar=ScalarQuantizationConfig(
            type=ScalarType.INT8, quantile=0.99, always_ram=True
        )
    )
)
```

**Key decisions:**
- `Distance.COSINE` — standard for text embeddings (angle, not magnitude)
- `INT8` quantization — 75% RAM reduction with minimal quality loss
- `on_disk=False` for sparse — small enough to keep in RAM

### Step 2: Dual Embedding (Ingestion Time)

```python
from langchain_ollama import OllamaEmbeddings
from fastembed import SparseTextEmbedding

# Dense: semantic meaning
dense_embedder = OllamaEmbeddings(model="nomic-embed-text")
dense_vectors = dense_embedder.embed_documents(chunks)

# Sparse: keyword matching (SPLADE)
sparse_embedder = SparseTextEmbedding(model_name="prithivida/Splade_PP_en_v1")
sparse_vectors = list(sparse_embedder.embed(chunks))
```

**Important:** Use `embed_documents()` for ingestion, `embed_query()` for search.

### Step 3: Upsert with Both Vectors

```python
from qdrant_client.models import PointStruct, SparseVector

points = []
for dense, sparse, metadata in zip(dense_vectors, sparse_vectors, metadatas):
    points.append(PointStruct(
        id=str(uuid.uuid4()),
        vector={
            "text-dense": dense,
            "text-sparse": SparseVector(
                indices=sparse.indices.tolist(),
                values=sparse.values.tolist()
            )
        },
        payload=metadata   # Must include "text" key for retrieval
    ))

client.upsert(collection_name="my_collection", points=points, wait=True)
```

### Step 4: Hybrid Search with RRF Fusion

```python
from qdrant_client.models import Prefetch, FusionQuery, Fusion, SparseVector

results = client.query_points(
    collection_name="my_collection",
    prefetch=[
        Prefetch(query=dense_vector, using="text-dense", limit=top_k),
        Prefetch(
            query=SparseVector(indices=sparse.indices.tolist(),
                               values=sparse.values.tolist()),
            using="text-sparse", limit=top_k
        ),
    ],
    query=FusionQuery(fusion=Fusion.RRF),
    limit=top_k
)
```

**How RRF works:** If Doc A is ranked #1 by dense and #3 by sparse, its RRF score
is `1/(1+1) + 1/(1+3) = 0.75`. Documents appearing in BOTH lists score highest.

### Step 5: Rerank with FlashRank

```python
from flashrank import Ranker, RerankRequest

reranker = Ranker()  # Loads a Cross-Encoder model

passages = [{"id": p.id, "text": p.payload["text"]} for p in results.points]
reranked = reranker.rerank(RerankRequest(query=question, passages=passages))
top_docs = reranked[:3]  # Keep only the best 3
```

**Why rerank?** RRF is fast but rough (compares query and doc separately).
FlashRank is a Cross-Encoder — reads query AND document TOGETHER for precise scoring.

## Dependencies

```txt
qdrant-client>=1.9.0
langchain-ollama>=0.1.0
fastembed>=0.2.0
flashrank>=0.2.0
```
