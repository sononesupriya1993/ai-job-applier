import os
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from playwright.sync_api import sync_playwright

# --- Google Sheet Setup ---
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

# --- Read data from sheet ---
rows = sheet.get_all_records()
cv_path = "../out/CV_Main.pdf"
cover_letter_dir = "../out/letters"

def apply_to_job(url, cover_letter_path, first_name, last_name, email, phone):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=r"C:\Users\SupriyAnkit\AppData\Local\Google\Chrome\User Data\Default",
            channel="chrome",
            headless=False
        )
        page = browser.new_page()
        print(f"🌐 Opening: {url}")
        page.goto(url, timeout=60000)

        print("🕒 Browser opened. Log in manually if needed; the window will stay open.")
        input("👉 Press ENTER here in the terminal after you finish logging in...")

        # (rest of your code below stays the same)
        print("✅ Done. You can now interact manually or close the browser.")



        # --- Example generic form fields (adjust per site) ---
        try:
            if page.query_selector("input[name='firstName']"):
                page.fill("input[name='firstName']", first_name)
            if page.query_selector("input[name='lastName']"):
                page.fill("input[name='lastName']", last_name)
            if page.query_selector("input[type='email']"):
                page.fill("input[type='email']", email)
            if page.query_selector("input[type='tel']"):
                page.fill("input[type='tel']", phone)

            # upload files if possible
            if page.query_selector("input[type='file']"):
                page.set_input_files("input[type='file']", [cv_path, cover_letter_path])

            # click apply/submit button
            if page.query_selector("button[type='submit']"):
                page.click("button[type='submit']")
                print("✅ Submitted!")
            else:
                print("⚠️ Submit button not found. Manual review may be needed.")
            
            time.sleep(5)
        except Exception as e:
            print("❌ Error during application:", e)

        browser.close()

# --- Main loop ---
for i, job in enumerate(rows, start=2):
    url = job.get("Job Link", "")
    print(f"\n🔍 Checking job #{i-1}: {job.get('Title', 'Unknown')} ({job.get('Company', 'Unknown')})")
    print(f"➡️  Link: {url}")
    print(f"📊 Match score marker: {job.get('Letter Made')}")

    if not url or url.strip() == "":
        print("⚠️  Skipping — no job link found.")
        continue

    if job.get("Letter Made") != "✅":
        print("🚫 Skipping — not a top match (Letter Made not ✅).")
        continue  # skip low matches

    company = job.get("Company", "Unknown")
    title = job.get("Title", "Unknown")
    cover_letter_path = os.path.join(cover_letter_dir, f"cover_letter_{company}.txt")

    print(f"\n🧾 Applying for {title} at {company}...")

    apply_to_job(
        url=url,
        cover_letter_path=cover_letter_path,
        first_name="Supriya",
        last_name="Sonone",
        email="ssupriya5156@gmail.com",
        phone="+47XXXXXXXX"
    )

    sheet.update_cell(i, 7, "✅ Applied")
    print(f"✅ Updated sheet for {company}")


    company = job.get("Company", "Unknown")
    title = job.get("Title", "Unknown")
    cover_letter_path = os.path.join(cover_letter_dir, f"cover_letter_{company}.txt")

    print(f"\n🧾 Applying for {title} at {company}...")

    apply_to_job(
        url=url,
        cover_letter_path=cover_letter_path,
        first_name="Sxxxxx",
        last_name="Sxxxxx",
        email="sxxxxxxxxx@gmail.com",
        phone="+47XXXXXXXX"
    )

    # mark as applied in Google Sheet
    sheet.update_cell(i, 7, "✅ Applied")
    print(f"✅ Updated sheet for {company}")
