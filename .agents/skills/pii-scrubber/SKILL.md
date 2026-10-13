---
name: pii-scrubber
description: >-
  Integrates Microsoft Presidio for PII detection and anonymization in text
  processing pipelines. Use when handling personal data, building GDPR/CCPA
  compliant systems, or sanitizing documents before embedding into vector databases.
---

# PII Scrubber Skill (Microsoft Presidio)

This skill adds PII (Personally Identifiable Information) detection and
anonymization to any text pipeline using Microsoft Presidio.

## Why PII Scrubbing Matters

If you embed documents containing names, emails, and phone numbers into a vector
database, that PII becomes **searchable** — which violates privacy laws (GDPR, CCPA).

```
Before: "Contact John Smith at john.smith@bank.com or 555-1234"
After:  "Contact <PERSON> at <EMAIL_ADDRESS> or <PHONE_NUMBER>"
```

The `<PERSON>` tags preserve semantic context without exposing real identities.

## Instructions

### Step 1: Install Dependencies

```bash
pip install presidio-analyzer presidio-anonymizer
python -m spacy download en_core_web_lg    # NLP model for entity detection
```

### Step 2: Initialize Engines (Module Level — Fail Fast)

```python
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# Heavy NLP models — load ONCE at module level
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()
```

### Step 3: Detect & Anonymize

```python
from typing import List, cast
from presidio_anonymizer.entities import RecognizerResult

def scrub_pii(text: str) -> str:
    """Detects and replaces PII entities with generic tags."""
    
    # Detect PII
    results = analyzer.analyze(
        text=text,
        entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER"],
        language="en"
    )
    
    # Replace detected PII with tags
    anonymized = anonymizer.anonymize(
        text=text,
        analyzer_results=cast(List[RecognizerResult], results)
    )
    
    return anonymized.text
```

### Supported Entity Types

| Entity | What It Detects | Replacement |
|---|---|---|
| `PERSON` | Names ("John Smith") | `<PERSON>` |
| `EMAIL_ADDRESS` | Emails ("john@bank.com") | `<EMAIL_ADDRESS>` |
| `PHONE_NUMBER` | Phone numbers ("555-1234") | `<PHONE_NUMBER>` |
| `CREDIT_CARD` | Card numbers | `<CREDIT_CARD>` |
| `US_SSN` | Social Security Numbers | `<US_SSN>` |
| `LOCATION` | Addresses, cities | `<LOCATION>` |
| `DATE_TIME` | Dates and times | `<DATE_TIME>` |

### Step 4: Add to Your Pipeline

```python
# In your preprocessing step:
clean_text = scrub_pii(raw_text)
doc_hash = hashlib.sha256(clean_text.encode()).hexdigest()
```

**Note:** Always hash AFTER scrubbing. This ensures two copies of the same document
with different names still produce the same hash (deduplication works correctly).

## Common Gotcha

The `cast()` call is required because Presidio's analyzer returns a slightly
different type than what the anonymizer expects. `cast()` is a no-op at runtime —
it only satisfies the type checker.
