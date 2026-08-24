# Project 1 — Talking Points & Resume Bullets

Keep this handy before interviews. It's the "how do I explain this project
in 30 seconds, then survive follow-up questions" cheat sheet.

## The 30-second explanation

"I built a system to track my own job search — every application, which
resume I used, the source, and the outcome — because I noticed I had no
idea which of my resumes or job boards were actually working. I built it
four ways on purpose: as an Excel dashboard, a normalized SQL database,
a Python cleaning/analysis pipeline, and a Power BI dashboard, so I could
demonstrate the same analysis across the tools a data analyst actually
uses day to day. All four agree on the numbers, which I check on purpose."

## Resume bullets (edit numbers once you're using your real data)

- Built a job application tracking system across Excel, SQL, and Python
  to analyze application outcomes, achieving cross-tool consistency on
  key metrics (interview rate, resume performance, response time).
- Designed a normalized SQL schema (3 tables, foreign keys) and wrote
  queries using JOINs, CASE expressions, CTEs, and window functions to
  answer job-search performance questions.
- Built a Python data-cleaning pipeline (Pandas) handling inconsistent
  casing, mixed date formats, and missing values from raw exports.
- Built a keyword-extraction tool that scores job description fit against
  a personal skill set and recommends a prioritized learning path.

## If asked "walk me through the SQL"

Point to `sql/queries.sql`, query #4 (resume performance) — it's the
simplest one that shows a real JOIN:

```sql
SELECT r.version_name, COUNT(a.application_id) AS applications, ...
FROM applications a
JOIN resumes r ON r.resume_id = a.resume_id
GROUP BY r.version_name
```

Plain English: "applications" holds one row per job I applied to, with a
resume_id number instead of the resume name. "resumes" is a small lookup
table that says what each number means. The JOIN glues them together so
I can group by resume name instead of by number. This is a normalized
schema — the same idea you use anytime you have a repeated category
(status, company, resume version) instead of retyping the full name on
every row.

## If asked "why Excel AND SQL AND Python AND Power BI — isn't that redundant?"

That's intentional, and a good answer: "Redundant on purpose. A data
analyst role usually touches more than one of these day to day, and I
wanted to prove I could get the same right answer regardless of tool —
that's also just good practice, cross-checking your own analysis."

## If asked "what was the hardest part?"

Honest answer to give: normalizing the skills data. Job descriptions are
free text ("SQL, Excel, Python" in one cell) — turning that into
something you can actually COUNT and GROUP BY required either a separate
`application_skills` table (SQL/Power BI) or a `SUMPRODUCT`/`SEARCH`
formula (Excel) or a keyword-taxonomy dictionary (Python). Three
different tools, three different techniques, same underlying problem.

## If asked "did you build this alone?"

Be straightforward if this comes up: you used Claude as a coding
assistant/tutor to scaffold it, the way you might use Stack Overflow or a
bootcamp mentor — and you should be able to explain every piece because
you went through it. If you haven't gone through a piece yet, do that
before claiming it in an interview.
