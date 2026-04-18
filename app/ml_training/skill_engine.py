def extract_skills(text):
    skills_list = [
        "python", "java", "c++", "sql", "machine learning",
        "deep learning", "excel", "power bi", "tableau",
        "data analysis", "communication", "cloud", "aws"
    ]

    found = []

    text = str(text).lower()

    for skill in skills_list:
        if skill in text:
            found.append(skill)

    return found