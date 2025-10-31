import openai
import json

# Load your profile
with open("../profile.json", "r", encoding="utf-8") as f:
    profile = json.load(f)

# Paste your latest job match JSON here (the one GPT gave you)
job_data = {
    "title": "ML Engineer",
    "company": "",
    "location": "Norway",
    "required_skills": [
        "Python (2+ years)",
        "SQL (2+ years)",
        "Experience with engineering data",
        "Practical experience with language models"
    ],
    "preferred_skills": [
        "Deploying production-grade ML",
        "Collaboration with data scientists",
        "Curiosity and willingness to learn"
    ],
    "key_responsibilities": [
        "Explore, develop, and productionize ML solutions",
        "Ensure models are robust, scalable, and valuable",
        "Collaborate with data and software teams"
    ],
    "match_score": 0.5,
    "comment": "Strong fit on Python and SQL; missing IoT and LLM-specific experience."
}

# -------------- CONFIG ----------------
# Replace this with your OpenAI API key (get from https://platform.openai.com)
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# -------------------------------------

# 🧠 Generate tailored CV
cv_prompt = f"""
You are an expert resume writer.

Based on this candidate profile:
{json.dumps(profile, indent=2)}

And this job:
{json.dumps(job_data, indent=2)}

Write a short, one-page text CV (plain text, no formatting) that highlights the candidate's strengths relevant to the job, 
and uses the same keywords from the job description.
Keep it under 300 words.
"""

cv_response = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": cv_prompt}]
)

cv_text = cv_response.choices[0].message.content.strip()

# ✉️ Generate cover letter
cl_prompt = f"""
Write a short cover letter for this job.
Mention the company name if given, otherwise just 'your organization'.
Keep it 3 paragraphs, professional but friendly.
Focus on how the candidate fits the role and is eager to contribute.
Use information from:
Profile:
{json.dumps(profile, indent=2)}
Job:
{json.dumps(job_data, indent=2)}
"""

cl_response = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": cl_prompt}]
)

cl_text = cl_response.choices[0].message.content.strip()

# Save outputs
with open("../out/cv_output.txt", "w", encoding="utf-8") as f:
    f.write(cv_text)

with open("../out/cover_letter.txt", "w", encoding="utf-8") as f:
    f.write(cl_text)

print("✅ Done! Check the 'out' folder for cv_output.txt and cover_letter.txt.")
