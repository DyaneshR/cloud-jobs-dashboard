"""
Stage 1: INGESTION
-------------------
Pulls job postings from free, public job-board APIs (no scraping — these
sites explicitly offer their data via API, so this is legit and won't get
you blocked).

Sources used:
  - Arbeitnow (https://arbeitnow.com/api/job-board-api) — free, no auth
  - RemoteOK  (https://remoteok.com/api)                — free, no auth

Concept: this is the "E" (Extract) in ETL. We keep this stage dumb on
purpose — it just fetches and saves raw data. All the smart parsing
happens later in extract_skills.py. Separating these stages means if a
source's API changes, you only fix one file.
"""
import requests
import time
from db import init_db, insert_job

SEARCH_TERMS = ["cloud engineer", "cloud support engineer", "devops engineer"]

# ---- Source 1: Arbeitnow -----------------------------------------------
def fetch_arbeitnow():
    jobs = []
    url = "https://arbeitnow.com/api/job-board-api"
    page = 1
    while url:
        resp = requests.get(url, params={"page": page} if page > 1 else {}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("data", []):
            title = item.get("title", "")
            if any(term.lower() in title.lower() for term in SEARCH_TERMS):
                jobs.append({
                    "source": "arbeitnow",
                    "title": title,
                    "company": item.get("company_name", "Unknown"),
                    "description": item.get("description", ""),
                    "url": item.get("url", ""),
                    "location": item.get("location", ""),
                })
        # Arbeitnow paginates via links.next
        next_url = (data.get("links") or {}).get("next")
        if next_url and page < 5:  # cap pages so this doesn't run forever
            url = next_url
            page += 1
            time.sleep(0.5)  # be polite to the API
        else:
            url = None
    return jobs


# ---- Source 2: RemoteOK --------------------------------------------------
def fetch_remoteok():
    jobs = []
    resp = requests.get(
        "https://remoteok.com/api",
        headers={"User-Agent": "Mozilla/5.0 (job-research-tool)"},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    # First element is metadata, skip it
    for item in data[1:]:
        title = item.get("position", "") or ""
        if any(term.lower() in title.lower() for term in SEARCH_TERMS):
            jobs.append({
                "source": "remoteok",
                "title": title,
                "company": item.get("company", "Unknown"),
                "description": item.get("description", ""),
                "url": item.get("url", ""),
                "location": item.get("location", "Remote"),
            })
    return jobs


def run():
    init_db()
    all_jobs = []
    print("Fetching from Arbeitnow...")
    try:
        all_jobs += fetch_arbeitnow()
    except Exception as e:
        print(f"  Arbeitnow failed: {e}")

    print("Fetching from RemoteOK...")
    try:
        all_jobs += fetch_remoteok()
    except Exception as e:
        print(f"  RemoteOK failed: {e}")

    print(f"Fetched {len(all_jobs)} matching jobs total. Saving to DB...")
    for job in all_jobs:
        insert_job(job)
    print("Done.")


if __name__ == "__main__":
    run()
