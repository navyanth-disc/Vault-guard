"""
tests/test_gcp_dlp.py
Proves that Indian PAN and 12-digit Aadhaar are sanitized before logging or embedding.
"""

import sys
import os
sys.path.insert(0, os.path.abspath("."))

from rag.sanitizer import sanitize_pii

def test_pan_and_aadhaar_masking():
    sample_text = (
        "Applicant Rajesh Kumar, PAN Card: ABCPR1234F, "
        "Aadhaar Number: 4921 8832 9014, applying for home loan of INR 50,00,000."
    )
    
    print("\n--- TEST: Zero-Trust PII Masking (PAN & Aadhaar) ---")
    sanitized, count, method = sanitize_pii(sample_text)
    print(f"Original:  {sample_text}")
    print(f"Sanitized: {sanitized}")
    print(f"Masked Count: {count} | Method: {method}")
    
    assert "ABCPR1234F" not in sanitized, "PAN was NOT masked!"
    assert "4921 8832 9014" not in sanitized, "Aadhaar was NOT masked!"
    assert "[INDIA_PAN_CARD_MASKED]" in sanitized
    assert "[INDIA_AADHAAR_MASKED]" in sanitized
    assert count == 2
    print("✅ PASS: PII successfully sanitized without data leakage.")

if __name__ == "__main__":
    test_pan_and_aadhaar_masking()
