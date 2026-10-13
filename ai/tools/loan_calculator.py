"""
ai/tools/loan_calculator.py
Deterministic Banking Amortization Calculator
Ensures exact monthly EMI, total interest, and total payable amounts.
Zero LLM token guessing.
"""

def calculate_loan_emi(principal: float, annual_rate_pct: float, tenure_years: int) -> dict:
    """
    Calculates deterministic monthly EMI, total interest, and total payable amount.
    Formula: EMI = [P x R x (1+R)^N] / [(1+R)^N - 1]
    """
    monthly_rate = (annual_rate_pct / 12) / 100.0
    months = tenure_years * 12
    
    # Standard compound amortization formula
    factor = (1.0 + monthly_rate) ** months
    emi = (principal * monthly_rate * factor) / (factor - 1.0)
    total_payable = emi * months
    total_interest = total_payable - principal
    
    return {
        "principal": principal,
        "annual_rate_pct": annual_rate_pct,
        "tenure_years": tenure_years,
        "tenure_months": months,
        "monthly_emi": round(emi, 2),
        "total_interest": round(total_interest, 2),
        "total_payable": round(total_payable, 2)
    }
