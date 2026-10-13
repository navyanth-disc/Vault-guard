"""
ai/state.py
Google Gemini Native Tool Schemas and Session Management
Defines FunctionDeclarations for native tool calling with zero third-party frameworks.
"""

from google.genai import types

def get_vaultguard_tools() -> list[types.Tool]:
    """Returns Google Gemini Native Tool declarations for function calling."""
    return [
        types.Tool(
            function_declarations=[
                types.FunctionDeclaration(
                    name="calculate_loan_emi",
                    description="Calculates exact monthly EMI, total interest, and total payable amount for loans.",
                    parameters=types.Schema(
                        type="OBJECT",
                        properties={
                            "principal": types.Schema(type="NUMBER", description="Loan principal amount in INR"),
                            "annual_rate_pct": types.Schema(type="NUMBER", description="Annual interest rate percentage (e.g. 8.5)"),
                            "tenure_years": types.Schema(type="INTEGER", description="Tenure in years (e.g. 15)")
                        },
                        required=["principal", "annual_rate_pct", "tenure_years"]
                    )
                ),
                types.FunctionDeclaration(
                    name="calculate_collateral_ltv",
                    description="Calculates maximum permissible loan based on 65% LTV bank policy against collateral valuation.",
                    parameters=types.Schema(
                        type="OBJECT",
                        properties={
                            "property_valuation": types.Schema(type="NUMBER", description="Assessed property valuation in INR"),
                            "requested_loan": types.Schema(type="NUMBER", description="Requested loan amount in INR"),
                            "ltv_cap_pct": types.Schema(type="NUMBER", description="Policy LTV cap percentage (default 65.0)")
                        },
                        required=["property_valuation", "requested_loan"]
                    )
                )
            ]
        )
    ]
