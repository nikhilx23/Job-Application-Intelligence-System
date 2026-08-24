-- schema.sql — normalized schema for the Job Application Intelligence System
-- 3 tables, 2 foreign key relationships.

DROP TABLE IF EXISTS application_skills;
DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS resumes;

CREATE TABLE resumes (
    resume_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    version_name  TEXT NOT NULL UNIQUE,
    focus_area    TEXT NOT NULL
);

CREATE TABLE applications (
    application_id      TEXT PRIMARY KEY,
    company              TEXT NOT NULL,
    role_title            TEXT NOT NULL,
    location              TEXT,
    date_applied          TEXT NOT NULL,
    source                 TEXT NOT NULL,
    resume_id              INTEGER NOT NULL REFERENCES resumes(resume_id),
    salary_min             INTEGER,
    salary_max             INTEGER,
    status                  TEXT NOT NULL
        CHECK (status IN ('Applied','No Response','Rejected','Interview','Offer')),
    response_date           TEXT,
    interview_date           TEXT,
    response_time_days        INTEGER
);

-- Normalizes the free-text "skills required" from each job posting into
-- one row per (application, skill) instead of one comma-separated cell --
-- this is what makes it possible to COUNT / GROUP BY skill in SQL.
CREATE TABLE application_skills (
    application_id  TEXT NOT NULL REFERENCES applications(application_id),
    skill            TEXT NOT NULL,
    PRIMARY KEY (application_id, skill)
);

CREATE INDEX idx_applications_resume ON applications(resume_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_source ON applications(source);
CREATE INDEX idx_skills_skill ON application_skills(skill);
