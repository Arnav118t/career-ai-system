import pandas as pd
from skill_engine import extract_skills

# Load data
students = pd.read_csv("indian_engineering_student_placement.csv")
jobs = pd.read_csv("linkdin_Job_data.csv")

# Clean
students = students.fillna(0)
jobs = jobs.fillna("")

# Normalize column names
students.columns = students.columns.str.lower()
jobs.columns = jobs.columns.str.lower()

# 🔥 ADD HERE (after cleaning + normalization)
students["skills"] = [["python", "sql"]] * len(students)
jobs["skills"] = jobs["job_details"].apply(extract_skills)
print(jobs[["job", "skills"]].head())

# Debug prints
print("Students:", students.shape)
print("Jobs:", jobs.shape)
print(jobs.columns)
print(jobs[["job_details", "skills"]].head())