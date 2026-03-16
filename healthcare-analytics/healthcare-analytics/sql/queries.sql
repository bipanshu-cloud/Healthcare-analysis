-- ============================================================
--  Healthcare Patient Analytics — SQL Queries
--  Compatible with SQLite, PostgreSQL, MySQL
-- ============================================================

-- ── TABLE SCHEMA ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS patients (
    patient_id          INTEGER PRIMARY KEY,
    admission_date      DATE,
    discharge_date      DATE,
    year                INTEGER,
    month               INTEGER,
    month_name          VARCHAR(20),
    quarter             VARCHAR(5),
    age                 INTEGER,
    age_group           VARCHAR(10),
    gender              VARCHAR(10),
    blood_group         VARCHAR(5),
    department          VARCHAR(50),
    disease_category    VARCHAR(50),
    diagnosis           VARCHAR(100),
    admission_type      VARCHAR(20),
    discharge_type      VARCHAR(30),
    severity_score      INTEGER,
    length_of_stay      INTEGER,
    total_cost          DECIMAL(12,2),
    insurance_type      VARCHAR(20),
    insurance_covered   DECIMAL(12,2),
    patient_paid        DECIMAL(12,2),
    is_readmission      INTEGER,
    num_procedures      INTEGER,
    num_medications     INTEGER,
    icu_days            INTEGER,
    satisfaction_score  DECIMAL(3,1)
);


-- ── Q1: Executive KPI Dashboard ──────────────────────────────
SELECT
    COUNT(*)                                                    AS total_patients,
    ROUND(SUM(total_cost), 0)                                   AS total_revenue,
    ROUND(AVG(total_cost), 2)                                   AS avg_cost_per_patient,
    ROUND(AVG(length_of_stay), 1)                               AS avg_los_days,
    ROUND(AVG(is_readmission) * 100, 1)                         AS readmission_rate_pct,
    ROUND(AVG(satisfaction_score), 2)                           AS avg_satisfaction,
    COUNT(CASE WHEN discharge_type = 'Expired' THEN 1 END)      AS total_deaths,
    ROUND(COUNT(CASE WHEN discharge_type = 'Expired' THEN 1 END)
          * 100.0 / COUNT(*), 1)                                AS mortality_rate_pct,
    COUNT(CASE WHEN admission_type = 'Emergency' THEN 1 END)    AS emergency_admissions,
    COUNT(CASE WHEN insurance_type = 'Self-Pay' THEN 1 END)     AS self_pay_patients
FROM patients;


-- ── Q2: Monthly Admissions + MoM Change (Window Function) ───
WITH monthly AS (
    SELECT
        year, month, month_name,
        COUNT(*)                        AS admissions,
        ROUND(AVG(total_cost), 0)       AS avg_cost,
        ROUND(AVG(length_of_stay), 1)   AS avg_los,
        ROUND(AVG(is_readmission)*100,1)AS readmit_pct
    FROM patients
    GROUP BY year, month, month_name
)
SELECT *,
    LAG(admissions) OVER (ORDER BY year, month)       AS prev_admissions,
    ROUND(
        (admissions - LAG(admissions) OVER (ORDER BY year, month))
        * 100.0 / NULLIF(LAG(admissions) OVER (ORDER BY year, month), 0),
    1) AS mom_change_pct
FROM monthly
ORDER BY year, month;


-- ── Q3: Department Performance ────────────────────────────────
SELECT
    department,
    COUNT(*)                                    AS patients,
    ROUND(SUM(total_cost), 0)                   AS total_cost,
    ROUND(AVG(total_cost), 0)                   AS avg_cost,
    ROUND(AVG(length_of_stay), 1)               AS avg_los,
    ROUND(AVG(is_readmission) * 100, 1)         AS readmit_rate_pct,
    ROUND(AVG(severity_score), 2)               AS avg_severity,
    ROUND(AVG(satisfaction_score), 2)           AS avg_satisfaction,
    COUNT(CASE WHEN discharge_type='Expired' THEN 1 END) AS deaths,
    ROUND(COUNT(CASE WHEN discharge_type='Expired' THEN 1 END)*100.0/COUNT(*),1) AS mortality_pct
FROM patients
GROUP BY department
ORDER BY total_cost DESC;


-- ── Q4: Top 15 Diagnoses by Cases ────────────────────────────
SELECT
    diagnosis,
    disease_category,
    COUNT(*)                                    AS total_cases,
    ROUND(AVG(total_cost), 0)                   AS avg_cost,
    ROUND(AVG(length_of_stay), 1)               AS avg_los,
    ROUND(AVG(is_readmission)*100, 1)           AS readmit_pct,
    ROUND(COUNT(CASE WHEN discharge_type='Expired' THEN 1 END)*100.0/COUNT(*),1) AS mortality_pct,
    ROUND(AVG(severity_score), 2)               AS avg_severity
FROM patients
GROUP BY diagnosis, disease_category
ORDER BY total_cases DESC
LIMIT 15;


-- ── Q5: Readmission Risk Factors (High-Risk Diagnoses) ───────
SELECT
    diagnosis,
    COUNT(*)                                    AS total_cases,
    SUM(is_readmission)                         AS readmissions,
    ROUND(AVG(is_readmission)*100, 1)           AS readmit_rate_pct,
    ROUND(AVG(total_cost), 0)                   AS avg_cost,
    ROUND(AVG(age), 1)                          AS avg_patient_age
FROM patients
GROUP BY diagnosis
HAVING COUNT(*) >= 20
ORDER BY readmit_rate_pct DESC
LIMIT 10;


-- ── Q6: Cost Analysis by Insurance Type ──────────────────────
SELECT
    insurance_type,
    COUNT(*)                                     AS patients,
    ROUND(AVG(total_cost), 2)                    AS avg_total_cost,
    ROUND(AVG(insurance_covered), 2)             AS avg_covered,
    ROUND(AVG(patient_paid), 2)                  AS avg_patient_pays,
    ROUND(AVG(insurance_covered)/AVG(total_cost)*100, 1) AS coverage_pct,
    ROUND(SUM(patient_paid), 0)                  AS total_patient_burden
FROM patients
GROUP BY insurance_type
ORDER BY patients DESC;


-- ── Q7: Age Group Health Outcomes ─────────────────────────────
SELECT
    age_group,
    COUNT(*)                                        AS patients,
    ROUND(AVG(total_cost), 0)                       AS avg_cost,
    ROUND(AVG(length_of_stay), 1)                   AS avg_los,
    ROUND(AVG(is_readmission)*100, 1)               AS readmit_pct,
    ROUND(AVG(severity_score), 2)                   AS avg_severity,
    ROUND(COUNT(CASE WHEN discharge_type='Expired' THEN 1 END)*100.0/COUNT(*),1) AS mortality_pct,
    ROUND(AVG(satisfaction_score), 2)               AS avg_satisfaction
FROM patients
GROUP BY age_group
ORDER BY CASE age_group
    WHEN '0-17'  THEN 1 WHEN '18-35' THEN 2
    WHEN '36-50' THEN 3 WHEN '51-65' THEN 4 ELSE 5 END;


-- ── Q8: Severity to Cost Correlation ─────────────────────────
SELECT
    severity_score,
    CASE severity_score
        WHEN 1 THEN 'Mild'     WHEN 2 THEN 'Moderate'
        WHEN 3 THEN 'Serious'  WHEN 4 THEN 'Severe'
        ELSE 'Critical'
    END                                             AS severity_label,
    COUNT(*)                                        AS patients,
    ROUND(AVG(total_cost), 0)                       AS avg_cost,
    ROUND(AVG(length_of_stay), 1)                   AS avg_los,
    ROUND(AVG(is_readmission)*100, 1)               AS readmit_pct,
    ROUND(COUNT(CASE WHEN discharge_type='Expired' THEN 1 END)*100.0/COUNT(*),1) AS mortality_pct
FROM patients
GROUP BY severity_score
ORDER BY severity_score;


-- ── Q9: Quarterly YoY Comparison ─────────────────────────────
SELECT
    year, quarter,
    COUNT(*)                                AS admissions,
    ROUND(SUM(total_cost), 0)               AS total_cost,
    ROUND(AVG(total_cost), 0)               AS avg_cost,
    ROUND(AVG(is_readmission)*100, 1)       AS readmit_pct,
    ROUND(AVG(length_of_stay), 1)           AS avg_los,
    ROUND(AVG(satisfaction_score), 2)       AS avg_satisfaction
FROM patients
GROUP BY year, quarter
ORDER BY year, quarter;


-- ── Q10: High-Cost Patients (Top Decile) ─────────────────────
SELECT
    patient_id, age, gender, department, diagnosis,
    severity_score, length_of_stay,
    ROUND(total_cost, 2)        AS total_cost,
    insurance_type,
    ROUND(patient_paid, 2)      AS patient_paid,
    discharge_type,
    is_readmission
FROM patients
WHERE total_cost >= (
    SELECT PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY total_cost)
    FROM patients
)
ORDER BY total_cost DESC
LIMIT 20;
-- Note: For SQLite use: SELECT total_cost FROM patients ORDER BY total_cost DESC LIMIT (SELECT CAST(COUNT(*)*0.1 AS INT) FROM patients)


-- ── Q11: Admission Type Distribution by Department ───────────
SELECT
    department,
    COUNT(*) AS total,
    SUM(CASE WHEN admission_type='Emergency' THEN 1 ELSE 0 END)    AS emergency,
    SUM(CASE WHEN admission_type='Elective'  THEN 1 ELSE 0 END)    AS elective,
    SUM(CASE WHEN admission_type='Urgent'    THEN 1 ELSE 0 END)    AS urgent,
    ROUND(SUM(CASE WHEN admission_type='Emergency' THEN 1 ELSE 0 END)*100.0/COUNT(*),1) AS emergency_pct
FROM patients
GROUP BY department
ORDER BY emergency_pct DESC;


-- ── Q12: Department Rank by Readmission (Window Function) ────
SELECT
    department,
    patients,
    readmit_rate_pct,
    RANK() OVER (ORDER BY readmit_rate_pct DESC) AS readmit_rank,
    RANK() OVER (ORDER BY avg_cost DESC)         AS cost_rank
FROM (
    SELECT
        department,
        COUNT(*)                            AS patients,
        ROUND(AVG(is_readmission)*100, 1)   AS readmit_rate_pct,
        ROUND(AVG(total_cost), 0)           AS avg_cost
    FROM patients
    GROUP BY department
) sub
ORDER BY readmit_rank;
