"""
analysis.py — runs the full analysis against sql/jobsearch.db, prints the
dashboard's six headline answers, and produces the charts in charts/.
"""
import sqlite3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

conn = sqlite3.connect("sql/jobsearch.db")


def q(sql):
    return pd.read_sql_query(sql, conn)


def main():
    print("=" * 70)
    print("JOB APPLICATION INTELLIGENCE SYSTEM — ANALYSIS")
    print("=" * 70)

    # --- Overall funnel ---
    funnel = q("""
        SELECT COUNT(*) AS total,
               ROUND(100.0*SUM(CASE WHEN status IN ('Interview','Offer') THEN 1 ELSE 0 END)/COUNT(*),1) AS interview_rate,
               SUM(CASE WHEN status='Offer' THEN 1 ELSE 0 END) AS offers,
               ROUND(AVG(response_time_days),1) AS avg_response
        FROM applications
    """).iloc[0]
    print(f"\n1) Total applications: {int(funnel.total)}")
    print(f"   Interview rate: {funnel.interview_rate}%")
    print(f"   Offers received: {int(funnel.offers)}")
    print(f"   Avg response time: {funnel.avg_response} days")

    # --- Resume performance ---
    resume_perf = q("""
        SELECT r.version_name AS resume, COUNT(*) AS sent,
               SUM(CASE WHEN a.status IN ('Interview','Offer') THEN 1 ELSE 0 END) AS interviews,
               ROUND(100.0*SUM(CASE WHEN a.status IN ('Interview','Offer') THEN 1 ELSE 0 END)/COUNT(*),1) AS rate
        FROM applications a JOIN resumes r ON r.resume_id = a.resume_id
        GROUP BY r.version_name ORDER BY rate DESC
    """)
    print(f"\n2) Best-performing resume: {resume_perf.iloc[0]['resume']} "
          f"({resume_perf.iloc[0]['rate']}% interview rate)")
    print(resume_perf.to_string(index=False))

    plt.figure(figsize=(7, 4.5))
    plt.bar(resume_perf["resume"], resume_perf["rate"], color="#4C72B0")
    plt.ylabel("Interview rate (%)")
    plt.title("Interview rate by resume version")
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    plt.savefig("charts/01_resume_performance.png", dpi=130)
    plt.close()

    # --- Source performance ---
    source_perf = q("""
        SELECT source, COUNT(*) AS sent,
               ROUND(100.0*SUM(CASE WHEN status IN ('Interview','Offer') THEN 1 ELSE 0 END)/COUNT(*),1) AS rate
        FROM applications GROUP BY source ORDER BY rate DESC
    """)
    print(f"\n3) Best-performing source: {source_perf.iloc[0]['source']} "
          f"({source_perf.iloc[0]['rate']}% interview rate)")

    plt.figure(figsize=(7, 4.5))
    plt.barh(source_perf["source"][::-1], source_perf["rate"][::-1], color="#55A868")
    plt.xlabel("Interview rate (%)")
    plt.title("Interview rate by application source")
    plt.tight_layout()
    plt.savefig("charts/02_source_performance.png", dpi=130)
    plt.close()

    # --- Fastest responders ---
    fastest = q("""
        SELECT company, ROUND(AVG(response_time_days),1) AS avg_days
        FROM applications WHERE response_time_days IS NOT NULL
        GROUP BY company ORDER BY avg_days ASC LIMIT 8
    """)
    print(f"\n4) Fastest-responding company: {fastest.iloc[0]['company']} "
          f"({fastest.iloc[0]['avg_days']} days)")

    plt.figure(figsize=(7, 4.5))
    plt.barh(fastest["company"][::-1], fastest["avg_days"][::-1], color="#C44E52")
    plt.xlabel("Avg. response time (days)")
    plt.title("Fastest-responding companies")
    plt.tight_layout()
    plt.savefig("charts/03_fastest_responders.png", dpi=130)
    plt.close()

    # --- Top skills ---
    top_skills = q("""
        SELECT skill, COUNT(*) AS n FROM application_skills
        GROUP BY skill ORDER BY n DESC LIMIT 10
    """)
    print(f"\n5) Most-requested skill: {top_skills.iloc[0]['skill']} "
          f"({int(top_skills.iloc[0]['n'])} postings)")

    plt.figure(figsize=(7, 4.5))
    plt.barh(top_skills["skill"][::-1], top_skills["n"][::-1], color="#8172B2")
    plt.xlabel("Times requested")
    plt.title("Top 10 requested skills across all postings")
    plt.tight_layout()
    plt.savefig("charts/04_top_skills.png", dpi=130)
    plt.close()

    # --- Status breakdown ---
    status = q("SELECT status, COUNT(*) AS n FROM applications GROUP BY status")
    print(f"\n6) Status breakdown:")
    print(status.to_string(index=False))

    plt.figure(figsize=(6, 6))
    order = ["Applied", "No Response", "Rejected", "Interview", "Offer"]
    status = status.set_index("status").reindex(order).reset_index()
    colors = ["#8C8C8C", "#D9D9D9", "#C44E52", "#4C72B0", "#55A868"]
    plt.pie(status["n"], labels=status["status"], autopct="%1.0f%%", colors=colors)
    plt.title("Application status breakdown")
    plt.tight_layout()
    plt.savefig("charts/05_status_breakdown.png", dpi=130)
    plt.close()

    print("\nCharts written to charts/ (5 PNGs).")


if __name__ == "__main__":
    main()
