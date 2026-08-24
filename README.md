# Project 1: Job Application Intelligence System

A portfolio data analyst project that tracks a real job search — every
application, which resume was used, the source, and the outcome — and
answers the question every job hunt needs answered: **which resume
actually works, which job boards are worth the time, and what skill gap
is costing the most interviews?**

Built as project 1 of 3 in a data analyst portfolio series (see
`Three_Data_Analyst_Projects_Printable_Guide.pdf` for the full roadmap —
Project 2 is the Personal Financial Intelligence System, Project 3 is an
Apartment Decision Engine).

## The problem

Most job searches generate a spreadsheet nobody looks at twice. This
project turns that spreadsheet into an actual analysis: is one resume
version outperforming the others, is a specific job board a waste of
time, which companies respond fastest, and — via the Job Match Score
tool — which missing skill would unlock the most future applications if
learned next.

## What's in this repo

```
project1/
├── data/
│   ├── raw/              Deliberately messy raw export (mixed date formats,
│   │                     inconsistent Status casing, stray whitespace,
│   │                     duplicate "logged it twice" rows) to demonstrate
│   │                     real-world data cleaning
│   └── clean/            Cleaned, analysis-ready CSVs: applications,
│                          application_skills (normalized), resumes
├── python/
│   ├── generate_data.py       Produces the messy raw export (fixed seed)
│   ├── clean_data.py          Parses dates, normalizes casing, dedupes
│   ├── build_database.py      Loads cleaned data into a normalized SQLite database
│   ├── analysis.py            Full analysis: 6 dashboard answers + 5 charts
│   ├── job_match_score.py     The Job Match Score tool (CLI version)
│   └── build_powerbi_package.py   Generates the Power BI star-schema CSVs
├── sql/
│   ├── schema.sql            Table definitions (resumes, applications,
│   │                          application_skills) — 3 tables, 2 foreign keys
│   ├── queries.sql           12 analysis queries: aggregation, JOINs, CASE
│   │                          expressions, CTEs, window functions (RANK,
│   │                          PERCENT_RANK, running totals)
│   └── jobsearch.db          The SQLite database itself
├── excel/
│   └── Job_Application_Dashboard.xlsx   6 sheets: Dashboard (live SUMIFS/
│                                         COUNTIFS/XLOOKUP formulas), Raw Data,
│                                         Skills, Resumes, Job Match Score
│                                         (live formula tool), Instructions
├── powerbi/
│   ├── dim_*.csv, fact_*.csv    Star-schema tables ready to import
│   └── POWERBI_GUIDE.md         Step-by-step Power Query, data model, DAX guide
├── charts/
│   └── *.png                    5 charts from the Python analysis
├── PROJECT_1_TALKING_POINTS.md  Interview cheat sheet — 30-second pitch,
│                                 resume bullets, and answers to the
│                                 follow-up questions this project invites
└── README.md                    This file
```

## How the data flows

```
generate_data.py → data/raw/  →  clean_data.py (clean + dedupe)  →  data/clean/
                                                        │
                        ┌───────────────┬───────────────┼───────────────┐
                        ▼               ▼               ▼               ▼
                build_database.py   analysis.py   (Excel dashboard   build_powerbi_package.py
                        │               │            built manually       │
                        ▼               ▼            from clean data)     ▼
                sql/jobsearch.db   charts/*.png   excel/*.xlsx        powerbi/*.csv
```

This is the same brief followed in Project 2: **Applications → Python/SQL
→ Cleaning/Normalization → Analysis → Skill-Gap Scoring → Power BI.**

## Running it yourself

Requires Python 3.11+ with `pandas` and `matplotlib`
(`pip install pandas matplotlib`).

```bash
cd project1
python3 python/generate_data.py          # 1. generate raw (messy) applications
python3 python/clean_data.py             # 2. clean + dedupe
python3 python/build_database.py         # 3. load into SQLite
python3 python/analysis.py               # 4. run analysis, produce charts, print findings
python3 python/build_powerbi_package.py  # 5. build the Power BI CSV package
```

To query the database directly:
```bash
python3 -c "import sqlite3; print(sqlite3.connect('sql/jobsearch.db').execute(open('sql/queries.sql').read().split(';')[0]).fetchall())"
```
or open `sql/jobsearch.db` in any SQLite browser (DB Browser for SQLite, etc.)
and run the statements in `sql/queries.sql` directly.

To use the Job Match Score tool on a real posting:
```bash
python3 python/job_match_score.py \
  --required "SQL, Python, Power BI, Tableau, Machine Learning, AWS" \
  --have "Excel, SQL, Python, Power BI, Pandas, PivotTables, Data Cleaning, Data Visualization, Statistics, Communication"
```

## Dashboard questions answered

| Question | Where it's answered | Result on this dataset |
|---|---|---|
| How many applications, and what's the interview rate? | Excel Dashboard, SQL Q1, `analysis.py` | **185 applications**, 15.7% interview rate, 12 offers, 11.1 days avg. response |
| Which resume version performs best? | Excel Dashboard, SQL Q3, `charts/01_resume_performance.png` | **Resume_A_Analytics**, 22.2% interview rate (vs. 13.6% and 10.7% for the other two) |
| Which job board is actually worth the time? | Excel Dashboard, SQL Q4, `charts/02_source_performance.png` | **Indeed**, 22.2% interview rate — tied for best despite not being the highest-volume source |
| Which companies respond fastest? | Excel Dashboard, SQL Q5, `charts/03_fastest_responders.png` | **Stonebridge Consulting**, 1.0 day average |
| What skills show up most in postings? | Excel Dashboard, SQL Q6, `charts/04_top_skills.png` | **Machine Learning** (51 postings), Tableau (50), Python (47) |
| What's the status breakdown? | Excel Dashboard, SQL Q2, `charts/05_status_breakdown.png` | No Response 65, Rejected 51, Applied 40, Interview 17, Offer 12 |

## Advanced features

1. **Job Match Score tool** — scores a job posting's required skills
   against your current skills (simple overlap ratio, built live in both
   Excel formulas and `job_match_score.py`), and recommends a
   *prioritized* learning path: missing skills ranked by how often they
   appear across all 185 logged postings, so you learn the skill that
   unlocks the most future applications first.
2. **Skill-gap analysis (SQL Q10)** — a CTE-based query comparing how
   often each skill is requested vs. how often it actually shows up on
   applications that led to an interview or offer, surfacing which
   in-demand skills are genuinely correlated with getting responses.
3. **Salary-band analysis (SQL Q11)** — checks whether applying to
   higher-salary postings hurts response rate (it doesn't, on this data —
   the $60k-$75k band actually has the highest interview rate).
4. **Window-function analytics (SQL Q7-Q9)** — `RANK()` for salary
   ranking within resume version, a running-total of applications per
   month, and `PERCENT_RANK()` for each company's response-speed
   percentile.

## Data note

The underlying dataset (185 applications, 40 companies, 1,130
application-skill pairs) is the actual data this project's Excel
dashboard was built from. `generate_data.py` re-exports it in
deliberately messy raw form (mixed date formats, inconsistent casing,
stray whitespace, a few duplicate "logged it twice" rows) so
`clean_data.py` demonstrates real cleaning work rather than starting from
already-tidy input — the round-trip (`generate_data.py` → `clean_data.py`)
reproduces the original clean dataset exactly.

## Skills demonstrated

- **Excel:** live dashboard with SUMIFS/COUNTIFS/XLOOKUP formulas, a
  skill-matching formula tool (SUMPRODUCT/SEARCH), PivotTable-ready raw data
- **SQL:** normalized schema design (3 tables, foreign keys), aggregation,
  JOINs, CASE expressions, CTEs, window functions (RANK, PERCENT_RANK,
  running totals via `SUM() OVER`)
- **Python/Pandas:** data cleaning (mixed date formats, inconsistent
  casing, deduplication), skill-matching/recommendation logic, charting
- **Power BI:** star-schema data modeling, DAX measures (including time
  intelligence with `DATESMTD`/`DATEADD`), dashboard/slicer design

## Talking to this project in an interview

See `PROJECT_1_TALKING_POINTS.md` for the 30-second pitch, ready-made
resume bullets, and prepared answers to the questions this project tends
to invite ("why four tools instead of one," "walk me through the SQL,"
"what was the hardest part," "did you build this alone").
