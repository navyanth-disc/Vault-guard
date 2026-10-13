"""
ai/guardrail.py
Production-Grade Zero-Compute Intent & Prompt-Injection Guardrail (<1ms)
Enforces:
1. Strict whole-word token matching (Zero substring leakage like 'hi' in 'something').
2. Pure greeting vs mixed intent discrimination.
3. Prompt injection & jailbreak detection.
4. Domain intent whitelisting (Banking, Credit, RBI, Underwriting).
"""

import re
import time

BANKING_INTENTS = {
    "account", "loan", "loans", "lending", "lender", "borrower", "borrowing",
    "emi", "interest", "balance", "card", "credit", "debit", "deposit", "transfer",
    "kyc", "branch", "collateral", "deed", "mortgage", "valuation", "ltv",
    "underwriting", "policy", "policies", "circular", "circulars", "rbi", "rate", "rates",
    "bank", "banking", "property", "tenure", "foir", "amortization", "advance",
    "advances", "npa", "sarfaesi", "eblr", "mclr", "repo", "psl", "cibil",
    "foreclosure", "prepayment", "penalty", "encumbrance", "exposure", "threshold",
    "finance", "financing", "risk", "priority", "guideline", "guidelines", "norm", "norms",
    "compliance", "regulatory", "commercial", "statutory", "solvency", "capital"
}

# Strict standalone greetings (matched as whole words only)
STANDALONE_GREETINGS = {"hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"}

# Adversarial prompt injection keywords
ADVERSARIAL_PATTERNS = [
    r"ignore (all )?(previous|prior) (instructions|prompts)",
    r"show (me )?(the )?system prompt",
    r"you are now (in )?dan mode",
    r"act as an unfiltered",
    r"reveal (your )?secret"
]

# Restricted entities and topics with no link to credit underwriting or loan collateral
RESTRICTED_NON_BANKING_ENTITIES = {
    "pm", "prime", "minister", "ministers", "modi", "president", "cabinet",
    "election", "elections", "parliament", "politics", "political", "politician",
    "politicians", "mp", "mla", "party", "bjp", "congress", "cricket", "bollywood",
    "cinema", "movie", "movies", "actor", "actress", "horoscope", "astrology",
    "weather", "recipe", "iphone", "samsung", "android"
}

def evaluate_guardrail(query: str) -> tuple[bool, float, str]:
    """
    Evaluates if query belongs to banking/underwriting domain.
    Returns: (is_allowed, latency_ms, reason)
    """
    t0 = time.perf_counter()
    q_clean = query.strip().lower()
    
    # 1. Adversarial Injection Check (<0.1ms)
    for pattern in ADVERSARIAL_PATTERNS:
        if re.search(pattern, q_clean):
            latency_ms = round((time.perf_counter() - t0) * 1000, 3)
            return False, latency_ms, "REJECTED_ADVERSARIAL_INJECTION"
            
    # Tokenize query into distinct whole words
    words = re.findall(r'\b[a-z0-9]+\b', q_clean)
    word_set = set(words)
    
    # 2. Pure Greeting Check (Only if query is EXCLUSIVELY a greeting, e.g. "Hi", "Hello")
    if word_set.issubset({"hello", "hi", "hey", "good", "morning", "afternoon", "evening", "there", "greetings"}):
        latency_ms = round((time.perf_counter() - t0) * 1000, 3)
        return True, latency_ms, "ALLOWED_PURE_GREETING"
        
    # 3. Access Restriction: Strictly Reject Political Offices & Non-Banking Entities (<0.1ms)
    # VaultGuard is strictly scoped to credit underwriting, loan collateral, and RBI prudential directives.
    matched_restricted = word_set.intersection(RESTRICTED_NON_BANKING_ENTITIES)
    if matched_restricted:
        latency_ms = round((time.perf_counter() - t0) * 1000, 3)
        return False, latency_ms, f"REJECTED_OUT_OF_SCOPE_RESTRICTED:{list(matched_restricted)[:3]}"
        
    # 4. Domain Intent Intersection
    matched_intents = word_set.intersection(BANKING_INTENTS)
    latency_ms = round((time.perf_counter() - t0) * 1000, 3)
    
    if matched_intents:
        return True, latency_ms, f"ALLOWED_BANKING_INTENT:{list(matched_intents)[:3]}"
    else:
        # Off-topic reject: "i love dummy", "something i love dummy", "recipe for cake"
        return False, latency_ms, "REJECTED_OFF_TOPIC"

