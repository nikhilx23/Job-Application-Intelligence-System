# Power BI Guide — Job Application Intelligence System

Step-by-step guide to rebuild the dashboard in Power BI Desktop from the
CSVs in this folder.

## 1. Import the data

Power BI Desktop → **Get Data → Text/CSV** → import all six files:

- `dim_resume.csv`
- `dim_source.csv`
- `dim_company.csv`
- `dim_skill.csv`
- `fact_applications.csv`
- `fact_application_skills.csv`

## 2. Build the data model (star schema)

In **Model view**, create these relationships (drag from the fact table's
key to the dimension table's key):

| From | To | Cardinality |
|---|---|---|
| `fact_applications[resume_id]` | `dim_resume[resume_id]` | Many-to-one |
| `fact_applications[source]` | `dim_source[source_name]` | Many-to-one |
| `fact_applications[company]` | `dim_company[company_name]` | Many-to-one |
| `fact_application_skills[application_id]` | `fact_applications[application_id]` | Many-to-one |
| `fact_application_skills[skill]` | `dim_skill[skill_name]` | Many-to-one |

This mirrors the same normalized structure as `sql/schema.sql` — one fact
table (applications) surrounded by lookup/dimension tables, which is why
the numbers match the SQL and Excel versions exactly.

## 3. Power Query cleanup (if importing your own raw data instead)

If you swap in your own job-search export instead of this project's data:

1. **Home → Transform Data** to open Power Query Editor
2. On `fact_applications`: set `date_applied`, `response_date`,
   `interview_date` to Date type; trim whitespace on `company`
3. Split `application_skills`' comma-separated skill text into rows with
   **Split Column → By Delimiter → Rows** if your export isn't already
   normalized like `fact_application_skills.csv`

## 4. Key DAX measures

```dax
Total Applications = COUNTROWS(fact_applications)

Interviews =
CALCULATE(
    COUNTROWS(fact_applications),
    fact_applications[status] IN {"Interview", "Offer"}
)

Interview Rate = DIVIDE([Interviews], [Total Applications], 0)

Offers = CALCULATE(COUNTROWS(fact_applications), fact_applications[status] = "Offer")

Avg Response Days = AVERAGE(fact_applications[response_time_days])

-- Time intelligence example: applications this month vs. last month
Applications This Month =
CALCULATE([Total Applications], DATESMTD(fact_applications[date_applied]))

Applications Prior Month =
CALCULATE(
    [Total Applications],
    DATEADD(fact_applications[date_applied], -1, MONTH)
)
```

## 5. Suggested visuals

- **Card visuals**: Total Applications, Interview Rate, Offers, Avg
  Response Days (mirrors the Excel dashboard's top row)
- **Bar chart**: Interview Rate by `dim_resume[version_name]`
- **Bar chart**: Interview Rate by `dim_source[source_name]`
- **Bar chart**: Avg response days by `dim_company[company_name]` (top 8,
  sort ascending)
- **Bar chart**: Count of `fact_application_skills` by `dim_skill[skill_name]`
  (top 10, sort descending) — "top requested skills"
- **Pie/donut chart**: Application count by `status`
- **Slicer**: `dim_resume[version_name]` and `dim_source[source_name]` so
  you can filter the whole dashboard by resume or job board

## 6. Dashboard/slicer design notes

- Put the four card visuals at the top, exactly like the Excel dashboard's
  layout, so a reviewer instantly gets the headline numbers
- Add slicers for resume version and source at the top-right — this lets
  you answer "how did Resume_A do on LinkedIn specifically" live, which is
  a natural follow-up question in an interview demo
- Use a consistent color per resume version across every visual (Power BI
  does this automatically once you set it once in one visual's format pane)
