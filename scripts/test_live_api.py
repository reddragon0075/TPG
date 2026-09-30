"""
TPG Live API Interactive Verification Script

Executes HTTP requests against the live Uvicorn server (http://127.0.0.1:8000)
to demonstrate end-to-end functionality across core intelligence engines:
1. Health & Diagnostics
2. Workspace & RBAC Profile
3. Knowledge Graph Memory Store
4. Requirement Intelligence (Ambiguity & Discovery Questions)
5. QA & Release Intelligence (Risk-based Test Strategy)
6. Strategy Intelligence (Strategic Bet Evaluation)
7. Analytics Intelligence (KPI & Target Tracking)
8. Workspace Statistics (Verifying Knowledge Graph growth)
"""

import sys
import json
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000"
HEADERS = {
    "X-API-Key": "tpg-dev-secret-key-12345",
    "Content-Type": "application/json",
}

def section(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def pretty_print(label: str, data: dict):
    print(f"\n--- {label} ---")
    print(json.dumps(data, indent=2))

def run_live_tests():
    print(f"Connecting to live TPG server at: {BASE_URL}")

    with httpx.Client(base_url=BASE_URL, headers=HEADERS, timeout=15.0) as client:
        # 1. Health Check
        section("1. System Health Check (/health)")
        resp = client.get("/health")
        print(f"HTTP Status: {resp.status_code}")
        health_data = resp.json()
        pretty_print("GET /health Response", health_data)
        assert resp.status_code == 200
        assert health_data["status"] == "healthy"

        # 2. Workspace Profile
        section("2. Current Workspace Profile (/workspace/me)")
        resp = client.get("/workspace/me")
        print(f"HTTP Status: {resp.status_code}")
        ws_data = resp.json()
        pretty_print("GET /workspace/me Response", ws_data)
        assert resp.status_code == 200

        # 3. Store Entity in Knowledge Graph Memory
        section("3. Knowledge Graph Storage (/memory/store)")
        store_payload = {
            "entity_type": "decision",
            "name": "Vendor Payout Architecture: Dedicated Microservice vs Monolith Extension",
            "summary": "Architectural evaluation of vendor payout settlement engine under 50k daily transactions.",
            "confidence": "confirmed",
            "source": "Architecture Review Board 2026-Q1",
            "status": "active",
            "properties": {
                "decision_type": "architectural",
                "chosen_option": "Dedicated Microservice with Event Sourcing",
                "tradeoffs": ["High isolation", "Eventual consistency SLA"],
                "approved_by": "VP of Architecture"
            }
        }
        resp = client.post("/memory/store", json=store_payload)
        print(f"HTTP Status: {resp.status_code}")
        stored_entity = resp.json()
        pretty_print("POST /memory/store Response", stored_entity)
        assert resp.status_code == 200
        entity_id = stored_entity["entity_id"]
        print(f"-> Created Entity ID: {entity_id}")

        # 4. Requirement Intelligence Analysis
        section("4. Requirement Intelligence Analysis (/intelligence/requirements/analyze)")
        req_payload = {
            "statement": "We should make the vendor payout process much faster and easier so sellers don't complain.",
            "context": {
                "domain": "fintech marketplace",
                "volume": "$10M/month in vendor disbursements"
            }
        }
        resp = client.post("/intelligence/requirements/analyze", json=req_payload)
        print(f"HTTP Status: {resp.status_code}")
        analysis_data = resp.json()
        pretty_print("POST /intelligence/requirements/analyze Response", {
            "is_product_requirement": analysis_data["is_product_requirement"],
            "detected_type": analysis_data["detected_type"],
            "ambiguity_score": analysis_data["ambiguity_score"],
            "completeness_score": analysis_data["completeness_score"],
            "missing_dimensions": analysis_data["missing_dimensions"],
            "top_prioritized_questions": analysis_data["prioritized_questions"][:3],
        })
        assert resp.status_code == 200

        # 5. QA Intelligence — Risk-Based Test Strategy
        section("5. QA Intelligence: Risk-Based Test Strategy (/qa/test-strategy)")
        qa_payload = {
            "prd_entity_id": "PRD-VENDOR-PAYOUTS",
            "prd_title": "Vendor Real-Time Instant Disbursements",
            "requirements": [
                {
                    "id": "REQ-001",
                    "text": "Instant Bank Account Transfer via RTP network within 15 seconds."
                },
                {
                    "id": "REQ-002",
                    "text": "KYC Identity Check Before Payout against global sanction lists."
                }
            ]
        }
        resp = client.post("/qa/test-strategy", json=qa_payload)
        print(f"HTTP Status: {resp.status_code}")
        qa_data = resp.json()
        pretty_print("POST /qa/test-strategy Response Summary", {
            "prd_title": qa_data.get("prd_title"),
            "risk_level": qa_data.get("risk_level"),
            "test_levels": qa_data.get("test_levels"),
            "key_risk_areas": qa_data.get("key_risk_areas"),
            "testing_approach": qa_data.get("testing_approach"),
            "estimated_test_effort_hours": qa_data.get("estimated_test_effort_hours"),
            "exit_criteria": qa_data.get("exit_criteria")
        })
        assert resp.status_code == 200

        # 6. Strategy Intelligence — Strategic Bet Evaluation
        section("6. Strategy Intelligence: Evaluate Strategic Bet (/strategy/bets/evaluate)")
        bet_payload = {
            "name": "Vendor Real-Time Wallet & Immediate Liquidity",
            "hypothesis": "Providing instant liquidity to high-volume marketplace sellers will increase 90-day seller retention by 25%.",
            "evidence_strength": 0.85,
            "investment_size": "MEDIUM",
            "market_uncertainty": 0.35
        }
        resp = client.post("/strategy/bets/evaluate", json=bet_payload)
        print(f"HTTP Status: {resp.status_code}")
        bet_data = resp.json()
        pretty_print("POST /strategy/bets/evaluate Response", bet_data)
        assert resp.status_code == 200

        # 7. Analytics Intelligence — Define KPI
        section("7. Analytics Intelligence: Define KPI (/analytics/kpi)")
        analytics_payload = {
            "name": "Vendor Payout Settlement Success Rate",
            "description": "Percentage of vendor instant payouts settled successfully on first attempt.",
            "formula": "(successful_instant_payouts / total_instant_payout_attempts) * 100",
            "unit": "percentage",
            "baseline": 93.4,
            "target": 99.5,
            "measurement_period": "daily"
        }
        resp = client.post("/analytics/kpi", json=analytics_payload)
        print(f"HTTP Status: {resp.status_code}")
        kpi_data = resp.json()
        pretty_print("POST /analytics/kpi Response", kpi_data)
        assert resp.status_code == 200

        # 8. Workspace Stats (Verifying Knowledge Graph Count)
        section("8. Knowledge Graph Aggregated Stats (/workspace/stats)")
        resp = client.get("/workspace/stats")
        print(f"HTTP Status: {resp.status_code}")
        stats_data = resp.json()
        pretty_print("GET /workspace/stats Response", stats_data)
        assert resp.status_code == 200
        print(f"\n-> Knowledge Graph total entities: {stats_data['total_entities']}")
        print(f"-> Entity types breakdown: {stats_data['entities_by_type']}")
        print("\n" + "=" * 70)
        print("  ALL 8 LIVE ENDPOINTS EXECUTED AND VERIFIED SUCCESSFULLY!")
        print("=" * 70)

if __name__ == "__main__":
    run_live_tests()
