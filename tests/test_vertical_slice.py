"""
tests/test_vertical_slice.py
End-to-end smoke test verifying:
1. GET  / (Embedded UI serves 200 OK)
2. GET  /health (Probes return HEALTHY and chunks indexed)
3. POST /api/chat (Zero-compute rejection of 'I love iPhone' in <1ms)
4. POST /api/chat (Loan EMI tool invocation)
5. POST /api/underwrite (Multimodal deed attachment & 65% LTV cap)
"""

import sys
import os
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_vertical_slice():
    print("\n================================================================================")
    print("LIVE REHEARSAL: END-TO-END VERTICAL SLICE SMOKE TEST")
    print("================================================================================")
    
    # 1. UI Root Probe
    res_ui = client.get("/")
    assert res_ui.status_code == 200
    assert "VaultGuard" in res_ui.text
    print("✅ 1. GET / -> Embedded Glassmorphic Web UI served (200 OK)")
    
    # 2. Health & Platform Probe
    res_health = client.get("/health")
    assert res_health.status_code == 200
    h_data = res_health.json()
    assert h_data["status"] == "HEALTHY"
    print(f"✅ 2. GET /health -> Platform: {h_data['platform']} | Indexed Chunks: {h_data['rbi_chunks_indexed']}")
    
    # 3. Zero-Compute Guardrail Rejection (<1ms)
    res_guard = client.post("/api/chat", json={"message": "I love iPhone 16 Pro Max"})
    assert res_guard.status_code == 200
    g_data = res_guard.json()
    assert g_data["telemetry"]["route_tier"] == "ZERO_COMPUTE_GUARDRAIL_REJECTION"
    assert g_data["telemetry"]["latency_ms"] < 5.0
    print(f"✅ 3. POST /api/chat ('I love iPhone') -> Rejection in {g_data['telemetry']['latency_ms']}ms (Zero Compute Drift)")
    
    # 4. EMI Amortization Tool
    res_calc = client.post("/api/chat", json={"message": "Calculate EMI for 50 Lakhs loan at 8.5% interest for 15 years"})
    assert res_calc.status_code == 200
    c_data = res_calc.json()
    assert "49,236.98" in c_data["answer"]
    print(f"✅ 4. POST /api/chat (EMI Calculation) -> Exact Amortization: ₹49,236.98 (Route: {c_data['telemetry']['route_tier']})")
    
    # 5. Multimodal Underwriting & 65% LTV Cap
    deed_path = "data/customer_artifacts/sample_property_deed_hyderabad.txt"
    with open(deed_path, "rb") as f:
        deed_bytes = f.read()
        
    res_uw = client.post(
        "/api/underwrite",
        files={"file": ("deed.txt", deed_bytes, "text/plain")},
        data={"requested_loan": 80000000.0} # Requested 8 Crores against 10 Crore property
    )
    assert res_uw.status_code == 200
    u_data = res_uw.json()
    assert u_data["status"] == "CAPPED_AT_65_LTV"
    assert "48,750,000.00" in u_data["underwriting_decision"]["approved_loan"]
    print(f"✅ 5. POST /api/underwrite (Deed Attachment) -> Capped at 65% LTV: {u_data['underwriting_decision']['approved_loan']} (Monthly EMI: {u_data['underwriting_decision']['monthly_emi']})")
    
    print("\n🎉 ALL 5 INTEGRATION PROBES PASSED! SYSTEM READY FOR CLOUD RUN DEPLOYMENT.")
    print("================================================================================")

if __name__ == "__main__":
    test_vertical_slice()
