# Agentic System Design & Multi-Turn Orchestration Guide

This knowledge file establishes the system design principles for Google Native Multi-Turn AI Agents.

---

## 1. Single-Platform Google Native Agent Topology

```
User Query / Deed PDF
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. GATEWAY ZERO-COMPUTE GUARDRAIL (<1ms)                    │
│    • Word-boundary token matching                           │
│    • Adversarial prompt-injection filter                    │
└──────────────────────────────┬──────────────────────────────┘
                               │ Allowed
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. ZERO-TRUST PII SANITIZATION                              │
│    • Google Cloud DLP (dlp_v2)                              │
│    • Indian PAN & 12-digit Aadhaar Tokenization             │
└──────────────────────────────┬──────────────────────────────┘
                               │ Sanitized
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. GEMINI 1.5 FLASH NATIVE AGENT (client.chats.create)      │
│    • Multi-Turn Session Memory (indexed by session_id)      │
│    • Native Tool Function Declarations                      │
└──────────────┬──────────────────────────────┬───────────────┘
               │ Tool Call                    │ Direct Text
               ▼                              ▼
┌─────────────────────────────┐ ┌─────────────────────────────┐
│ 4. DETERMINISTIC TOOLS      │ │ 5. REGULATORY RAG RETRIEVAL │
│    • calculate_loan_emi     │ │    • 545KB RBI Corpus       │
│    • calculate_collateral_ltv│ │    • Abstention on 0-score  │
└──────────────┬──────────────┘ └─────────────┬───────────────┘
               │ Observation Result           │ Verified Citation
               └──────────────┬───────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. RESPONSE SYNTHESIS & REAL-TIME LLMOPS TELEMETRY          │
│    • Streams Answer + Latency (ms) + Route Tier + PII status│
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Multi-Turn Session Memory Standards

* **Session Isolation**: Each user session is keyed by a unique `session_id`. Conversations from different branch officers must never contaminate each other.
* **Turn Retention**:
  * Turn 1: *"I want to apply for a 50 Lakhs loan against my property."*
  * Turn 2: *"What if the interest rate is 8.5% for 15 years?"*
  * The agent must retain the principal amount from Turn 1 when calculating the monthly EMI in Turn 2.
* **Production Persistence**: In-memory dictionary for local development; Google Cloud Firestore for serverless multi-instance production.

---

## 3. Human-in-the-Loop Credit Underwriting Policy

1. **AI as Advisor, Human as Approver**:
   The AI copilot generates the structured Underwriting Decision Card (Valuation, 65% LTV Cap, Monthly EMI), but the Bank Branch Loan Officer clicks the final credit approval button.
2. **Deterministic Mathematical Authority**:
   The LLM is strictly prohibited from doing mental math on compound interest. All numbers must originate from verified Python functions.
