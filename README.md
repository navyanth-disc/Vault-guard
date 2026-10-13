# VaultGuard — Enterprise Credit Underwriting & Compliance Copilot

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Google Cloud Run](https://img.shields.io/badge/Google%20Cloud-Run%20(asia--south1)-4285F4.svg?logo=google-cloud&logoColor=white)](https://cloud.google.com/run)
[![Gemini 1.5 Flash](https://img.shields.io/badge/Gemini-1.5%20Flash-8E75C2.svg?logo=google&logoColor=white)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**VaultGuard** is an enterprise AI credit underwriting and regulatory compliance copilot designed for bank branch loan officers and credit underwriters. It combines deterministic financial arithmetic, statutory Reserve Bank of India (RBI) regulatory retrieval (RAG), multimodal property deed appraisal, and zero-trust PII masking into a unified, serverless application.

---

## 🌟 Key Architecture & Capabilities

1. **Sub-Millisecond Gateway Guardrail (`<0.5ms`)**
   - High-throughput whole-word set containment check that enforces strict domain authorization.
   - Rejects prompt injections, off-topic requests, and political offices (e.g., PM, elections) before tokens hit the LLM.

2. **Deterministic Financial Arithmetic (API over Probabilistic Token Prediction)**
   - Mathematical calculations (Compound Interest, Monthly EMI, FOIR eligibility) are delegated to Python math tools rather than probabilistic LLM token prediction.
   - Enforces statutory **65% Loan-to-Value (LTV)** policy caps and **50% Fixed Obligation to Income Ratio (FOIR)** debt servicing limits.

3. **Multimodal Collateral Deed Underwriting**
   - Direct extraction of property valuations, encumbrance status, and ownership records from uploaded sale deed documents (PDF/TXT).
   - Instant computation of maximum permissible loan sanctions and amortization schedules.

4. **Statutory RBI Regulatory Retrieval (RAG with TTL Cache)**
   - Ingests authentic RBI Master Circulars (Housing Finance, IRACP 90-day NPA norms, KYC Directions, EBLR floating benchmark rates, SARFAESI Act, and Priority Sector Lending).
   - In-memory TTL query cache with real-time hit/miss ratio tracking.
   - Clean, complete sentence synthesis citing official statutory directives (100% Abstention SLA on ungrounded queries).

5. **Zero-Trust PII Masking**
   - Redacts sensitive Indian Identity tokens (PAN Card: `[A-Z]{5}[0-9]{4}[A-Z]{1}` and 12-digit Aadhaar: `\b[2-9]{1}[0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b`) prior to indexing or session storage.

6. **Self-Contained Glassmorphic Web UI & Admin Control Plane**
   - Served directly by FastAPI at `GET /` with zero Node.js/npm build steps.
   - Includes real-time LLMOps telemetry metrics (latencies, cache hits, PII redactions) and a live regulatory document ingestion drawer.

---

## 🏛️ Repository Structure

```
vault-guard/
├── .agents/                        # 5-Layer Cognitive Agent Brain & Rules
│   ├── AGENTS.md                   # Core rules, 100% GCP mandate & squad roles
│   ├── STATE.md                    # Real-time architectural snapshot
│   ├── CHANGELOG.md                # Chronological build & action history
│   └── skills/                     # 11 Specialized On-Demand Skills
├── ai/
│   ├── guardrail.py                # Zero-Compute Gateway Guardrail (<1ms)
│   ├── state.py                    # Gemini Native Tool Declarations
│   └── tools/
│       ├── loan_calculator.py      # Compound Interest & EMI Amortization Math
│       └── underwriting_rules.py   # Collateral LTV Verification (65% Cap) & FOIR
├── app/
│   ├── main.py                     # Unified FastAPI Engine & Glassmorphic UI
│   └── schemas.py                  # Pydantic Request & Response Models
├── data/
│   ├── rbi_regulatory_corpus/      # Scraped authentic RBI Master Circulars & Acts
│   └── customer_artifacts/         # Sample property sale deeds for underwriting
├── rag/
│   ├── chunker.py                  # Hierarchical chunker with web-noise scrubber
│   ├── loader.py                   # Corpus & multimodal text extractor
│   ├── retriever.py                # Hybrid Regulatory Retriever with TTL cache
│   └── sanitizer.py                # Zero-Trust PII Sanitizer (Regex & Cloud DLP)
├── tests/
│   ├── test_vertical_slice.py      # End-to-End smoke rehearsal
│   ├── test_guardrail.py           # Guardrail refusal & latency verification
│   ├── test_rag.py                 # Statutory citation retrieval accuracy
│   ├── test_tools.py               # Deterministic EMI & LTV mathematical unit tests
│   ├── test_gcp_dlp.py             # PII masking verification
│   └── test_ai_architecture_metrics.py # Senior Test Architect 20-metric test suite
├── requirements.txt                # Pinned Python dependencies
└── .gitignore                      # Git exclusion rules
```

---

## 🚀 Quickstart & Local Installation

### Prerequisites
- Python 3.12 (or Python 3.10+)
- Virtual environment tool (`venv`)

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/<your-username>/vault-guard.git
cd vault-guard

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment (Optional for Cloud Run / Gemini Features)

```bash
export GEMINI_API_KEY="your-gemini-api-key"
export GCP_PROJECT_ID="your-gcp-project-id"
```

*(Note: VaultGuard executes gracefully offline in local development with deterministic calculations, regex PII sanitization, and statutory chunk formulation even without API keys.)*

### 3. Run the Application

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser at: **[http://localhost:8000](http://localhost:8000)**

---

## 🧪 Running the Test Suite

Run all verification test suites:

```bash
# End-to-end smoke rehearsal
python tests/test_vertical_slice.py

# Complete 20-metric Senior Test Architect suite
python tests/test_ai_architecture_metrics.py

# Domain guardrail tests
python tests/test_guardrail.py

# Deterministic financial arithmetic tools
python tests/test_tools.py

# RAG regulatory retrieval tests
python tests/test_rag.py
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves embedded Glassmorphic Web UI & Admin Drawer |
| `GET` | `/health` | Liveness probe, active sessions, and indexed chunk count |
| `POST` | `/api/chat` | Credit Underwriting copilot with tool routing & guardrail |
| `POST` | `/api/underwrite` | Multimodal collateral deed appraisal & 65% LTV cap |
| `GET` | `/api/admin/metrics` | Real-time LLMOps telemetry (p50/p95 latency, cache stats) |
| `POST` | `/api/admin/ingest` | Ingest new RBI circular (PDF/TXT) and dynamically re-index |
| `POST` | `/api/admin/purge-cache` | Purge in-memory TTL query cache |
| `POST` | `/api/admin/policy` | Dynamically update bank LTV and FOIR policy caps |

---

## 🔒 Security & Compliance Mandates

- **Zero Third-Party APIs:** 100% native Google Cloud Platform architecture.
- **Strict Domain Guardrails:** Rejects non-banking, adversarial, and political inquiries.
- **PII Protection:** Indian PAN and Aadhaar tokens are sanitized before logs or storage.
- **Deterministic Math:** LLM token prediction is strictly decoupled from financial interest/LTV arithmetic.

---

## 📄 License

This project is licensed under the MIT License.
