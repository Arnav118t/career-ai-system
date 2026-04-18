import pandas as pd
import random

students = pd.read_csv("indian_engineering_student_placement.csv")
jobs = pd.read_csv("linkdin_Job_data.csv")

data = []

for i in range(1000):  # generate samples

    student = students.sample(1).iloc[0]
    job = jobs.sample(1).iloc[0]

    sample = {}

    # student features
    sample["gpa"] = student["cgpa"]

    # job features
    sample["ctc"] = 10
    sample["skill_match"] = len(job["skills"])

    # target (dummy for now)
    sample["satisfaction_score"] = (
    sample["gpa"] * 3 +
    sample["skill_match"] * 6 +
    random.uniform(-5, 5)
)
    
    data.append(sample)

df = pd.DataFrame(data)

df.to_csv("ml_training/training_data.csv", index=False)

print(df.head())