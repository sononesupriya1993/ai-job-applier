import json
import os
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ---- Google Sheets Setup ----
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")


scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name("../sheets_key.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

# ---- Load job data ----
with open("../out/job_analysis_results.json", "r", encoding="utf-8") as f:
    jobs = json.load(f)

# ---- Always clear old data and rewrite cleanly ----
sheet.clear()
headers = ["Date", "Title", "Company", "Match Score", "Letter Made", "Job Link"]
sheet.append_row(headers)

# ---- Prepare data rows ----
today = datetime.date.today().strftime("%Y-%m-%d")
rows = []

for job in jobs:
    title = job.get("title", "Unknown Title")
    company = job.get("company", "Unknown Company")
    score = round(job.get("match_score", 0), 2)
    link = job.get("link", "")
    letter = "✅" if score >= 0.7 else "❌"
    rows.append([today, title, company, score, letter, link])

# ---- Write all rows below header ----
if rows:
    sheet.append_rows(rows, value_input_option="USER_ENTERED")

print("📊 Tracker updated successfully — check your Google Sheet!")
