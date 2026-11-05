import asyncio
import time
import json
import httpx
from src.main import app
from src.services.db import db_service

# Reload topics.json in db_service to ensure latest mappings
db_service.topics = db_service._load_json("topics.json")

TEST_SUITE = [
    # --- Category 1: Fee Structure ---
    {
        "id": 1,
        "category": "Fee Structure",
        "question": "What is the B.Tech first year fee per semester at JUIT?",
        "expected": "1,64,550 INR/sem",
        "keywords": ["1,64,550"]
    },
    {
        "id": 2,
        "category": "Fee Structure",
        "question": "What is the semester fee for BCA and BBA courses?",
        "expected": "82,550 INR/sem",
        "keywords": ["82,550"]
    },
    {
        "id": 3,
        "category": "Fee Structure",
        "question": "How much does the M.Tech program cost per semester at JUIT?",
        "expected": "74,850 INR/sem",
        "keywords": ["74,850"]
    },
    {
        "id": 4,
        "category": "Fee Structure",
        "question": "What is the tuition fee per semester for MBA students?",
        "expected": "1,62,500 INR/sem",
        "keywords": ["1,62,500"]
    },
    {
        "id": 5,
        "category": "Fee Structure",
        "question": "What is the semester fee for Ph.D scholars at JUIT?",
        "expected": "32,450 INR/sem",
        "keywords": ["32,450"]
    },

    # --- Category 2: Additional Charges & Concessions ---
    {
        "id": 6,
        "category": "Charges & Concessions",
        "question": "What is the refundable caution money amount at JUIT?",
        "expected": "20,000 INR",
        "keywords": ["20,000"]
    },
    {
        "id": 7,
        "category": "Charges & Concessions",
        "question": "How much are the one-time admission charges for B.Tech students?",
        "expected": "25,000 INR",
        "keywords": ["25,000"]
    },
    {
        "id": 8,
        "category": "Charges & Concessions",
        "question": "What are the hostel charges per semester for double occupancy?",
        "expected": "84,000 INR",
        "keywords": ["84,000"]
    },
    {
        "id": 9,
        "category": "Charges & Concessions",
        "question": "How much extra is charged per semester for a single occupancy hostel room?",
        "expected": "8,000 INR",
        "keywords": ["8,000"]
    },
    {
        "id": 10,
        "category": "Charges & Concessions",
        "question": "What fee concession is provided to wards of Armed and Paramilitary personnel?",
        "expected": "30%",
        "keywords": ["30%"]
    },

    # --- Category 3: Placements & Packages ---
    {
        "id": 11,
        "category": "Placements",
        "question": "What was the highest package offered to the 2021-25 batch?",
        "expected": "50 LPA",
        "keywords": ["50"]
    },
    {
        "id": 12,
        "category": "Placements",
        "question": "Which company offered the highest package of 50 LPA at JUIT?",
        "expected": "Google",
        "keywords": ["google"]
    },
    {
        "id": 13,
        "category": "Placements",
        "question": "What was the second highest salary offered to the 2021-25 batch and by whom?",
        "expected": "46.38 LPA by Amazon",
        "keywords": ["46.38", "amazon"]
    },
    {
        "id": 14,
        "category": "Placements",
        "question": "What is the average or mean placement salary for the 2021-25 batch?",
        "expected": "7.18 LPA",
        "keywords": ["7.18"]
    },
    {
        "id": 15,
        "category": "Placements",
        "question": "What is the median salary for the 2021-25 batch?",
        "expected": "6 LPA",
        "keywords": ["6"]
    },
    {
        "id": 16,
        "category": "Placements",
        "question": "Name some of the key recruiters that hire from JUIT.",
        "expected": "Google, Amazon, Zscaler, Infosys, Wipro, Cognizant",
        "keywords": ["google", "amazon"]
    },

    # --- Category 4: University Leadership ---
    {
        "id": 17,
        "category": "Leadership",
        "question": "Who is the Chancellor of Jaypee University of Information Technology?",
        "expected": "Sh. Manoj Gaur",
        "keywords": ["manoj gaur"]
    },
    {
        "id": 18,
        "category": "Leadership",
        "question": "Who is the Vice Chancellor of JUIT Solan?",
        "expected": "Prof. (Dr.) Rajendra Kumar Sharma",
        "keywords": ["rajendra", "sharma"]
    },
    {
        "id": 19,
        "category": "Leadership",
        "question": "From which institute did the Vice Chancellor Prof. Rajendra Kumar Sharma complete his PhD?",
        "expected": "IIT Roorkee",
        "keywords": ["roorkee"]
    },
    {
        "id": 20,
        "category": "Leadership",
        "question": "Who was the predecessor of Vice Chancellor Prof. Rajendra Kumar Sharma?",
        "expected": "Prof. Vinod Kumar",
        "keywords": ["vinod kumar"]
    },
    {
        "id": 21,
        "category": "Leadership",
        "question": "Who is the Registrar and Dean of Students at JUIT?",
        "expected": "Brigadier RK Sharma, SM (Retd.)",
        "keywords": ["rk sharma", "brigadier"]
    },

    # --- Category 5: Deans & Faculty Leadership ---
    {
        "id": 22,
        "category": "Deans & Academic Heads",
        "question": "Who is the Dean (Academics) at JUIT Solan?",
        "expected": "Prof. (Dr.) Shruti Jain",
        "keywords": ["shruti jain"]
    },
    {
        "id": 23,
        "category": "Deans & Academic Heads",
        "question": "Which department does the Dean Academics Prof. Shruti Jain belong to?",
        "expected": "ECE (Electronics and Communication Engineering)",
        "keywords": ["ece", "electronics"]
    },
    {
        "id": 24,
        "category": "Deans & Academic Heads",
        "question": "Who is the Dean of Students Welfare (DOSW) at JUIT?",
        "expected": "Prof. Dr. Rakesh Kumar Bajaj",
        "keywords": ["rakesh", "bajaj"]
    },
    {
        "id": 25,
        "category": "Deans & Academic Heads",
        "question": "Which academic department is headed by Prof. Rakesh Kumar Bajaj?",
        "expected": "Department of Mathematics",
        "keywords": ["mathematics"]
    },
    {
        "id": 26,
        "category": "Deans & Academic Heads",
        "question": "Who is the Associate Dean (Innovation) at JUIT?",
        "expected": "Prof. (Dr.) Tiratha Raj Singh",
        "keywords": ["tiratha raj singh"]
    },

    # --- Category 6: Administration & Staff ---
    {
        "id": 27,
        "category": "Staff & Administration",
        "question": "Who is the Assistant Registrar (Academics) in the Registrar Office?",
        "expected": "Mr. Sanjay Kumar Verma",
        "keywords": ["sanjay", "verma"]
    },
    {
        "id": 28,
        "category": "Staff & Administration",
        "question": "Who is the Chief Finance Officer (CFO) of JUIT?",
        "expected": "Sh. Hemant Vyas",
        "keywords": ["hemant vyas"]
    },
    {
        "id": 29,
        "category": "Staff & Administration",
        "question": "Who heads the Human Resources (HR) department at JUIT?",
        "expected": "Mr. M. R. Zinta",
        "keywords": ["zinta"]
    },
    {
        "id": 30,
        "category": "Staff & Administration",
        "question": "Who is the Principal Consultant for IT Infrastructure at JUIT?",
        "expected": "Mr. Sanjay Jain",
        "keywords": ["sanjay jain"]
    },
    {
        "id": 31,
        "category": "Staff & Administration",
        "question": "What is the total faculty strength across departments at JUIT Solan?",
        "expected": "Over 150+ members",
        "keywords": ["150"]
    },

    # --- Category 7: Rankings & Accreditations ---
    {
        "id": 32,
        "category": "Rankings",
        "question": "What is the NIRF 2025 ranking band of JUIT in Engineering?",
        "expected": "201-300 band",
        "keywords": ["201-300"]
    },
    {
        "id": 33,
        "category": "Rankings",
        "question": "What star rating was awarded to JUIT by the Institution's Innovation Council (IIC) for 2023-24?",
        "expected": "3.5-star rating",
        "keywords": ["3.5"]
    },
    {
        "id": 34,
        "category": "Rankings",
        "question": "Which engineering program holds NBA accreditation from 2024 to 2027 at JUIT?",
        "expected": "B.Tech Biotechnology",
        "keywords": ["biotechnology"]
    },
    {
        "id": 35,
        "category": "Rankings",
        "question": "Which was the first private university in Himachal Pradesh accredited by NAAC?",
        "expected": "JUIT (Jaypee University of Information Technology)",
        "keywords": ["juit", "jaypee"]
    },

    # --- Category 8: History & Location ---
    {
        "id": 36,
        "category": "History & Campus",
        "question": "In which year was JUIT established?",
        "expected": "2002",
        "keywords": ["2002"]
    },
    {
        "id": 37,
        "category": "History & Campus",
        "question": "Under which Act of the Himachal Pradesh Legislature was JUIT established?",
        "expected": "Act No. 14 of 2002",
        "keywords": ["14"]
    },
    {
        "id": 38,
        "category": "History & Campus",
        "question": "Which entity partnered with the Himachal Pradesh Government to establish JUIT?",
        "expected": "Jaiprakash Sewa Sansthan",
        "keywords": ["jaiprakash"]
    },
    {
        "id": 39,
        "category": "History & Campus",
        "question": "Where is JUIT campus located?",
        "expected": "Waknaghat, Solan, Himachal Pradesh",
        "keywords": ["waknaghat", "solan"]
    },
    {
        "id": 40,
        "category": "History & Campus",
        "question": "What is the distance of JUIT from Shimla and Chandigarh?",
        "expected": "25 km from Shimla, 85 km from Chandigarh",
        "keywords": ["25", "85"]
    },

    # --- Category 9: Admissions & Programs ---
    {
        "id": 41,
        "category": "Admissions & Programs",
        "question": "What are the modes of admission for B.Tech programs at JUIT?",
        "expected": "JEE Rank and 10+2 Merit",
        "keywords": ["jee", "10+2"]
    },
    {
        "id": 42,
        "category": "Admissions & Programs",
        "question": "Does JUIT offer lateral entry admission to B.Tech programs?",
        "expected": "Yes, B.Tech (Lateral Entry) is offered",
        "keywords": ["lateral entry"]
    },
    {
        "id": 43,
        "category": "Admissions & Programs",
        "question": "Which postgraduate programs are offered at JUIT?",
        "expected": "M.Tech, M.Sc, and MBA",
        "keywords": ["m.tech", "mba"]
    },

    # --- Category 10: Faculty Profiles ---
    {
        "id": 44,
        "category": "Faculty Profile",
        "question": "Tell me about Prof. Shruti Jain's scientific recognition.",
        "expected": "Top 2% scientists globally by Stanford University",
        "keywords": ["stanford", "2%"]
    },
    {
        "id": 45,
        "category": "Faculty Profile",
        "question": "Who is Prof. Dr. Hemant Sood at JUIT?",
        "expected": "Professor in Biotechnology and Bioinformatics",
        "keywords": ["hemant sood"]
    },

    # --- Category 11: Conversational & Intent Routing (Punctuation Edge Cases) ---
    {
        "id": 46,
        "category": "Conversational",
        "question": "hello!",
        "expected": "Chitchat greeting",
        "keywords": ["luna", "help"]
    },
    {
        "id": 47,
        "category": "Conversational",
        "question": "who are you?",
        "expected": "Luna official assistant identity",
        "keywords": ["luna", "assistant"]
    },
    {
        "id": 48,
        "category": "Conversational",
        "question": "thank you!",
        "expected": "Welcome message",
        "keywords": ["welcome"]
    },

    # --- Category 12: Collision Resilience & Negative Guardrails ---
    {
        "id": 49,
        "category": "Collision Resilience",
        "question": "Can I give feedback on my hostel experience?",
        "expected": "Must NOT return fee structure",
        "negative_keywords": ["1,64,550", "tuition", "caution money"],
        "keywords": []
    },
    {
        "id": 50,
        "category": "Negative Safety / Guardrails",
        "question": "What is the secret recipe of Coca-Cola?",
        "expected": "Refusal / missing information statement",
        "keywords": ["not have", "database"]
    }
]

async def run_50_test_suite():
    print("=" * 85)
    print("🧪 STARTING COMPREHENSIVE 50-QUESTION EVALUATION SUITE FOR LUNA")
    print("   Target Model: antigravity/gemini-3.6-flash-medium")
    print("   Endpoint: http://localhost:20128/v1")
    print("=" * 85)

    transport = httpx.ASGITransport(app=app)
    results = []
    total_latency = 0.0

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        for idx, item in enumerate(TEST_SUITE, start=1):
            qid = item["id"]
            cat = item["category"]
            q = item["question"]
            expected = item["expected"]
            keywords = item.get("keywords", [])
            neg_keywords = item.get("negative_keywords", [])

            t0 = time.time()
            resp = await client.post("/chat", json={"message": q, "session_id": f"eval_50_{qid}"})
            latency = time.time() - t0
            total_latency += latency

            if resp.status_code != 200:
                print(f"❌ [Q{qid:02d}] HTTP {resp.status_code} Error: {resp.text}")
                results.append({
                    "id": qid,
                    "category": cat,
                    "question": q,
                    "status": "FAIL",
                    "reason": f"HTTP {resp.status_code}",
                    "latency": latency
                })
                continue

            data = resp.json()
            answer = data.get("response", "")
            citations = data.get("citations", [])
            trust_level = data.get("trust_level", "B")

            # Normalization
            answer_norm = answer.replace("–", "-").replace("—", "-").lower()

            # Check positive keywords
            pos_pass = all(k.lower() in answer_norm for k in keywords)
            # Check negative keywords
            neg_pass = not any(nk.lower() in answer_norm for nk in neg_keywords)

            passed = pos_pass and neg_pass
            status = "PASS" if passed else "FAIL"

            results.append({
                "id": qid,
                "category": cat,
                "question": q,
                "expected": expected,
                "response": answer,
                "status": status,
                "latency": round(latency, 2),
                "citations": citations,
                "trust_level": trust_level
            })

            status_icon = "✅ PASS" if passed else "❌ FAIL"
            print(f"[{qid:02d}/50] {status_icon} | {cat:<22} | Latency: {latency:.2f}s | Q: {q[:45]}...")

    passed_count = sum(1 for r in results if r["status"] == "PASS")
    failed_count = len(results) - passed_count
    accuracy = (passed_count / len(results)) * 100
    avg_latency = total_latency / len(results)

    print("\n" + "=" * 85)
    print("📈 FINAL COMPREHENSIVE BENCHMARK REPORT (50 QUESTIONS)")
    print("=" * 85)
    print(f"   Total Questions : {len(results)}")
    print(f"   Passed          : {passed_count}")
    print(f"   Failed          : {failed_count}")
    print(f"   Accuracy        : {accuracy:.2f}%")
    print(f"   Avg Latency     : {avg_latency:.2f}s")
    print("=" * 85)

    # Category breakdown
    cat_stats = {}
    for r in results:
        c = r["category"]
        if c not in cat_stats:
            cat_stats[c] = {"total": 0, "passed": 0}
        cat_stats[c]["total"] += 1
        if r["status"] == "PASS":
            cat_stats[c]["passed"] += 1

    print("\n📊 CATEGORY BREAKDOWN:")
    for c, s in cat_stats.items():
        acc = (s["passed"] / s["total"]) * 100
        print(f"   • {c:<25}: {s['passed']}/{s['total']} ({acc:.1f}%)")

    # Save complete detailed JSON results
    import os
    os.makedirs("benchmarks", exist_ok=True)
    out_file = os.path.join("benchmarks", "results_50_questions.json")
    with open(out_file, "w") as f:
        json.dump({
            "overall_accuracy": accuracy,
            "passed": passed_count,
            "failed": failed_count,
            "avg_latency": avg_latency,
            "category_stats": cat_stats,
            "detailed_results": results
        }, f, indent=2)
    print(f"\nDetailed results saved to {out_file}")

if __name__ == "__main__":
    asyncio.run(run_50_test_suite())
