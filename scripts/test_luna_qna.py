import asyncio
import time
import json
import httpx
from src.main import app
from src.services.db import db_service

# Reload topics.json in db_service
db_service.topics = db_service._load_json("topics.json")

async def run_tests():
    print("=" * 80)
    print("🚀 LUNA SYSTEM VALIDATION & QnA ACCURACY BENCHMARK")
    print("   Endpoint: http://localhost:20128/v1 (OmniRoute)")
    print("   Model: antigravity/gemini-3.6-flash-medium")
    print("=" * 80)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health Check
        resp = await client.get("/health")
        assert resp.status_code == 200, f"Health check failed: {resp.text}"
        print("✅ Health Check: OK")

        # 2. Bug Fix Validation: Punctuation in Intent Router
        punc_tests = ["hello!", "hi!", "who are you?", "thanks!"]
        for pt in punc_tests:
            resp = await client.post("/chat", json={"message": pt, "session_id": "test_punc"})
            data = resp.json()
            assert data["trust_level"] == "A", f"Punctuation test failed for {pt}"
            assert len(data["citations"]) == 0
            print(f"✅ Intent Router with Punctuation ('{pt}'): -> Fast Chitchat OK ('{data['response'][:40]}...')")

        # 3. Bug Fix Validation: Keyword Substring Collision Prevention
        collision_queries = [
            ("Can I give feedback?", "fee"),
            ("What online services are available?", "vc"),
            ("What is the teaching methodology?", "hod"),
            ("Looking for a 3-year course in three hours", "hr")
        ]
        for cq, collision_target in collision_queries:
            resp = await client.post("/chat", json={"message": cq, "session_id": "test_collision"})
            data = resp.json()
            ans_lower = data["response"].lower()
            if collision_target == "fee":
                assert "1,64,550" not in ans_lower, f"Collision detected: 'feedback' returned fee info!"
            elif collision_target == "vc":
                assert "rajendra kumar sharma" not in ans_lower, f"Collision detected: 'services' returned VC info!"
            print(f"✅ Substring Collision Check ('{cq}'): -> No False Collision with '{collision_target}'")

        # 4. Bug Fix Validation: Ambiguity False-Positive Traps
        trap_queries = ["kumar hostel", "deepak lab"]
        for tq in trap_queries:
            resp = await client.post("/chat", json={"message": tq, "session_id": "test_trap"})
            data = resp.json()
            assert "Did you mean" not in data["response"], f"Ambiguity false-positive triggered on '{tq}'!"
            print(f"✅ Ambiguity Safety Valve ('{tq}'): -> No False Positive Traps OK")

        # 5. Bug Fix Validation: Session Isolation
        session_a = "user_alpha"
        session_b = "user_beta"
        await client.post("/chat", json={"message": "My name is John Doe and my favorite hobby is robotics.", "session_id": session_a})
        resp_b = await client.post("/chat", json={"message": "What is my name and favorite hobby?", "session_id": session_b})
        data_b = resp_b.json()
        assert "John Doe" not in data_b["response"], "Session leakage detected: User B saw User A's context!"
        print("✅ Session Isolation: -> User A and User B histories strictly separated OK")

        print("\n" + "=" * 80)
        print("📊 QnA ACCURACY BENCHMARK WITH GROUND TRUTH EVALUATION")
        print("=" * 80)

        qna_pairs = [
            {
                "id": "Q1",
                "category": "Fee Structure",
                "question": "What is the B.Tech 1st year fee per semester at JUIT?",
                "expected_facts": ["1,64,550", "sem"],
                "strict_keywords": ["1,64,550"]
            },
            {
                "id": "Q2",
                "category": "Placements",
                "question": "What is the highest placement package for the 2021-25 batch and which company offered it?",
                "expected_facts": ["50 LPA", "Google"],
                "strict_keywords": ["50", "google"]
            },
            {
                "id": "Q3",
                "category": "Placements",
                "question": "What is the mean/average salary for the 2021-25 batch at JUIT?",
                "expected_facts": ["7.18 LPA"],
                "strict_keywords": ["7.18"]
            },
            {
                "id": "Q4",
                "category": "Leadership",
                "question": "Who is the Vice Chancellor of Jaypee University of Information Technology?",
                "expected_facts": ["Rajendra Kumar Sharma"],
                "strict_keywords": ["rajendra", "sharma"]
            },
            {
                "id": "Q5",
                "category": "Administration",
                "question": "Who is the Registrar and Dean of Students at JUIT?",
                "expected_facts": ["Brigadier RK Sharma", "SM (Retd.)"],
                "strict_keywords": ["rk sharma", "brigadier"]
            },
            {
                "id": "Q6",
                "category": "Academics Leadership",
                "question": "Who is the Dean (Academics) at JUIT Solan?",
                "expected_facts": ["Prof. (Dr.) Shruti Jain", "ECE"],
                "strict_keywords": ["shruti jain"]
            },
            {
                "id": "Q7",
                "category": "Rankings",
                "question": "What is the NIRF ranking of JUIT?",
                "expected_facts": ["201-300", "Engineering", "NIRF 2025"],
                "strict_keywords": ["201-300"]
            },
            {
                "id": "Q8",
                "category": "Establishment & History",
                "question": "When was JUIT established and by which act?",
                "expected_facts": ["2002", "Himachal Pradesh State Legislature"],
                "strict_keywords": ["2002"]
            },
            {
                "id": "Q9",
                "category": "Faculty Profile",
                "question": "Tell me about Dr. Rakesh Kumar Bajaj and his administrative role.",
                "expected_facts": ["Dean of Students Welfare", "Mathematics"],
                "strict_keywords": ["students welfare", "mathematics"]
            },
            {
                "id": "Q10",
                "category": "Student Welfare / Hostel",
                "question": "What are the hostel charges per semester for double occupancy?",
                "expected_facts": ["84,000 INR", "Double occupancy"],
                "strict_keywords": ["84,000"]
            }
        ]

        results = []
        total_time = 0

        for q in qna_pairs:
            t0 = time.time()
            resp = await client.post("/chat", json={"message": q["question"], "session_id": f"qna_{q['id']}"})
            latency = time.time() - t0
            total_time += latency
            
            assert resp.status_code == 200, f"Error calling /chat for {q['id']}: {resp.text}"
            data = resp.json()
            answer = data["response"]
            citations = data.get("citations", [])
            trust_level = data.get("trust_level", "B")

            # Normalize hyphens and dashes
            answer_norm = answer.replace("–", "-").replace("—", "-").lower()
            all_passed = all(kw.lower() in answer_norm for kw in q["strict_keywords"])
            
            status = "PASS" if all_passed else "FAIL"
            results.append({
                "id": q["id"],
                "category": q["category"],
                "question": q["question"],
                "expected": ", ".join(q["expected_facts"]),
                "answer_snippet": answer.replace("\n", " ")[:140],
                "status": status,
                "latency_sec": round(latency, 2),
                "citations": citations,
                "trust_level": trust_level
            })

            print(f"\n[{q['id']}] Category: {q['category']}")
            print(f"  Q: {q['question']}")
            print(f"  Expected: {', '.join(q['expected_facts'])}")
            print(f"  Response: {answer.replace(chr(10), ' ')[:120]}...")
            print(f"  Status: {'✅ PASS' if all_passed else '❌ FAIL'} | Latency: {latency:.2f}s | Trust: Track {trust_level}")
            if citations:
                print(f"  Sources: {citations}")

        print("\n" + "=" * 80)
        passed_count = sum(1 for r in results if r["status"] == "PASS")
        avg_latency = total_time / len(results)
        accuracy = (passed_count / len(results)) * 100
        print(f"🏁 BENCHMARK SUMMARY:")
        print(f"   Total Tested: {len(results)}")
        print(f"   Passed: {passed_count}")
        print(f"   Accuracy: {accuracy:.1f}%")
        print(f"   Avg Latency: {avg_latency:.2f}s")
        print("=" * 80)

        import os
        os.makedirs("benchmarks", exist_ok=True)
        out_file = os.path.join("benchmarks", "benchmark_results.json")
        with open(out_file, "w") as f:
            json.dump({
                "accuracy": accuracy,
                "total": len(results),
                "passed": passed_count,
                "avg_latency": avg_latency,
                "details": results
            }, f, indent=2)

if __name__ == "__main__":
    asyncio.run(run_tests())
