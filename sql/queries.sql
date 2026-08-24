-- queries.sql — 12 analysis queries answering the dashboard's questions.
-- Demonstrates aggregation, JOINs, CASE expressions, CTEs, and window
-- functions (RANK, PERCENT_RANK, running totals).

-- Q1. Overall funnel: total applications, interview rate, offers, avg response time
SELECT
    COUNT(*)                                                        AS total_applications,
    ROUND(100.0 * SUM(CASE WHEN status IN ('Interview','Offer') THEN 1 ELSE 0 END)
          / COUNT(*), 1)                                             AS interview_rate_pct,
    SUM(CASE WHEN status = 'Offer' THEN 1 ELSE 0 END)                AS offers,
    ROUND(AVG(response_time_days), 1)                                AS avg_response_days
FROM applications;

-- Q2. Status breakdown
SELECT status, COUNT(*) AS count
FROM applications
GROUP BY status
ORDER BY count DESC;

-- Q3. Resume performance -- which resume version gets the most interviews?
-- (This is the query referenced in PROJECT_1_TALKING_POINTS.md.)
SELECT r.version_name,
       COUNT(a.application_id)                                        AS applications,
       SUM(CASE WHEN a.status IN ('Interview','Offer') THEN 1 ELSE 0 END) AS interviews,
       ROUND(100.0 * SUM(CASE WHEN a.status IN ('Interview','Offer') THEN 1 ELSE 0 END)
             / COUNT(a.application_id), 1)                             AS interview_rate_pct
FROM applications a
JOIN resumes r ON r.resume_id = a.resume_id
GROUP BY r.version_name
ORDER BY interview_rate_pct DESC;

-- Q4. Source performance -- which job board actually produces interviews?
SELECT source,
       COUNT(*)                                                        AS applications,
       SUM(CASE WHEN status IN ('Interview','Offer') THEN 1 ELSE 0 END) AS interviews,
       ROUND(100.0 * SUM(CASE WHEN status IN ('Interview','Offer') THEN 1 ELSE 0 END)
             / COUNT(*), 1)                                             AS interview_rate_pct
FROM applications
GROUP BY source
ORDER BY interview_rate_pct DESC;

-- Q5. Fastest-responding companies (top 8, min. one recorded response)
SELECT company, ROUND(AVG(response_time_days), 1) AS avg_response_days
FROM applications
WHERE response_time_days IS NOT NULL
GROUP BY company
ORDER BY avg_response_days ASC
LIMIT 8;

-- Q6. Top requested skills across all logged postings
SELECT skill, COUNT(*) AS times_requested
FROM application_skills
GROUP BY skill
ORDER BY times_requested DESC
LIMIT 10;

-- Q7. Salary range offered, by resume version (window function: RANK)
SELECT version_name, role_title, salary_min, salary_max,
       RANK() OVER (PARTITION BY version_name ORDER BY salary_max DESC) AS salary_rank
FROM applications a
JOIN resumes r ON r.resume_id = a.resume_id
WHERE status IN ('Interview', 'Offer');

-- Q8. Applications per month, with a running total (window function)
SELECT strftime('%Y-%m', date_applied) AS month,
       COUNT(*) AS applications_this_month,
       SUM(COUNT(*)) OVER (ORDER BY strftime('%Y-%m', date_applied)) AS running_total
FROM applications
GROUP BY month
ORDER BY month;

-- Q9. Percentile rank of each company's response speed (window function: PERCENT_RANK)
SELECT company, response_time_days,
       ROUND(PERCENT_RANK() OVER (ORDER BY response_time_days), 2) AS speed_percentile
FROM applications
WHERE response_time_days IS NOT NULL
ORDER BY speed_percentile;

-- Q10. Skill gap: skills frequently requested but rarely present on
-- applications that led to an interview or offer (CTE)
WITH interview_apps AS (
    SELECT application_id FROM applications WHERE status IN ('Interview','Offer')
),
skill_demand AS (
    SELECT skill, COUNT(*) AS demand FROM application_skills GROUP BY skill
),
skill_on_winners AS (
    SELECT skill, COUNT(*) AS wins
    FROM application_skills
    WHERE application_id IN (SELECT application_id FROM interview_apps)
    GROUP BY skill
)
SELECT d.skill, d.demand,
       COALESCE(w.wins, 0) AS wins_with_this_skill,
       ROUND(100.0 * COALESCE(w.wins, 0) / d.demand, 1) AS win_rate_pct
FROM skill_demand d
LEFT JOIN skill_on_winners w ON w.skill = d.skill
ORDER BY d.demand DESC
LIMIT 10;

-- Q11. Salary band vs. outcome -- does asking for more money hurt response rate?
SELECT
    CASE
        WHEN salary_max < 60000 THEN 'Under $60k'
        WHEN salary_max < 75000 THEN '$60k-$75k'
        ELSE '$75k+'
    END AS salary_band,
    COUNT(*) AS applications,
    ROUND(100.0 * SUM(CASE WHEN status IN ('Interview','Offer') THEN 1 ELSE 0 END)
          / COUNT(*), 1) AS interview_rate_pct
FROM applications
GROUP BY salary_band
ORDER BY salary_band;

-- Q12. Companies applied to more than once (data-quality / dedup check)
SELECT company, COUNT(*) AS times_applied
FROM applications
GROUP BY company
HAVING COUNT(*) > 1
ORDER BY times_applied DESC;
