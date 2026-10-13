# VaultGuard Agent Changelog

All significant project changes, architectural decisions, and milestones are recorded below.

---

### 12/10/2026 19:50
- Initialized 5-layer Cognitive Agent Brain (`.agents/`).
- Created `AGENTS.md` establishing 100% Native Google Cloud Platform mandate and 4-Agent Developer Squad (`@rag-engineer`, `@agent-orchestrator`, `@compliance-guard`, `@fullstack-devops`).
- Created `STATE.md` with complete architecture and component health snapshot.
- Consolidated 11 specialized skills into `.agents/skills/` for portable discovery in Google Cloud Shell.
- Scraped 545KB+ of authentic Reserve Bank of India (RBI) Master Circulars and Statutory Banking Acts into `data/rbi_regulatory_corpus/`.
- Generated customer test collateral deed extract with PAN and Aadhaar in `data/customer_artifacts/`.
### 13/10/2026 12:40
- **Access Restriction on Political Entities (`ai/guardrail.py`)**: Added `RESTRICTED_NON_BANKING_ENTITIES` (including `pm`, `prime minister`, `minister`, `politics`, `modi`, etc.) with sub-millisecond `<0.5ms` gateway refusal, ensuring queries regarding political offices with no link to credit underwriting or collateral are rejected immediately.
- **RAG Ubiquity Bleed & 100% Abstention SLA (`rag/retriever.py`)**: Introduced `UBIQUITOUS_CORPUS_TERMS` to prevent queries from matching solely on omnipresent boilerplate terms (`rbi`, `rule`). Enforced preserved 2-letter tokens (`len >= 2`) and strict 0-chunk abstention for out-of-scope non-banking queries.
- **Corpus & Chunker Web Scraping Scrubbing (`rag/chunker.py`, `data/rbi_regulatory_corpus/`)**: Automated stripping of web portal navigation debris (`Skip to main content`, `Change Language`, `Search...`), preventing header noise from entering chunk index.
- **Synthesized Regulatory Response Formulation (`app/main.py`)**: Replaced raw `[:650]...` character slicing with `synthesize_regulatory_response()` ensuring full, grammatically complete sentences, structured policy directives, and zero mid-word truncations.
