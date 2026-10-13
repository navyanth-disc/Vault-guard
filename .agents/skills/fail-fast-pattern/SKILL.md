---
name: fail-fast-pattern
description: >-
  Implements the Fail Fast & Pre-heat initialization pattern for any pipeline or
  server. Use when setting up database connections, loading ML models, or initializing
  heavy resources. Ensures infrastructure failures crash immediately at startup, not
  after expensive processing.
---

# Fail Fast & Pre-heat Pattern Skill

## The Problem

```python
# BAD: Lazy initialization — crashes LATE
def process_document(text):
    client = QdrantClient(...)        # What if Qdrant is down?
    embedder = load_model(...)         # What if the model is missing?
    vector = embedder.embed(text)      # You already processed the PDF for nothing
    client.upsert(vector)              # Crash HERE, after 30 seconds of work
```

## The Solution

```python
# GOOD: Fail Fast — crashes EARLY
# Module-level initialization (runs once at import time)
_client = QdrantClient(...)            # Crashes NOW if Qdrant is down
_embedder = load_model(...)            # Crashes NOW if model is missing

def process_document(text):
    vector = _embedder.embed(text)     # Pre-loaded, fast
    _client.upsert(vector)             # Pre-connected, fast
```

## Instructions

### When To Apply This Pattern

Apply Fail Fast when your code depends on ANY of these:
- **Database connections** (Qdrant, PostgreSQL, Redis, MongoDB)
- **ML model loading** (Embedding models, LLMs, rerankers)
- **API clients** (external services, cloud APIs)
- **File system paths** (config files, data directories)

### Implementation Rules

1. **Initialize at module level** (top of the file, outside any function):
   ```python
   _client = DatabaseClient(host=cfg["host"], port=cfg["port"])
   _model = load_heavy_model(cfg["model_name"])
   ```

2. **Use underscore prefix** (`_variable`) to signal "private, don't import directly":
   ```python
   _qdrant_client = QdrantClient(...)    # Private: use via search() function
   ```

3. **Load config FIRST**, then initialize everything from it:
   ```python
   # 1. Load config
   with open("config/settings.yaml") as f:
       cfg = yaml.safe_load(f)
   
   # 2. Initialize from config
   _client = Client(host=cfg["host"])
   _model = Model(name=cfg["model"])
   ```

4. **Order matters** — initialize dependencies before dependents:
   ```python
   _client = QdrantClient(...)           # 1. Database first
   _collection = cfg["collection_name"]   # 2. Config second
   _embedder = get_embedder()             # 3. Models third
   ```

### The Pipeline Pattern

For orchestrator/pipeline files, do setup BEFORE processing:

```python
def run_pipeline():
    # === FAIL FAST ZONE (crash here, not later) ===
    client = connect_to_database()
    verify_collection_exists(client)
    model = load_embedding_model()
    
    # === PROCESSING ZONE (safe to proceed) ===
    for file in get_input_files():
        data = load(file)
        result = model.process(data)
        client.store(result)
```

### Benefits

| Aspect | Without Fail Fast | With Fail Fast |
|---|---|---|
| **When errors appear** | After expensive processing | Immediately at startup |
| **Performance** | Models reloaded every call | Models loaded once, reused |
| **Debugging** | "Why did it crash at step 47?" | "Qdrant isn't running" |
| **Resource usage** | Wasteful (load/unload cycle) | Efficient (singleton pattern) |
