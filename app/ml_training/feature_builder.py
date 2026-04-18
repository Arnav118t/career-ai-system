import pandas as pd

def build_student_features(df):

    df["gpa"] = df["cgpa"]

    df["college_tier"] = 2  # assume for now

    df["study_time"] = df["cgpa"] * 2

    df["switch_months"] = 12

    df["risk_score"] = df["backlogs"] * 2

    df["ambition_score"] = df["cgpa"] / 10

    df["stability_score"] = 10 - df["backlogs"]

    df["learning_score"] = df["cgpa"] * 1.5

    df["salary_priority"] = 7

    df["wlb_preference"] = 5

    return df
def build_job_features(jobs):

    jobs["ctc"] = 10  # temporary default

    jobs["company_type"] = 1

    jobs["location_tier"] = 1

    jobs["workload_score"] = 6

    jobs["skill_match"] = 5

    jobs["savings_rate"] = 3

    jobs["switch_probability"] = 0.5

    jobs["predicted_2yr_salary"] = jobs["ctc"] * 1.5

    return jobs