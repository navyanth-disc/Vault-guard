# Scalability, Performance & Cost Optimization Guide

This knowledge file establishes production-grade non-functional requirements (NFRs) for Google Cloud Run serverless deployments.

---

## 1. Latency Budgeting & SLOs

| Tier | Component | Target Latency | Method |
| :--- | :--- | :---: | :--- |
| **Tier 0** | Zero-Compute Gateway Guardrail | $\le 1.0\text{ ms}$ | Token set intersection & regex boundaries. |
| **Tier 1** | PII Sanitization | $\le 5.0\text{ ms}$ | Regex scanning / Google Cloud DLP API. |
| **Tier 2** | Deterministic Python Tools | $\le 0.5\text{ ms}$ | Pure compiled Python math calculations. |
| **Tier 3** | Local RAG Corpus Retrieval | $\le 25.0\text{ ms}$ | Lexical & semantic scoring over 415 chunks. |
| **Tier 4** | Gemini 1.5 Flash Reasoning | $\le 800.0\text{ ms}$ | Sub-second multimodal token generation. |
| **Total** | **End-to-End p95 Latency** | **$< 1000\text{ ms}$** | **Sub-second SLA for live loan underwriting.** |

---

## 2. Serverless Google Cloud Run Scalability

* **Region**: `asia-south1` (Mumbai) for minimal data transit latency to Indian banking branches.
* **Concurrency**: 80 concurrent requests per container instance (`--concurrency=80`).
* **Autoscaling**: Scale from 0 to 10 instances on-demand (`--min-instances=0 --max-instances=10`).
* **Zero Idle Cost**: When no loan officers are querying the copilot, compute scales to zero, incurring **$0.00 idle cost**.

---

## 3. Cost Per Successful Task (CPST) Formula

$$\text{Cost per Successful Task} = \frac{\sum(\text{Input Tokens} \times C_{\text{in}} + \text{Output Tokens} \times C_{\text{out}} + \text{Cloud Run CPU Seconds} \times C_{\text{compute}})}{\text{Total Completed Underwriting Decisions}}$$

* **Token Optimization**:
  * Zero-compute guardrails reject off-topic spam queries before any tokens are billed.
  * Hierarchical parent-child chunking injects only relevant 400-char snippets, saving up to 80% on prompt token costs.
  * Single container serving both UI and API eliminates cross-origin network hops and egress bandwidth charges.
