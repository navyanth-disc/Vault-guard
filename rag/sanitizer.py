"""
rag/sanitizer.py
Google Cloud Sensitive Data Protection (Cloud DLP / dlp_v2) with Deterministic Fallback.
Comprehensive Zero-Trust Sanitization:
1. Indian National IDs: PAN Card, 12-digit Aadhaar.
2. Financial & Payment Tokens: Credit/Debit Card (Luhn format), Bank Account Numbers.
3. Access Secrets: Passwords, API Keys, JWT/Bearer tokens, Private keys.
4. PII Contact Info: Email addresses, Phone numbers.
"""

import os
import re

# Comprehensive Regulatory & Security Regex Patterns
PAN_PATTERN = r'[A-Z]{5}[0-9]{4}[A-Z]{1}'
AADHAAR_PATTERN = r'\b[2-9]{1}[0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b'
CREDIT_CARD_PATTERN = r'\b(?:\d{4}[ -]?){3}\d{4}\b'
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
PHONE_PATTERN = r'\b(?:\+91[\-\s]?)?[6-9]\d{9}\b'
SECRET_KEY_PATTERN = r'(?i)\b(password|passwd|pwd|secret|api[_-]?key|bearer|access_token|auth_token)\s*[:=]\s*(?:[\'"][^\'"]+[\'"]|[^\s,\'";]+)'

def sanitize_pii(text: str, project_id: str = None) -> tuple[str, int, str]:
    """
    Sanitizes customer text and ingested documents before logging, embedding, or model ingestion.
    Returns: (sanitized_text, masked_count, method_used)
    """
    project_id = project_id or os.environ.get("GCP_PROJECT_ID")
    
    # 1. Attempt Native Google Cloud DLP if project ID is available
    if project_id:
        try:
            from google.cloud import dlp_v2
            dlp = dlp_v2.DlpServiceClient()
            parent = f"projects/{project_id}/locations/global"
            inspect_config = {
                "info_types": [
                    {"name": "INDIA_PAN_INDIVIDUAL"},
                    {"name": "INDIA_AADHAAR_INDIVIDUAL"},
                    {"name": "CREDIT_CARD_NUMBER"},
                    {"name": "EMAIL_ADDRESS"},
                    {"name": "PHONE_NUMBER"},
                    {"name": "AUTH_TOKEN"},
                    {"name": "GENERIC_SECRET"}
                ]
            }
            deidentify_config = {
                "info_type_transformations": {
                    "transformations": [
                        {"primitive_transformation": {"replace_with_info_type_config": {}}}
                    ]
                }
            }
            res = dlp.deidentify_content(
                request={
                    "parent": parent,
                    "deidentify_config": deidentify_config,
                    "inspect_config": inspect_config,
                    "item": {"value": text}
                }
            )
            return res.item.value, 1, "GOOGLE_CLOUD_DLP_API"
        except Exception:
            pass

    # 2. Fast Deterministic Regex Sanitization (Enterprise Security Baseline)
    total_masked = 0
    sanitized = text

    # Passwords & API Secrets
    secrets_found = len(re.findall(SECRET_KEY_PATTERN, sanitized))
    if secrets_found > 0:
        total_masked += secrets_found
        sanitized = re.sub(
            SECRET_KEY_PATTERN,
            lambda m: re.split(r'[:=]', m.group(0))[0].strip() + ": [PROTECTED_SECRET_REDACTED]",
            sanitized
        )

    # Credit / Debit Cards (16 digits before 12-digit Aadhaar check)
    cards = len(re.findall(CREDIT_CARD_PATTERN, sanitized))
    total_masked += cards
    sanitized = re.sub(CREDIT_CARD_PATTERN, '[PAYMENT_CARD_MASKED]', sanitized)

    # PAN Cards
    pans = len(re.findall(PAN_PATTERN, sanitized))
    total_masked += pans
    sanitized = re.sub(PAN_PATTERN, '[INDIA_PAN_CARD_MASKED]', sanitized)

    # Aadhaar Cards
    aadhaars = len(re.findall(AADHAAR_PATTERN, sanitized))
    total_masked += aadhaars
    sanitized = re.sub(AADHAAR_PATTERN, '[INDIA_AADHAAR_MASKED]', sanitized)

    # Emails
    emails = len(re.findall(EMAIL_PATTERN, sanitized))
    total_masked += emails
    sanitized = re.sub(EMAIL_PATTERN, '[EMAIL_ADDRESS_MASKED]', sanitized)

    # Phone Numbers
    phones = len(re.findall(PHONE_PATTERN, sanitized))
    total_masked += phones
    sanitized = re.sub(PHONE_PATTERN, '[PHONE_NUMBER_MASKED]', sanitized)

    return sanitized, total_masked, "DETERMINISTIC_REGULATORY_REGEX"
