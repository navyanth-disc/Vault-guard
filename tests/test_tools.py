"""
tests/test_tools.py
Verifies deterministic math:
1. Loan EMI calculation exact amortization (No LLM token guessing).
2. Collateral LTV cap calculation at 65%.
3. FOIR debt-to-income servicing capacity.
"""

import sys
import os
sys.path.insert(0, os.path.abspath("."))

from ai.tools.loan_calculator import calculate_loan_emi
from ai.tools.underwriting_rules import calculate_collateral_ltv, calculate_foir_eligibility

def test_loan_emi():
    print("\n--- TEST: Loan EMI Deterministic Math ---")
    # 50 Lakhs at 8.5% for 15 years
    res = calculate_loan_emi(principal=5000000.0, annual_rate_pct=8.5, tenure_years=15)
    print(f"50L @ 8.5% for 15 yrs -> Monthly EMI: ₹{res['monthly_emi']:,.2f} | Total Interest: ₹{res['total_interest']:,.2f}")
    assert abs(res['monthly_emi'] - 49236.98) < 0.05, f"Expected 49236.98, got {res['monthly_emi']}"
    assert res['tenure_months'] == 180
    print("✅ PASS: Compound amortization math verified.")

def test_ltv_cap():
    print("\n--- TEST: 65% LTV Bank Policy Enforcement ---")
    # Case A: 1 Crore valuation, 80 Lakhs requested -> Should be capped at 65 Lakhs
    res_a = calculate_collateral_ltv(property_valuation=10000000.0, requested_loan=8000000.0, ltv_cap_pct=65.0)
    print(f"Valuation: ₹1 Cr | Requested: ₹80L -> Approved: ₹{res_a['approved_loan']:,.2f} | Status: {res_a['status']}")
    assert res_a['approved_loan'] == 6500000.0
    assert res_a['status'] == "CAPPED_AT_65_LTV"
    
    # Case B: 1 Crore valuation, 50 Lakhs requested -> Should be approved in full
    res_b = calculate_collateral_ltv(property_valuation=10000000.0, requested_loan=5000000.0, ltv_cap_pct=65.0)
    print(f"Valuation: ₹1 Cr | Requested: ₹50L -> Approved: ₹{res_b['approved_loan']:,.2f} | Status: {res_b['status']}")
    assert res_b['approved_loan'] == 5000000.0
    assert res_b['status'] == "APPROVED"
    print("✅ PASS: 65% LTV policy cap verified.")

def test_foir():
    print("\n--- TEST: 50% FOIR Income Assessment ---")
    # 1.5 Lakhs net monthly income, 25k existing EMIs -> Max total = 75k, capacity = 50k
    res = calculate_foir_eligibility(net_monthly_income=150000.0, existing_emis=25000.0, foir_cap_pct=50.0)
    print(f"Income: ₹1.5L | Existing EMI: ₹25k -> Available EMI Capacity: ₹{res['available_emi_capacity']:,.2f}")
    assert res['available_emi_capacity'] == 50000.0
    assert res['status'] == "ELIGIBLE"
    print("✅ PASS: FOIR debt servicing capacity verified.")

if __name__ == "__main__":
    test_loan_emi()
    test_ltv_cap()
    test_foir()
