"""
tests/test_rag.py
Verifies that RegulatoryRetriever accurately retrieves official RBI circulars.
"""

import sys
import os
sys.path.insert(0, os.path.abspath("."))

from rag.retriever import RegulatoryRetriever

def test_regulatory_retrieval():
    print("\n--- TEST: RBI Regulatory Knowledge Base Retrieval ---")
    retriever = RegulatoryRetriever()
    print(f"Total Chunks Indexed: {len(retriever.chunks)}")
    assert len(retriever.chunks) > 50, "Chunks index too small!"
    
    # Query 1: LTV & Housing finance
    query_1 = "Loan to Value LTV ratio quantum of housing loans"
    results_1, _ = retriever.retrieve(query_1, top_k=2)
    print(f"\nQuery: '{query_1}'")
    print(f"Top Hit: {results_1[0]['source']} (Score: {results_1[0]['score']})")
    assert "housing_finance" in results_1[0]["source"].lower()
    
    # Query 2: SARFAESI Act 60-day notice
    query_2 = "SARFAESI demand notice sixty days secured debt"
    results_2, _ = retriever.retrieve(query_2, top_k=2)
    print(f"\nQuery: '{query_2}'")
    print(f"Top Hit: {results_2[0]['source']} (Score: {results_2[0]['score']})")
    assert "sarfaesi" in results_2[0]["source"].lower()
    
    # Query 3: Floating rate prepayment foreclosure
    query_3 = "foreclosure charges prepayment penalty floating rate"
    results_3, _ = retriever.retrieve(query_3, top_k=2)
    print(f"\nQuery: '{query_3}'")
    print(f"Top Hit: {results_3[0]['source']} (Score: {results_3[0]['score']})")
    assert "interest_rate" in results_3[0]["source"].lower() or "housing" in results_3[0]["source"].lower()
    
    print("\n✅ PASS: Accurate statutory citation retrieval verified across RBI corpus.")

if __name__ == "__main__":
    test_regulatory_retrieval()
