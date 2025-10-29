import os, re, time, requests
from bs4 import BeautifulSoup

JOBS_DIR = "../jobs"
OUT_DIR = "../jobs/fetched"
ALLOW_DOMAINS = ["greenhouse.io", "lever.co"]

os.makedirs(OUT_DIR, exist_ok=True)

def domain_ok(url):
    low = url.lower()
    return any(d in low for d in ALLOW_DOMAINS)

def extract_text(url):
    r = requests.get(url, timeout=15, headers={"User-Agent":"Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    # crude: pull main text content
    for tag in soup(["script","style","nav","footer","header"]):
        tag.decompose()
    text = " ".join(soup.get_text("\n").split())
    return text[:50000]  # cap length

def main():
    for name in os.listdir(JOBS_DIR):
        if not name.endswith(".txt"):
            continue
        path = os.path.join(JOBS_DIR, name)
        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        links = [ln for ln in lines if ln.startswith("http")]
        links = [u for u in links if domain_ok(u)]
        if not links:
            continue
        out_name = name.replace(".txt", ".jd.txt")
        out_path = os.path.join(OUT_DIR, out_name)
        if os.path.exists(out_path):
            continue
        all_texts = []
        for u in links[:3]:  # try first few
            try:
                txt = extract_text(u)
                all_texts.append(f"URL: {u}\n\n{txt}\n\n" + "-"*60 + "\n")
                time.sleep(1)
            except Exception as e:
                print("skip", u, e)
        if all_texts:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write("\n".join(all_texts))
            print("🧾 saved JD text:", out_path)

if __name__ == "__main__":
    main()
