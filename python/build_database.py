"""
build_database.py — loads the cleaned CSVs into a normalized SQLite
database (sql/jobsearch.db) using sql/schema.sql.
"""
import csv
import sqlite3


def main():
    conn = sqlite3.connect("sql/jobsearch.db")
    cur = conn.cursor()

    with open("sql/schema.sql") as f:
        cur.executescript(f.read())

    # resumes
    with open("data/clean/resumes.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute(
                "INSERT INTO resumes (version_name, focus_area) VALUES (?, ?)",
                (row["resume_version"], row["focus_area"]),
            )
    resume_id_by_name = {
        name: rid for rid, name in
        cur.execute("SELECT resume_id, version_name FROM resumes")
    }

    # applications
    with open("data/clean/applications_clean.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute(
                """INSERT INTO applications
                   (application_id, company, role_title, location, date_applied,
                    source, resume_id, salary_min, salary_max, status,
                    response_date, interview_date, response_time_days)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    row["Application ID"], row["Company"], row["Role Title"],
                    row["Location"], row["Date Applied"], row["Source"],
                    resume_id_by_name[row["Resume Version"]],
                    int(row["Salary Min"]) if row["Salary Min"] else None,
                    int(row["Salary Max"]) if row["Salary Max"] else None,
                    row["Status"],
                    row["Response Date"] or None,
                    row["Interview Date"] or None,
                    int(row["Response Time (Days)"]) if row["Response Time (Days)"] else None,
                ),
            )

    # application_skills
    with open("data/clean/application_skills.csv", newline="") as f:
        reader = csv.DictReader(f)
        seen = set()
        for row in reader:
            key = (row["Application ID"], row["Skill"])
            if key in seen:
                continue
            seen.add(key)
            cur.execute(
                "INSERT INTO application_skills (application_id, skill) VALUES (?, ?)",
                (row["Application ID"], row["Skill"]),
            )

    conn.commit()

    n_apps = cur.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    n_resumes = cur.execute("SELECT COUNT(*) FROM resumes").fetchone()[0]
    n_skills = cur.execute("SELECT COUNT(*) FROM application_skills").fetchone()[0]
    print(f"Loaded {n_apps} applications, {n_resumes} resumes, "
          f"{n_skills} application-skill rows into sql/jobsearch.db")

    conn.close()


if __name__ == "__main__":
    main()
