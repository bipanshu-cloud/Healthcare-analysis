"""
Healthcare Patient Analytics — Dataset Generator
Generates 1,500 rows of realistic hospital patient records
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

random.seed(7)
np.random.seed(7)

# ── CONFIG ────────────────────────────────────────────────────────────────────
DISEASES = {
    "Cardiovascular": ["Heart Attack", "Heart Failure", "Arrhythmia", "Hypertension", "Stroke"],
    "Respiratory":    ["Pneumonia", "COPD", "Asthma", "Bronchitis", "Pulmonary Embolism"],
    "Neurological":   ["Epilepsy", "Migraine", "Parkinson's", "Dementia", "TIA"],
    "Orthopedic":     ["Hip Fracture", "Knee Replacement", "Spinal Stenosis", "Osteoporosis", "Back Pain"],
    "Gastrointestinal":["Appendicitis", "Colitis", "Pancreatitis", "GERD", "Liver Cirrhosis"],
    "Endocrine":      ["Diabetes Type 1", "Diabetes Type 2", "Thyroid Disorder", "Obesity", "Hypoglycemia"],
    "Infectious":     ["Sepsis", "UTI", "Cellulitis", "Meningitis", "COVID-19"],
    "Oncology":       ["Lung Cancer", "Breast Cancer", "Colon Cancer", "Leukemia", "Lymphoma"],
}

DEPARTMENTS = ["Cardiology", "Pulmonology", "Neurology", "Orthopedics",
               "Gastroenterology", "Endocrinology", "Infectious Disease", "Oncology"]

ADMISSION_TYPES  = ["Emergency", "Elective", "Urgent", "Observation"]
DISCHARGE_TYPES  = ["Home", "Transferred", "Against Medical Advice", "Expired", "Rehab Facility"]
INSURANCE_TYPES  = ["Private", "Medicare", "Medicaid", "Self-Pay", "Government"]
BLOOD_GROUPS     = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
GENDERS          = ["Male", "Female"]

# Avg LOS (days) and base cost per department
DEPT_CONFIG = {
    "Cardiology":         (5.5, 18000),
    "Pulmonology":        (4.8, 14000),
    "Neurology":          (4.2, 15000),
    "Orthopedics":        (3.8, 20000),
    "Gastroenterology":   (3.5, 11000),
    "Endocrinology":      (3.0,  9000),
    "Infectious Disease": (6.2, 13000),
    "Oncology":           (7.1, 25000),
}

def age_for_disease(disease):
    if any(d in disease for d in ["Heart","Stroke","COPD","Parkinson","Dementia","Hip","Knee","Osteo"]):
        return int(np.clip(np.random.normal(68, 12), 45, 95))
    if any(d in disease for d in ["Asthma","Epilepsy","Diabetes Type 1","Leukemia"]):
        return int(np.clip(np.random.normal(35, 15), 5, 60))
    return int(np.clip(np.random.normal(52, 18), 18, 90))

def generate_dataset(n=1500):
    rows = []
    start = datetime(2022, 1, 1)
    end   = datetime(2024, 6, 30)
    delta = (end - start).days
    patient_id = 100001

    for _ in range(n):
        dept = random.choices(DEPARTMENTS, weights=[18,12,12,14,10,10,12,12])[0]
        dept_idx   = DEPARTMENTS.index(dept)
        disease_cat= list(DISEASES.keys())[dept_idx]
        disease    = random.choice(DISEASES[disease_cat])

        admit_date = start + timedelta(days=random.randint(0, delta))
        avg_los, base_cost = DEPT_CONFIG[dept]
        los = max(1, int(np.random.normal(avg_los, avg_los * 0.4)))
        discharge_date = admit_date + timedelta(days=los)

        age    = age_for_disease(disease)
        gender = random.choice(GENDERS)

        # Severity 1-5
        severity = random.choices([1,2,3,4,5], weights=[10,25,35,20,10])[0]

        # Cost influenced by LOS, severity, department
        cost = round(base_cost * (los / avg_los) * (1 + severity * 0.12) * random.uniform(0.85, 1.15), 2)
        insurance = random.choices(INSURANCE_TYPES, weights=[30, 25, 20, 10, 15])[0]
        covered_pct = {"Private": 0.80, "Medicare": 0.75, "Medicaid": 0.65,
                       "Self-Pay": 0.00, "Government": 0.85}[insurance]
        insurance_covered = round(cost * covered_pct, 2)
        patient_paid      = round(cost - insurance_covered, 2)

        # Readmission: higher for elderly, severe, certain diseases
        readmit_prob = 0.10 + (severity - 1) * 0.04 + (age > 65) * 0.06
        if disease in ["Heart Failure","COPD","Sepsis","Diabetes Type 2"]:
            readmit_prob += 0.08
        is_readmission = 1 if random.random() < min(readmit_prob, 0.40) else 0

        # Mortality
        mort_prob = 0.02 + (severity == 5) * 0.08 + (age > 75) * 0.03
        discharge_type = random.choices(
            DISCHARGE_TYPES,
            weights=[60, 8, 3, mort_prob * 100, 14]
        )[0]

        rows.append({
            "patient_id":        patient_id,
            "admission_date":    admit_date.strftime("%Y-%m-%d"),
            "discharge_date":    discharge_date.strftime("%Y-%m-%d"),
            "year":              admit_date.year,
            "month":             admit_date.month,
            "month_name":        admit_date.strftime("%B"),
            "quarter":           f"Q{(admit_date.month-1)//3+1}",
            "age":               age,
            "age_group":         ("0-17" if age<18 else "18-35" if age<36 else
                                  "36-50" if age<51 else "51-65" if age<66 else "65+"),
            "gender":            gender,
            "blood_group":       random.choice(BLOOD_GROUPS),
            "department":        dept,
            "disease_category":  disease_cat,
            "diagnosis":         disease,
            "admission_type":    random.choices(ADMISSION_TYPES, weights=[40,30,20,10])[0],
            "discharge_type":    discharge_type,
            "severity_score":    severity,
            "length_of_stay":    los,
            "total_cost":        cost,
            "insurance_type":    insurance,
            "insurance_covered": insurance_covered,
            "patient_paid":      patient_paid,
            "is_readmission":    is_readmission,
            "num_procedures":    random.randint(1, severity + 2),
            "num_medications":   random.randint(1, severity + 3),
            "icu_days":          max(0, los - random.randint(los, los+3)) if severity >= 4 else 0,
            "satisfaction_score":round(random.gauss(3.8 - severity * 0.1, 0.7), 1),
        })
        patient_id += 1

    df = pd.DataFrame(rows)
    df["satisfaction_score"] = df["satisfaction_score"].clip(1.0, 5.0).round(1)
    df["admission_date"]     = pd.to_datetime(df["admission_date"])
    df["discharge_date"]     = pd.to_datetime(df["discharge_date"])
    return df.sort_values("admission_date").reset_index(drop=True)


if __name__ == "__main__":
    df  = generate_dataset(1500)
    out = os.path.join(os.path.dirname(__file__), "../data/patients.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    df.to_csv(out, index=False)
    print(f"✅ Dataset generated: {len(df):,} rows → {out}")
    print(df.dtypes)
    print(df.head(3).to_string())
