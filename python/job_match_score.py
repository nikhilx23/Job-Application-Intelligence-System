"""
job_match_score.py — the "Job Match Score" tool (also built as a live
formula tool in excel/Job_Application_Dashboard.xlsx, sheet "Job Match
Score"). Scores how well a job posting's required skills match your
current skill set, and recommends a prioritized learning path for the
gap -- ranked by how often that skill shows up across all 185 logged
postings, so you learn the skill that unlocks the most future
applications first, not just any missing skill.

Usage:
    python3 job_match_score.py --required "SQL, Python, Power BI, Tableau, Machine Learning, AWS" \\
                                --have "Excel, SQL, Python, Power BI, Pandas, PivotTables, Data Cleaning, Data Visualization, Statistics, Communication"
"""
import argparse
import csv
from collections import Counter


def load_skill_demand():
    counts = Counter()
    with open("data/clean/application_skills.csv", newline="") as f:
        for row in csv.DictReader(f):
            counts[row["Skill"]] += 1
    return counts


def match_score(required, have):
    required = {s.strip() for s in required.split(",") if s.strip()}
    have = {s.strip() for s in have.split(",") if s.strip()}
    matched = required & have
    missing = required - have
    score = len(matched) / len(required) if required else 0.0
    return score, matched, missing


def main():
    parser = argparse.ArgumentParser(description="Score a job posting's skill match")
    parser.add_argument("--required", required=True,
                         help="Comma-separated required skills from the posting")
    parser.add_argument("--have", required=True,
                         help="Comma-separated skills you currently have")
    args = parser.parse_args()

    score, matched, missing = match_score(args.required, args.have)
    demand = load_skill_demand()

    total = len(matched) + len(missing)
    print(f"Match score: {score:.0%}  ({len(matched)}/{total} required skills)")
    print(f"You have: {', '.join(sorted(matched)) or '(none)'}")
    print(f"Missing:  {', '.join(sorted(missing)) or '(none)'}")

    if missing:
        ranked = sorted(missing, key=lambda s: demand.get(s, 0), reverse=True)
        print("\nPrioritized learning path (missing skills, ranked by how often")
        print("they appear across your 185 logged postings -- learn the top one first):")
        for s in ranked:
            print(f"  - {s}  (appears in {demand.get(s, 0)} postings)")


if __name__ == "__main__":
    main()
