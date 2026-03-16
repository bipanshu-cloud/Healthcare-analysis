# 🏥 Healthcare Patient Analytics

A recruiter-ready data analytics portfolio project demonstrating:
**SQL · Python (Pandas) · Data Visualization · Clinical Business Analysis**

---

## 🗂 Project Structure

```
healthcare-analytics/
├── data/
│   ├── patients.csv          ← 1,500-row patient dataset
│   └── patients.db           ← SQLite database (auto-generated)
│
├── python_analysis/
│   ├── generate_data.py      ← Realistic patient data generator
│   └── analysis.py           ← Full Pandas analysis (10 sections)
│
├── sql/
│   ├── queries.sql           ← 12 production SQL queries
│   └── run_sql.py            ← Python SQLite runner
│
├── dashboard/
│   └── index.html            ← Interactive Chart.js dashboard
│
├── reports/                  ← Auto-generated CSV reports
│   ├── monthly_trends.csv
│   ├── department_performance.csv
│   ├── top_diagnoses.csv
│   ├── readmission_analysis.csv
│   ├── insurance_breakdown.csv
│   ├── age_group_analysis.csv
│   ├── severity_analysis.csv
│   └── quarterly_summary.csv
│
└── README.md
```

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install pandas numpy

# 2. Generate the dataset
py python_analysis/generate_data.py

# 3. Run full Python analysis
py python_analysis/analysis.py

# 4. Run SQL queries
py sql/run_sql.py

# 5. Open dashboard (no server needed)
# Just double-click: dashboard/index.html
```

---

## 📋 Dataset Fields (27 columns)

| Field | Description |
|-------|-------------|
| `patient_id` | Unique patient identifier |
| `admission_date` | Hospital admission date |
| `discharge_date` | Discharge date |
| `age` / `age_group` | Patient age & bracket |
| `gender` | Male / Female |
| `department` | Hospital department (8) |
| `disease_category` | Disease category (8) |
| `diagnosis` | Specific diagnosis (40 unique) |
| `admission_type` | Emergency / Elective / Urgent |
| `discharge_type` | Home / Transferred / Expired |
| `severity_score` | 1 (Mild) to 5 (Critical) |
| `length_of_stay` | Days hospitalized |
| `total_cost` | Full treatment cost |
| `insurance_type` | Private / Medicare / Medicaid |
| `insurance_covered` | Amount covered by insurance |
| `patient_paid` | Out-of-pocket amount |
| `is_readmission` | Readmitted within period (0/1) |
| `num_procedures` | Procedures performed |
| `num_medications` | Medications prescribed |
| `satisfaction_score` | Patient rating (1–5) |

---

## 🔍 Analyses Performed

### Python / Pandas (10 sections)
- ✅ Executive KPI summary
- ✅ Monthly admission trends + MoM change
- ✅ Department performance benchmarking
- ✅ Top 20 diagnoses by cases
- ✅ Readmission rate by department
- ✅ Cost & insurance coverage breakdown
- ✅ Age group health outcomes
- ✅ Severity score vs cost/mortality correlation
- ✅ Quarterly cost comparison
- ✅ 8 actionable clinical insights

### SQL (12 queries)
1. Executive KPI dashboard
2. Monthly admissions + MoM window function
3. Department performance
4. Top 15 diagnoses
5. Readmission risk factors
6. Insurance cost analysis
7. Age group health outcomes
8. Severity-cost correlation
9. Quarterly YoY comparison
10. High-cost patient identification
11. Admission type by department (CASE WHEN pivot)
12. Department ranking (RANK + window functions)

### Dashboard (8 charts)
- 8 KPI cards with clinical color coding
- Monthly admissions + cost dual-axis trend
- Department share donut
- Admission type breakdown
- Readmission rates horizontal bar (color-coded risk)
- Insurance stacked bar (covered vs patient burden)
- Age group outcomes (grouped bar)
- Severity distribution
- Top 15 diagnoses table with risk tags
- Quarterly cost trend

---

## 💡 Key Findings

1. **Orthopedics** has the highest readmission rate at **25.1%** — needs intervention
2. **Oncology** is the costliest department at **$5.9M** total
3. **Hypertension** is the most common diagnosis (**56 cases**)
4. Patients **65+** face the highest mortality rate at **8.0%**
5. **Self-pay patients (152)** face an average burden of **$20,332** — financial risk
6. **42.2% emergency admissions** — high unplanned care burden
7. Critical severity (score 5) patients cost **37% more** than mild cases
8. **Hip Fracture** has the highest readmission rate among diagnoses (**37%**)

---

## 🛠 Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3 | Data generation & orchestration |
| Pandas | Data wrangling & aggregation |
| NumPy | Statistical distributions |
| SQLite | SQL query demonstration |
| Chart.js | 8 interactive chart types |
| HTML/CSS | Clinical dashboard frontend |

---

## 📝 Skills Demonstrated for Resume

- **Healthcare Domain Knowledge**: LOS, readmission rates, severity scoring, mortality
- **Python / Pandas**: Multi-level groupby, lambda agg, window stats
- **SQL**: CTEs, LAG/LEAD, RANK, PARTITION BY, CASE WHEN pivots
- **Data Visualization**: Dual-axis, stacked bars, donut charts, risk-color encoding
- **Business Storytelling**: Converting data into 8 actionable clinical insights

---

*Built as a portfolio project to demonstrate healthcare data analytics skills.*
