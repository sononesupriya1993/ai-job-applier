import openai
import json
from datetime import datetime

# Load your profile (for contact info only)
with open("../profile.json", "r", encoding="utf-8") as f:
    profile = json.load(f)

# 🔧 Replace with your OpenAI API key
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


# ---- Job description to tailor for ----
job_description = """
As an ML Engineer, you will play a key role in the exploration, development and production of machine learning solutions that create value for our customers and internal processes. You will work closely with data scientists, data engineers and software developers to ensure that our models are robust, scalable and provide real business value.

We offer a working day with exciting and varied tasks in a team with high professional expertise and great commitment, as well as good opportunities for professional development and influence on technology and infrastructure. You will be part of the unit led by VP Data & AI, who has overall responsibility for data, machine learning and artificial intelligence in the company. The department is part of the staff function in the company, and works closely with consulting engineers to solve challenges related to customer needs and the everyday life of the projects.

 

Who are we looking for?

We are looking for an enterprising person who enjoys taking responsibility and has practical experience as an ML Engineer or Data Scientist. We are looking for an employee with:

Minimum 2 years of experience with Python and SQL.
Higher education in computer science, statistics, applied mathematics, computer science or related fields.
Curiosity and willingness to learn to keep up with a constantly changing field.
Experience with engineering data: Signal processing, IoT, 3D models, hierarchical data structures or similar.
Practical experience with language models and use of APIs for function calling, RAG and context engineering.
 

If you have mainly worked with CRM, ERP or sales data, you must be able to demonstrate 

private projects that support interest in engineering data.

 
"""

# ---- Prompt ----
prompt = f"""
You are an expert recruiter assistant.

Write a short, professional cover letter for the job below,
using the candidate's real CV as-is (do NOT invent new skills, education, or projects).
Only reference information already present in the candidate profile and try to connect it with the job description highlighting the relevant skills and experience if any.
Keep it 3 short paragraphs, friendly but formal. Do not use fancy words.

Candidate:
{json.dumps(profile, indent=2)}

Job:
{job_description}
"""

response = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}]
)

cover_letter = response.choices[0].message.content.strip()

# Save to file
filename = f"../out/cover_letter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
with open(filename, "w", encoding="utf-8") as f:
    f.write(cover_letter)

print("✅ Cover letter created:", filename)
print("📎 Remember to attach CV_Main.pdf with this letter when applying.")
