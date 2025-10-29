import os, re, json, base64, datetime
from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ---- settings you can tweak ----
SAVE_DIR = "../jobs"                    # where we save found jobs
LABEL_QUERY = 'newer_than:10d'  # search emails from last 7 days
SENDERS = [
    "linkedin.com",
    "e.linkedin.com",
    "job-alerts@linkedin.com",
    "jobs-noreply@linkedin.com",
    "no-reply@linkedin.com",
    "alerts-noreply@google.com"        # Google Jobs alerts
]
ROLE_KEYWORDS = [
    "data analyst", "data scientist", "ml engineer", "machine learning",
    "junior data scientist", "junior data analyst", "Tableau"
]
# --------------------------------

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_service():
    # token.json stores the user's access/refresh tokens
    creds = None
    if os.path.exists("../token.json"):
        creds = Credentials.from_authorized_user_file("../token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("../client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("../token.json", "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

def clean_filename(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9._-]+", "_", s.strip())
    return s[:120]

def extract_urls_from_html(html: str):
    soup = BeautifulSoup(html, "lxml")
    urls = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("http"):
            urls.add(href)
    return list(urls)

def looks_like_job(title_or_text: str) -> bool:
    low = title_or_text.lower()
    return any(k in low for k in ROLE_KEYWORDS)

def main():
    service = get_service()
    query = LABEL_QUERY
    # apply sender filters to reduce noise
    sender_part = " OR ".join([f'from:{s}' for s in SENDERS])
    if sender_part:
        query = f"({query}) ({sender_part})"

    results = service.users().messages().list(userId="me", q=query, maxResults=25).execute()
    messages = results.get("messages", [])
    if not messages:
        print("No recent job emails found.")
        return

    os.makedirs(SAVE_DIR, exist_ok=True)
    saved_count = 0

    for m in messages:
        msg = service.users().messages().get(userId="me", id=m["id"], format="full").execute()
        headers = msg["payload"].get("headers", [])
        subject = next((h["value"] for h in headers if h["name"].lower()=="subject"), "(no subject)")
        frm = next((h["value"] for h in headers if h["name"].lower()=="from"), "")
        date = next((h["value"] for h in headers if h["name"].lower()=="date"), "")
        # find HTML part
        parts = msg["payload"].get("parts", [])
        html_body = ""
        def walk(parts):
            nonlocal html_body
            for p in parts:
                if p.get("mimeType") == "text/html":
                    data = p["body"].get("data")
                    if data:
                        html_body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                elif p.get("parts"):
                    walk(p["parts"])
        if parts:
            walk(parts)
        else:
            # sometimes body is right at payload.body
            data = msg["payload"]["body"].get("data")
            if data:
                html_body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

        if not html_body:
            continue

        urls = extract_urls_from_html(html_body)

        # keep only URLs that look like jobs or from known job domains
        JOB_DOMAINS = ["linkedin.com", "greenhouse.io", "lever.co", "workday", "smartrecruiters", "jobs", "careers"]
        job_urls = [u for u in urls if any(d in u.lower() for d in JOB_DOMAINS)]

        # save a small job "inbox" file for each email
        if job_urls and (looks_like_job(subject) or looks_like_job(html_body)):
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            base = clean_filename(subject) or "job_alert"
            path = os.path.join(SAVE_DIR, f"{ts}__{base}.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"Subject: {subject}\nFrom: {frm}\nDate: {date}\n\nLinks:\n")
                for u in job_urls:
                    f.write(u + "\n")
            print("📝 saved job links to:", path)
            saved_count += 1

    print(f"✅ Done. Saved {saved_count} job link files into {SAVE_DIR}")

if __name__ == "__main__":
    main()
