import os, json, openai

# load your profile (so the model knows your real info)
with open("../profile.json", "r", encoding="utf-8") as f:
    profile = json.load(f)

openai.api_key = "sk-your-key-here"

JOBS_DIR = "../jobs/fetched"
OUT_FILE = "../out/job_analysis_results.json"

def analyze_job(job_text):
    prompt = f"""
    SYSTEM: You are a structured job analyzer.
    USER: Here is a job description:
    \"\"\"{job_text}\"\"\"

    Candidate profile:
    {json.dumps(profile, indent=2)}

    TASKS:
    1. Extract and return in JSON:
       - title
       - company
       - required_skills (list)
       - preferred_skills (list)
       - key_responsibilities (list)
    2. Compare candidate skills with required_skills.
    3. Compute a "match_score" between 0.0 and 1.0.
    4. Return a short explanation (2 sentences) of strengths and gaps.

    Output ONLY JSON like:
    {{
      "title": "",
      "company": "",
      "required_skills": [],
      "preferred_skills": [],
      "key_responsibilities": [],
      "match_score": 0.0,
      "comment": ""
    }}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.choices[0].message.content.strip()
    try:
        return json.loads(text)
    except:
        print("⚠️ could not parse model response, raw text below:")
        print(text)
        return None

def main():
    results = []
    for name in os.listdir(JOBS_DIR):
        if not name.endswith(".jd.txt"):
            continue
        path = os.path.join(JOBS_DIR, name)
        print(f"🔍 analyzing {name} ...")
        with open(path, "r", encoding="utf-8") as f:
            job_text = f.read()
        analysis = analyze_job(job_text)
        if analysis:
            analysis["source_file"] = name
            results.append(analysis)
            print(f"✅ {name} → match_score: {analysis['match_score']:.2f}")
    # save all results
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n📊 analysis completed. Results saved to {OUT_FILE}")

if __name__ == "__main__":
    main()
