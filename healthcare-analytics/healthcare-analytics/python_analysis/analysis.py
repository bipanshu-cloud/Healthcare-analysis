"""
Healthcare Patient Analytics — Full Python / Pandas Analysis
=============================================================
Covers:
  1. Executive Summary KPIs
  2. Monthly Admission Trends
  3. Disease & Department Analysis
  4. Readmission Rate Analysis
  5. Cost & Insurance Breakdown
  6. Age Group & Demographics
  7. Length of Stay Analysis
  8. Severity & Mortality Insights
  9. Patient Satisfaction
 10. Key Recommendations
"""

import pandas as pd
import numpy as np
import os, warnings
warnings.filterwarnings("ignore")

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "../data/patients.csv")
OUT  = os.path.join(BASE, "../reports")
os.makedirs(OUT, exist_ok=True)

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(DATA, parse_dates=["admission_date","discharge_date"])
print(f"\n{'='*65}")
print(f"  HEALTHCARE PATIENT ANALYTICS — FULL REPORT")
print(f"{'='*65}")
print(f"  Records : {len(df):,} patients")
print(f"  Period  : {df['admission_date'].min().date()} → {df['admission_date'].max().date()}")

# ── 1. EXECUTIVE KPIs ─────────────────────────────────────────────────────────
print(f"\n{'─'*65}")
print("  📊 EXECUTIVE KPIs")
print(f"{'─'*65}")
kpis = {
    "Total Patients":         f"{len(df):,}",
    "Total Revenue (costs)":  f"${df['total_cost'].sum():,.0f}",
    "Avg Cost per Patient":   f"${df['total_cost'].mean():,.2f}",
    "Avg Length of Stay":     f"{df['length_of_stay'].mean():.1f} days",
    "Overall Readmission Rate":f"{df['is_readmission'].mean()*100:.1f}%",
    "ICU Admissions":         f"{(df['icu_days']>0).sum():,} ({(df['icu_days']>0).mean()*100:.1f}%)",
    "Avg Satisfaction Score": f"{df['satisfaction_score'].mean():.2f} / 5.0",
    "Expired Patients":       f"{(df['discharge_type']=='Expired').sum():,} ({(df['discharge_type']=='Expired').mean()*100:.1f}%)",
    "Emergency Admissions":   f"{(df['admission_type']=='Emergency').sum():,} ({(df['admission_type']=='Emergency').mean()*100:.1f}%)",
    "Self-Pay Patients":      f"{(df['insurance_type']=='Self-Pay').sum():,}",
}
for k, v in kpis.items():
    print(f"  {k:<30} {v}")

# ── 2. MONTHLY ADMISSIONS ─────────────────────────────────────────────────────
monthly = (
    df.groupby(["year","month","month_name"])
    .agg(admissions=("patient_id","count"),
         avg_cost=("total_cost","mean"),
         avg_los=("length_of_stay","mean"),
         readmit_rate=("is_readmission","mean"))
    .reset_index().sort_values(["year","month"])
)
monthly["mom_change"] = monthly["admissions"].pct_change() * 100
monthly["readmit_rate"] = (monthly["readmit_rate"] * 100).round(1)
monthly["avg_cost"] = monthly["avg_cost"].round(0)
monthly["avg_los"]  = monthly["avg_los"].round(1)

print(f"\n{'─'*65}")
print("  📅 MONTHLY ADMISSION TRENDS")
print(f"{'─'*65}")
print(f"  {'Month':<12} {'Year':<6} {'Admits':>7} {'MoM%':>8} {'Avg Cost':>10} {'Avg LOS':>8} {'Readmit%':>9}")
print(f"  {'─'*12} {'─'*6} {'─'*7} {'─'*8} {'─'*10} {'─'*8} {'─'*9}")
for _, r in monthly.iterrows():
    g = f"{r['mom_change']:+.1f}%" if pd.notna(r["mom_change"]) else "  —"
    print(f"  {r['month_name']:<12} {int(r['year']):<6} {int(r['admissions']):>7,} {g:>8} ${r['avg_cost']:>9,.0f} {r['avg_los']:>7.1f}d {r['readmit_rate']:>8.1f}%")
monthly.to_csv(f"{OUT}/monthly_trends.csv", index=False)

# ── 3. DEPARTMENT PERFORMANCE ─────────────────────────────────────────────────
dept = (
    df.groupby("department")
    .agg(patients=("patient_id","count"),
         total_cost=("total_cost","sum"),
         avg_cost=("total_cost","mean"),
         avg_los=("length_of_stay","mean"),
         readmit_rate=("is_readmission","mean"),
         avg_severity=("severity_score","mean"),
         avg_satisfaction=("satisfaction_score","mean"))
    .sort_values("total_cost", ascending=False)
    .reset_index()
)
dept["readmit_rate"] = (dept["readmit_rate"]*100).round(1)

print(f"\n{'─'*65}")
print("  🏥 DEPARTMENT PERFORMANCE")
print(f"{'─'*65}")
print(f"  {'Department':<22} {'Patients':>8} {'Total Cost':>12} {'Avg LOS':>8} {'Readmit%':>9} {'Sev':>5} {'Sat':>5}")
print(f"  {'─'*22} {'─'*8} {'─'*12} {'─'*8} {'─'*9} {'─'*5} {'─'*5}")
for _, r in dept.iterrows():
    print(f"  {r['department']:<22} {r['patients']:>8,} ${r['total_cost']:>11,.0f} {r['avg_los']:>7.1f}d {r['readmit_rate']:>8.1f}% {r['avg_severity']:>5.1f} {r['avg_satisfaction']:>5.2f}")
dept.to_csv(f"{OUT}/department_performance.csv", index=False)

# ── 4. TOP DIAGNOSES ──────────────────────────────────────────────────────────
diag = (
    df.groupby(["disease_category","diagnosis"])
    .agg(cases=("patient_id","count"),
         avg_cost=("total_cost","mean"),
         avg_los=("length_of_stay","mean"),
         readmit_rate=("is_readmission","mean"),
         mortality=("discharge_type", lambda x: (x=="Expired").mean()))
    .sort_values("cases", ascending=False)
    .reset_index().head(20)
)
diag["readmit_rate"] = (diag["readmit_rate"]*100).round(1)
diag["mortality"]    = (diag["mortality"]*100).round(1)

print(f"\n{'─'*65}")
print("  🦠 TOP 20 DIAGNOSES")
print(f"{'─'*65}")
print(f"  {'Diagnosis':<25} {'Cases':>6} {'Avg Cost':>10} {'Avg LOS':>8} {'Readmit%':>9} {'Mort%':>6}")
print(f"  {'─'*25} {'─'*6} {'─'*10} {'─'*8} {'─'*9} {'─'*6}")
for _, r in diag.iterrows():
    print(f"  {r['diagnosis']:<25} {r['cases']:>6,} ${r['avg_cost']:>9,.0f} {r['avg_los']:>7.1f}d {r['readmit_rate']:>8.1f}% {r['mortality']:>5.1f}%")
diag.to_csv(f"{OUT}/top_diagnoses.csv", index=False)

# ── 5. READMISSION ANALYSIS ───────────────────────────────────────────────────
readmit = (
    df.groupby("department")
    .agg(total=("patient_id","count"),
         readmissions=("is_readmission","sum"),
         rate=("is_readmission","mean"),
         avg_cost_readmit=("total_cost", lambda x: x[df.loc[x.index,"is_readmission"]==1].mean()))
    .reset_index()
    .sort_values("rate", ascending=False)
)
readmit["rate_pct"] = (readmit["rate"]*100).round(1)

print(f"\n{'─'*65}")
print("  🔁 READMISSION RATES BY DEPARTMENT")
print(f"{'─'*65}")
print(f"  {'Department':<22} {'Total':>7} {'Readmits':>9} {'Rate':>7} {'Avg Cost (Readmit)':>20}")
print(f"  {'─'*22} {'─'*7} {'─'*9} {'─'*7} {'─'*20}")
for _, r in readmit.iterrows():
    print(f"  {r['department']:<22} {r['total']:>7,} {r['readmissions']:>9,} {r['rate_pct']:>6.1f}% ${r['avg_cost_readmit']:>19,.0f}")
readmit.to_csv(f"{OUT}/readmission_analysis.csv", index=False)

# ── 6. COST & INSURANCE BREAKDOWN ────────────────────────────────────────────
ins = (
    df.groupby("insurance_type")
    .agg(patients=("patient_id","count"),
         total_cost=("total_cost","sum"),
         avg_cost=("total_cost","mean"),
         avg_covered=("insurance_covered","mean"),
         avg_patient_paid=("patient_paid","mean"),
         coverage_rate=("insurance_covered",lambda x: (x/df.loc[x.index,"total_cost"]).mean()))
    .reset_index()
    .sort_values("patients", ascending=False)
)
ins["coverage_rate"] = (ins["coverage_rate"]*100).round(1)

print(f"\n{'─'*65}")
print("  💰 INSURANCE & COST BREAKDOWN")
print(f"{'─'*65}")
print(f"  {'Insurance':<14} {'Patients':>8} {'Avg Cost':>10} {'Avg Covered':>12} {'Patient Pays':>13} {'Coverage%':>10}")
print(f"  {'─'*14} {'─'*8} {'─'*10} {'─'*12} {'─'*13} {'─'*10}")
for _, r in ins.iterrows():
    print(f"  {r['insurance_type']:<14} {r['patients']:>8,} ${r['avg_cost']:>9,.0f} ${r['avg_covered']:>11,.0f} ${r['avg_patient_paid']:>12,.0f} {r['coverage_rate']:>9.1f}%")
ins.to_csv(f"{OUT}/insurance_breakdown.csv", index=False)

# ── 7. AGE GROUP ANALYSIS ─────────────────────────────────────────────────────
age_g = (
    df.groupby("age_group")
    .agg(patients=("patient_id","count"),
         avg_cost=("total_cost","mean"),
         avg_los=("length_of_stay","mean"),
         readmit_rate=("is_readmission","mean"),
         avg_severity=("severity_score","mean"),
         mortality=("discharge_type", lambda x: (x=="Expired").mean()))
    .reset_index()
)
order = ["0-17","18-35","36-50","51-65","65+"]
age_g["age_group"] = pd.Categorical(age_g["age_group"], categories=order, ordered=True)
age_g = age_g.sort_values("age_group")
age_g["readmit_rate"] = (age_g["readmit_rate"]*100).round(1)
age_g["mortality"]    = (age_g["mortality"]*100).round(1)

print(f"\n{'─'*65}")
print("  👥 AGE GROUP ANALYSIS")
print(f"{'─'*65}")
print(f"  {'Age Group':<10} {'Patients':>9} {'Avg Cost':>10} {'Avg LOS':>8} {'Readmit%':>9} {'Severity':>9} {'Mort%':>6}")
print(f"  {'─'*10} {'─'*9} {'─'*10} {'─'*8} {'─'*9} {'─'*9} {'─'*6}")
for _, r in age_g.iterrows():
    print(f"  {r['age_group']:<10} {r['patients']:>9,} ${r['avg_cost']:>9,.0f} {r['avg_los']:>7.1f}d {r['readmit_rate']:>8.1f}% {r['avg_severity']:>9.2f} {r['mortality']:>5.1f}%")
age_g.to_csv(f"{OUT}/age_group_analysis.csv", index=False)

# ── 8. SEVERITY ANALYSIS ──────────────────────────────────────────────────────
sev = (
    df.groupby("severity_score")
    .agg(patients=("patient_id","count"),
         avg_cost=("total_cost","mean"),
         avg_los=("length_of_stay","mean"),
         readmit_rate=("is_readmission","mean"),
         icu_rate=("icu_days", lambda x: (x>0).mean()),
         mortality=("discharge_type", lambda x: (x=="Expired").mean()),
         avg_satisfaction=("satisfaction_score","mean"))
    .reset_index()
)
sev["readmit_rate"]= (sev["readmit_rate"]*100).round(1)
sev["mortality"]   = (sev["mortality"]*100).round(1)
sev["icu_rate"]    = (sev["icu_rate"]*100).round(1)

print(f"\n{'─'*65}")
print("  ⚕️  SEVERITY SCORE ANALYSIS (1=Mild → 5=Critical)")
print(f"{'─'*65}")
print(f"  {'Severity':<10} {'Patients':>9} {'Avg Cost':>10} {'Avg LOS':>8} {'Readmit%':>9} {'ICU%':>6} {'Mort%':>6} {'Satisf':>7}")
print(f"  {'─'*10} {'─'*9} {'─'*10} {'─'*8} {'─'*9} {'─'*6} {'─'*6} {'─'*7}")
labels = {1:"Mild",2:"Moderate",3:"Serious",4:"Severe",5:"Critical"}
for _, r in sev.iterrows():
    label = f"{int(r['severity_score'])} - {labels[int(r['severity_score'])]}"
    print(f"  {label:<10} {r['patients']:>9,} ${r['avg_cost']:>9,.0f} {r['avg_los']:>7.1f}d {r['readmit_rate']:>8.1f}% {r['icu_rate']:>5.1f}% {r['mortality']:>5.1f}% {r['avg_satisfaction']:>7.2f}")
sev.to_csv(f"{OUT}/severity_analysis.csv", index=False)

# ── 9. QUARTERLY COMPARISON ───────────────────────────────────────────────────
qtr = (
    df.groupby(["year","quarter"])
    .agg(admissions=("patient_id","count"),
         total_cost=("total_cost","sum"),
         avg_cost=("total_cost","mean"),
         readmit_rate=("is_readmission","mean"),
         avg_los=("length_of_stay","mean"))
    .reset_index().sort_values(["year","quarter"])
)
qtr["readmit_rate"] = (qtr["readmit_rate"]*100).round(1)
print(f"\n{'─'*65}")
print("  📆 QUARTERLY SUMMARY")
print(f"{'─'*65}")
print(f"  {'Period':<10} {'Admits':>7} {'Total Cost':>13} {'Avg Cost':>10} {'Readmit%':>9} {'Avg LOS':>8}")
print(f"  {'─'*10} {'─'*7} {'─'*13} {'─'*10} {'─'*9} {'─'*8}")
for _, r in qtr.iterrows():
    print(f"  {r['year']} {r['quarter']:<5} {r['admissions']:>7,} ${r['total_cost']:>12,.0f} ${r['avg_cost']:>9,.0f} {r['readmit_rate']:>8.1f}% {r['avg_los']:>7.1f}d")
qtr.to_csv(f"{OUT}/quarterly_summary.csv", index=False)

# ── 10. KEY INSIGHTS ──────────────────────────────────────────────────────────
highest_readmit = readmit.iloc[0]
costliest_dept  = dept.iloc[0]
most_common_dx  = diag.iloc[0]
worst_age_mort  = age_g.loc[age_g["mortality"].idxmax()]

print(f"\n{'─'*65}")
print("  💡 KEY CLINICAL & OPERATIONAL INSIGHTS")
print(f"{'─'*65}")
print(f"  1. Highest readmission dept : {highest_readmit['department']} ({highest_readmit['rate_pct']}%)")
print(f"  2. Most expensive department: {costliest_dept['department']} (${costliest_dept['total_cost']:,.0f} total)")
print(f"  3. Most common diagnosis    : {most_common_dx['diagnosis']} ({most_common_dx['cases']} cases)")
print(f"  4. Highest mortality age    : {worst_age_mort['age_group']} ({worst_age_mort['mortality']}%)")
print(f"  5. Self-pay patients        : {(df['insurance_type']=='Self-Pay').sum()} patients at financial risk")
print(f"  6. Severity 4-5 patients    : {(df['severity_score']>=4).sum():,} ({(df['severity_score']>=4).mean()*100:.1f}%) require intensive resources")
print(f"  7. Avg satisfaction (Sev 5) : {df[df['severity_score']==5]['satisfaction_score'].mean():.2f} vs overall {df['satisfaction_score'].mean():.2f}")
print(f"  8. Emergency admission rate : {(df['admission_type']=='Emergency').mean()*100:.1f}% — high unplanned burden")

print(f"\n{'='*65}")
print(f"  ✅ All reports saved → reports/")
print(f"{'='*65}\n")
