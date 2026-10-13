# Enterprise AI Test Architecture: Metrics & Evaluation Guide

This knowledge file establishes the testing standards for RAG and Agentic Copilots. All developer agents must write tests conforming to these metrics.

---

## 1. The 5 Quality Pillars of AI Testing

```
┌────────────────────────────────────────────────────────────────────────┐
│                        AI QUALITY TEST PYRAMID                         │
├────────────────────────────────────────────────────────────────────────┤
│ Level 4: Production & Non-Functional  (Latency, Cost, Throughput)      │
│ Level 3: End-to-End Workflow & Agent  (Task Success, State, Tools)    │
│ Level 2: Component Integration        (RAG Recall, Re-ranking, DLP)    │
│ Level 1: Unit & Gate Invariants       (Guardrails <1ms, Deterministic) │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. RAG Retrieval Quality Metrics

| Metric | Mathematical Definition | Acceptance Threshold | Failure Mode |
| :--- | :--- | :---: | :--- |
| **Recall@K** | $\frac{|\text{Relevant Chunks} \cap \text{Top K}|}{|\text{Total Relevant Chunks}|}$ | $\ge 0.90$ | Required policy evidence missing from retrieved context. |
| **Precision@K** | $\frac{|\text{Relevant Chunks} \cap \text{Top K}|}{K}$ | $\ge 0.80$ | Too much noise/distractor chunks occupying prompt budget. |
| **Abstention Accuracy** | $\frac{|\text{Ungrounded Queries Refused}|}{|\text{Total Ungrounded Queries}|}$ | **$1.00$ (100%)** | AI hallucinates an answer when evidence is absent from corpus. |
| **MRR (Mean Reciprocal Rank)** | $\frac{1}{|Q|}\sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$ | $\ge 0.85$ | Ground truth document ranks low down the retrieved list. |
| **Context Relevance** | Ratio of token overlap to retrieved chunk length | $\ge 0.35$ | Spurious single-word substring false positive matching. |

---

## 3. Answer Quality & Groundedness Metrics

* **Faithfulness / Groundedness**: Every claim in the generated answer must be mathematically or semantically attributable to the supplied context.
* **Citation Accuracy**: Citations must point to the specific regulatory circular and clause (e.g., `RBI/2024-25/11 Section 3(a)`).
* **Zero Hallucination Guarantee**: If evidence is missing, the system **must abstain**:
  > *"I cannot find sufficient evidence in the official RBI Regulatory Corpus to substantiate an answer for this query. As an enterprise banking copilot, I abstain from guessing policy rules."*

---

## 4. Agent Behavior & Orchestration Metrics

* **Tool-Selection Accuracy ($\ge 0.95$)**: The agent selects `calculate_loan_emi` for repayments and `calculate_collateral_ltv` for deed valuation.
* **Tool Argument Accuracy ($\ge 0.98$)**: Extracted parameters match verified numeric values (e.g., float principle in INR, tenure in years).
* **Deterministic Execution Rate ($100\%$)**: All compound interest and LTV caps are evaluated via exact Python math, zero probabilistic token guessing.
* **Loop / Cycle Rate ($0\%$)**: The agent must terminate in $\le 3$ steps and never enter recursive tool-calling loops.

---

## 5. Security, Guardrails & Trust Boundaries

* **Zero-Compute Gateway Rejection ($\le 1.0\text{ms}$)**: Off-topic queries ("I love iPhone", "recipe for pizza", "something i love dummy") must be rejected via token intersection before invoking Gemini.
* **Direct Prompt-Injection Resistance ($100\%$)**: Adversarial bypass attempts ("Ignore all prior instructions", "DAN mode") are immediately intercepted.
* **Sensitive Data (PII) Leakage Rate ($0\%$)**: Indian PAN (`[A-Z]{5}[0-9]{4}[A-Z]{1}`) and 12-digit Aadhaar (`\b[2-9]{1}[0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b`) must be redacted before logging or embedding.
