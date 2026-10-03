"""Print every number quoted in the paper from results.json and data/scored.jsonl.

Offline: no model or API call is made.

Usage (from the repository root):
    python code/paper_numbers.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = json.load(open(os.path.join(ROOT, "results.json"), encoding="utf-8"))
S = [json.loads(l) for l in open(os.path.join(ROOT, "data", "scored.jsonl"), encoding="utf-8")
     if l.strip()]
P, C, H, M = R["pooled_arm_by_depth"], R["cells"], R["per_hop_survival_depth5"], R["meta"]
FAM = [("anthropic_haiku45", "Claude Haiku 4.5"), ("mistral_pixtral_lg", "Pixtral Large"),
       ("meta_llama33_70b", "Llama 3.3 70B"), ("amazon_nova_pro", "Nova Pro")]


def pct(k, n):
    return 100.0 * k / n


print("== Method")
print("chains scored: %d, judged: %d, generation hops: %d"
      % (M["n_chains_scored"], M["n_judged"], sum(c["depth"] * c["n"] for c in C.values())))
agree = int(round(M["prog_judge_agreement"] * M["n_judged"]))
print("programmatic/judge agreement: %d/%d = %.1f%%"
      % (agree, M["n_judged"], 100 * M["prog_judge_agreement"]))

print("\n== Headline (pooled over depths, strict FULL)")
for arm in ("control", "clause"):
    k = sum(P["%s|d%d" % (arm, d)]["prog_FULL"] for d in (1, 3, 5))
    n = sum(P["%s|d%d" % (arm, d)]["n"] for d in (1, 3, 5))
    print("%-8s %d/%d = %.1f%%" % (arm, k, n, pct(k, n)))

print("\n== Figure 3 / depth sweep (strict FULL, Wilson 95%)")
for arm in ("control", "clause"):
    for d in (1, 3, 5):
        p = P["%s|d%d" % (arm, d)]
        lo, hi = p["prog_full_ci95"]
        print("%-8s d=%d  %d/%d = %.1f%%  [%.0f, %.0f]"
              % (arm, d, p["prog_FULL"], p["n"], 100 * p["prog_full_rate"], 100 * lo, 100 * hi))

print("\n== Figure 2 / per-hop retention, depth-5 control, all families")
row = H["control|ALL"]
print("retained per hop:", ", ".join("%.1f" % (100 * h["full_rate"]) for h in row["hops"]))
h1, h5 = row["hops"][0]["full"], row["hops"][4]["full"]
print("lost at hop 1: %d of %d (%.1f%%); lost over hops 2-5: %d chains (%.1f points)"
      % (row["n"] - h1, row["n"], pct(row["n"] - h1, row["n"]), h1 - h5, pct(h1 - h5, row["n"])))

print("\n== Table 1 (pooled over depths, n=60 per cell, percent)")
print("%-18s %6s %6s %6s | %6s %6s %6s" % ("family", "full", "name", "id", "full", "name", "id"))
for fk, lab in FAM:
    out = []
    for arm in ("control", "clause"):
        cs = [C["%s|%s|d%d" % (fk, arm, d)] for d in (1, 3, 5)]
        n = sum(c["n"] for c in cs)
        out += [pct(sum(c["prog"]["FULL"] for c in cs), n),
                pct(sum(c["prog_name_hit"] for c in cs), n),
                pct(sum(c["prog_id_hit"] for c in cs), n)]
    print("%-18s %6.1f %6.1f %6.1f | %6.1f %6.1f %6.1f" % ((lab,) + tuple(out)))

print("\n== Fabrication (LLM judge)")
fab = [r for r in S if r.get("judge_fabricated")]
nclause = sum(1 for r in S if r["arm"] == "clause")
print("judge-flagged: %d of %d chains; %d of %d clause chains (%.1f%%); control: %d"
      % (len(fab), len(S), sum(1 for r in fab if r["arm"] == "clause"), nclause,
         pct(sum(1 for r in fab if r["arm"] == "clause"), nclause),
         sum(1 for r in fab if r["arm"] == "control")))
for r in fab:
    print("  %s  %s" % (r["key"], r["judge_fabricated_text"][:90]))

print("\n== Regex screen (disclosed, not used)")
fab_keys = set(r["key"] for r in fab)
fires = set()
for r in S:
    true = r["principal_id"].replace("-", "").lower()
    for m in re.finditer(r"\b([A-Za-z]{1,4})[-\s]?(\d{3,6})\b", r["terminal_handoff"]):
        if (m.group(1) + m.group(2)).lower() != true:
            fires.add(r["key"])
tp = len(fires & fab_keys)
print("fires on %d of %d chains; true positives %d; precision %.2f; recall %.2f"
      % (len(fires), len(S), tp, tp / float(len(fires) or 1), tp / float(len(fab_keys) or 1)))
