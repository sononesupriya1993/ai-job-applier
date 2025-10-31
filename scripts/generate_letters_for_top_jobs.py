import os, json, openai
from datetime import datetime

from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


# read previous analyzer output
with open("../out/job_analysis_results.json", "r", encoding="utf-8") as f:
    analyzed_jobs = json.load(f)

# read your real CV/profile for personal info
with open("../profile.json", "r", encoding="utf-8") as f:
    profile = json.load(f)

OUT_DIR = "../out/letters"
os.makedirs(OUT_DIR, exist_ok=True)

THRESHOLD = 0.7 # only make letters for matches >= 70%

def make_cover_letter(job):
    prompt = f"""
    You are an expert recruiter assistant.

    Write a short professional cover letter (3 short paragraphs)
    for this candidate and job. Use ONLY facts from the candidate profile;
    do not invent experience, degrees, or projects. Only reference information already present in the candidate profile and try to connect it with the job description highlighting the relevant skills and experience if any.

    Candidate:
    {json.dumps(profile, indent=2)}

    Job details:
    {json.dumps(job, indent=2)}

    Tone: confident, friendly, and concise.
    Output plain text only.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def main():
    for job in analyzed_jobs:
        score = job.get("match_score", 0)
        if score < THRESHOLD:
            continue
        title = job.get("title", "Unknown Role")
        company = job.get("company", "Unknown Company")
        print(f"✉️  Generating cover letter for {title} at {company} (score {score:.2f})")
        letter = make_cover_letter(job)
        # save file
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{title.replace(' ','_')}_{company.replace(' ','_')}.txt"
        path = os.path.join(OUT_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(letter)
        print(f"✅ saved: {path}")
    print("\n🎉 Done. All cover letters are in the 'out/letters' folder.")

if __name__ == "__main__":
    main()
