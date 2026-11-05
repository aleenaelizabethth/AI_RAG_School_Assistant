from policy_rag import search_policy

tests = [
    ("What time does school start?", [1]),
    ("Can my child learn swimming?", [5]),
    ("Where can my daughter learn guitar?", [6]),
    ("Is there a school bus?", [7]),
    ("Who do I call about fee receipts?", [10, 12]),
    ("My son is sick and will miss school", [2, 3]),
    ("What are the behaviour rules?", [8]),
    ("Do students have to join a sport?", [5]),
    ("Is the swimming pool safe?", [5, 9]),
    ("Is this a real school?", [13]),
    ("badminton coaching", [5]),
    ("choir", [6]),
    ("refunds", [10]),
    ("Transportation Department", [7, 12]),
    ("cricket equipment", [5]),
    ("mime and storytelling", [6]),
    ("outstanding balance", [10]),
    ("pickup and drop-off points", [7]),
    ("medical or accessibility concerns", [9, 5]),
    ("placeholder email address", [12, 13]),
]

for mode in ["meaning", "keyword", "hybrid"]:
    hits = 0
    for question, correct in tests:
        results = search_policy(question, top_k=2, mode=mode)
        found = [int(r["text"].split(".")[0]) for r in results if r["text"][0].isdigit()]
        if any(n in correct for n in found):
            hits += 1
        else:
            print("  missed (" + mode + "):", question)
    print(mode, ":", hits, "/", len(tests))