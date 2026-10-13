"""
ai/tools/underwriting_rules.py
Deterministic Credit Underwriting Policy Rules
Enforces statutory RBI & Bank Policy:
- 65% LTV Cap on collateral property valuation
- 50% FOIR (Fixed Obligation to Income Ratio) on customer net income
"""

def calculate_collateral_ltv(property_valuation: float, requested_loan: float, ltv_cap_pct: float = 65.0) -> dict:
    """
    Enforces bank lending policy: Maximum loan allowed is 65% of verified collateral valuation.
    """
    max_permissible_loan = round(property_valuation * (ltv_cap_pct / 100.0), 2)
    requested_ltv_pct = round((requested_loan / property_valuation) * 100.0, 2)
    is_eligible = requested_loan <= max_permissible_loan
    approved_loan = min(requested_loan, max_permissible_loan)
    
    return {
        "property_valuation": property_valuation,
        "requested_loan": requested_loan,
        "approved_loan": approved_loan,
        "max_permissible_loan": max_permissible_loan,
        "requested_ltv_pct": requested_ltv_pct,
        "policy_ltv_cap_pct": ltv_cap_pct,
        "status": "APPROVED" if is_eligible else "CAPPED_AT_65_LTV"
    }

def calculate_foir_eligibility(net_monthly_income: float, existing_emis: float, foir_cap_pct: float = 50.0) -> dict:
    """
    Enforces FOIR cap: Maximum total monthly debt servicing cannot exceed 50% of net income.
    """
    max_total_emi = round(net_monthly_income * (foir_cap_pct / 100.0), 2)
    available_emi_capacity = max(0.0, round(max_total_emi - existing_emis, 2))
    
    return {
        "net_monthly_income": net_monthly_income,
        "existing_emis": existing_emis,
        "max_total_allowed_emi": max_total_emi,
        "available_emi_capacity": available_emi_capacity,
        "foir_cap_pct": foir_cap_pct,
        "status": "ELIGIBLE" if available_emi_capacity > 0 else "OVER_LEVERAGED"
    }
