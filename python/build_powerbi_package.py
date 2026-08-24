"""
build_powerbi_package.py — exports a star-schema CSV package (ready to
import into Power BI / Power Query) into powerbi/.
"""
import csv
import sqlite3

conn = sqlite3.connect("sql/jobsearch.db")


def export(sql, path, headers):
    rows = conn.execute(sql).fetchall()
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    print(f"  {path}  ({len(rows)} rows)")


def main():
    print("Building Power BI star schema:")

    export("SELECT resume_id, version_name, focus_area FROM resumes",
           "powerbi/dim_resume.csv", ["resume_id", "version_name", "focus_area"])

    export("SELECT DISTINCT source AS source_name FROM applications",
           "powerbi/dim_source.csv", ["source_name"])

    export("SELECT DISTINCT company AS company_name FROM applications",
           "powerbi/dim_company.csv", ["company_name"])

    export("SELECT DISTINCT skill AS skill_name FROM application_skills",
           "powerbi/dim_skill.csv", ["skill_name"])

    export("""SELECT application_id, company, role_title, location, date_applied,
                     source, resume_id, salary_min, salary_max, status,
                     response_date, interview_date, response_time_days
              FROM applications""",
           "powerbi/fact_applications.csv",
           ["application_id", "company", "role_title", "location", "date_applied",
            "source", "resume_id", "salary_min", "salary_max", "status",
            "response_date", "interview_date", "response_time_days"])

    export("SELECT application_id, skill FROM application_skills",
           "powerbi/fact_application_skills.csv", ["application_id", "skill"])

    print("Done.")


if __name__ == "__main__":
    main()
