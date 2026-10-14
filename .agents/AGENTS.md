# VaultGuard Project Rules & Cognitive Constitution

## 1. Project Identity & Mission
- **Project**: VaultGuard — Enterprise Credit Underwriting & Compliance Copilot
- **Track**: Track 3: App Builders (Agent-First Workflows)
- **Runtime**: Python 3.12 | Google Cloud Run (Serverless, region `asia-south1`)
- **Core Principle**: 100% Native Google Cloud Platform (Zero Third-Party Servers or APIs).

---

## 2. 100% Native Google Cloud Platform Mandate
Every agent working on this repository must strictly adhere to native Google Cloud services:
1. **Foundation Model**: Google Gemini 1.5 Flash (`gemini-1.5-flash-002`) via `google-genai` / Vertex AI.
2. **Multimodal Document Inspection**: Native Gemini 1.5 Flash PDF token processing via `types.Part.from_bytes` (Zero 3rd-party OCR).
3. **PII Masking & Compliance**: Google Cloud Sensitive Data Protection (`google-cloud-dlp` / `dlp_v2`) with regex fallback.
4. **Agent Tool Calling**: Gemini Native Function Calling (`google.genai.types.Tool`, `FunctionDeclaration`).
5. **State & Session Persistence**: Google Cloud Firestore (`google-cloud-firestore`) / in-memory session store.
6. **Object Vault**: Google Cloud Storage (`google-cloud-storage` - GCS).
7. **Serverless Deployment**: Google Cloud Run (`gcloud run deploy`) via Google Cloud Build (`--source .`).

---

## 3. The 4 Developer Agents Squad
Tasks are partitioned across 4 specialized agent roles to prevent code conflicts:

| Agent Role | Domain & Focus | Key Deliverables |
| :--- | :--- | :--- |
| **`@rag-engineer`** | RBI Regulatory Corpus ingestion, chunking, and semantic search. | `rag/loader.py`, `rag/chunker.py`, `rag/retriever.py` |
| **`@agent-orchestrator`** | Gemini Native Multi-Turn Agent, Function Calling (`client.chats.create`), and banking math tools. | `ai/state.py`, `ai/orchestrator.py`, `ai/tools/loan_calculator.py`, `ai/tools/underwriting_rules.py` |
| **`@compliance-guard`** | Multimodal PDF inspection, `<1ms` zero-compute guardrail, and Cloud DLP PII sanitization. | `ai/guardrail.py`, `rag/sanitizer.py`, `app/schemas.py` |
| **`@fullstack-devops`** | Glassmorphic Web UI, real-time telemetry streaming, Dockerfile, and Cloud Run deploy. | `app/main.py`, `Dockerfile`, `tests/test_vertical_slice.py` |

---

## 4. Engineering Rules & Best Practices

1. **Deterministic Financial Math**:
   - NEVER let the LLM calculate compound interest, EMI, or LTV ratios via probabilistic token guessing.
   - ALWAYS invoke deterministic Python math tools (`calculate_loan_emi`, `calculate_collateral_ltv`).
2. **Zero-Compute Gateway Guardrail**:
   - Block off-topic queries ("I love iPhone", general chitchat) at the gateway using set intersection (`<1ms`) before tokens reach Gemini.
3. **Zero-Trust PII Masking**:
   - Indian PAN (`[A-Z]{5}[0-9]{4}[A-Z]{1}`) and 12-digit Aadhaar (`\b[2-9]{1}[0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b`) MUST be sanitized before any logging or indexing.
4. **Self-Contained Glassmorphic UI**:
   - Web UI is served directly at `GET /` by FastAPI with zero Node.js / npm build requirements for maximum Cloud Run deployment reliability.
5. **Fail-Fast Initialization**:
   - Check Vertex AI credentials and Cloud DLP initialization at startup so misconfigurations crash early rather than during live client requests.

---

## 5. Known Gotchas & Lessons Learned (Zero-Tolerance Post-Mortem)

1. **Substring Guardrail Leakage Bug**:
   - *Failure*: `if any(g in q_lower for g in GREETING_INTENTS)` checked raw substrings, causing `"something i love dummy"` to match `"hi"` inside `"something"`, which bypassed domain guardrails.
   - *Fix & Law*: NEVER use substring matching for intents. Enforce `re.findall(r'\b[a-z0-9]+\b')` whole-word token extraction and set containment (`word_set.issubset(...)`).

2. **RAG Single-Token & Stopword Bleed**:
   - *Failure*: Sparse/dense retrieval matched generic English words or single tokens to random corpus documents.
   - *Fix & Law*: Enforce English stopword removal (`STOPWORDS`), query token coverage threshold ($\ge 35\%$), and minimum 2 distinct token matches for multi-word queries. If evidence is lacking, ALWAYS return 0 chunks (100% Abstention SLA).

3. **Conflation of Ingestion vs. Applicant Underwriting**:
   - *Failure*: Providing deed attachment (`📎`) for customer valuation while neglecting regulatory policy ingestion upload.
   - *Fix & Law*: The architecture strictly bifurcates **Customer Artifacts** (`POST /api/underwrite` -> property deed valuation) and **Regulatory Corpus** (`POST /api/admin/ingest` -> circular PDF/TXT chunking & live index extension). Both must have explicit, separate UI controls.

4. **Return Contract Consistency**:
   - *Failure*: Changing `retriever.retrieve` to return `(results, was_cache_hit)` broke unpack callers that expected a single list.
   - *Fix & Law*: Verify all call-sites and execute the automated test suite immediately upon modifying any public method signature.

5. **Container Build & GCP Sandbox Auth**:
   - Always ensure `requirements.txt` exists (`cp HYD_GEMINI_REQUIREMENTS.txt requirements.txt`) before running `gcloud run deploy --source .`.
   - In Google Cloud Shell / Cloud Run, use Application Default Credentials (ADC) without hardcoding secret keys.

6. **Universal Mobile & Cross-Device Responsiveness**:
   - *Failure*: Desktop-only fixed widths (e.g. 460px admin drawer, rigid header pills) caused layout breakages on mobile phone viewports.
   - *Fix & Law*: Implement universal responsive design with `100dvh`, `width: min(460px, 100vw)` drawers, horizontal-scroll telemetry headers, `16px` font inputs (prevents iOS auto-zoom), and `@media (max-width: 768px)` / `@media (max-width: 480px)` styles.

7. **Mother Brain (Gemini 1.5 Flash) Calibration & RAG Manipulation Immunity**:
   - *Failure*: Unfiltered conversational tokens ("know", "hey") manipulated RAG into matching "Know Your Customer" for city queries ("hey do you know Hyderabad rbi rules"), while uncalibrated Gemini client initialization timed out silently on Cloud Run.
   - *Fix & Law*:
     1. Treat conversational verbs (`know`, `knows`, `hey`, `hi`, `ask`, `check`) as stopwords to prevent RAG manipulation.
     2. Dynamically calibrate `get_gemini_client()` for Vertex AI ADC (`GOOGLE_CLOUD_PROJECT`, `asia-south1`) and `GEMINI_API_KEY`.
     3. Calibrate Gemini's system prompt with a strict relevance gate: abstain if the retrieved regulatory text does not address the officer's specific inquiry.
