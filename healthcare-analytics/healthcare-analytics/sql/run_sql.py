"""
Run SQL queries on healthcare data using SQLite
"""
import sqlite3, pandas as pd, os

BASE = os.path.dirname(os.path.abspath(__file__))
df   = pd.read_csv(os.path.join(BASE, "../data/patients.csv"))
db   = os.path.join(BASE, "../data/patients.db")

conn = sqlite3.connect(db)
df.to_sql("patients", conn, if_exists="replace", index=False)
print(f"✅ Loaded {len(df):,} rows into SQLite → {db}\n")

queries = {
    "Executive KPIs": """
        SELECT COUNT(*) total_patients, ROUND(SUM(total_cost),0) total_cost,
               ROUND(AVG(total_cost),2) avg_cost, ROUND(AVG(length_of_stay),1) avg_los,
               ROUND(AVG(is_readmission)*100,1) readmit_pct,
               ROUND(AVG(satisfaction_score),2) avg_satisfaction
        FROM patients
    """,
    "Department Performance": """
        SELECT department, COUNT(*) patients, ROUND(SUM(total_cost),0) total_cost,
               ROUND(AVG(is_readmission)*100,1) readmit_pct,
               ROUND(AVG(length_of_stay),1) avg_los
        FROM patients GROUP BY department ORDER BY total_cost DESC
    """,
    "Top 10 Diagnoses": """
        SELECT diagnosis, COUNT(*) cases, ROUND(AVG(total_cost),0) avg_cost,
               ROUND(AVG(is_readmission)*100,1) readmit_pct
        FROM patients GROUP BY diagnosis ORDER BY cases DESC LIMIT 10
    """,
    "Insurance Breakdown": """
        SELECT insurance_type, COUNT(*) patients,
               ROUND(AVG(total_cost),0) avg_cost,
               ROUND(AVG(patient_paid),0) patient_pays
        FROM patients GROUP BY insurance_type ORDER BY patients DESC
    """,
    "Age Group Outcomes": """
        SELECT age_group, COUNT(*) patients,
               ROUND(AVG(total_cost),0) avg_cost,
               ROUND(AVG(is_readmission)*100,1) readmit_pct,
               ROUND(COUNT(CASE WHEN discharge_type='Expired' THEN 1 END)*100.0/COUNT(*),1) mortality_pct
        FROM patients GROUP BY age_group
        ORDER BY CASE age_group WHEN '0-17' THEN 1 WHEN '18-35' THEN 2
                 WHEN '36-50' THEN 3 WHEN '51-65' THEN 4 ELSE 5 END
    """,
}

for name, q in queries.items():
    print(f"── {name} ──")
    print(pd.read_sql(q, conn).to_string(index=False))
    print()

conn.close()
print("✅ All SQL queries executed successfully.")
