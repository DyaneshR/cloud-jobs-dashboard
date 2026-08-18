# Cloud/DevOps Job Requirements Dashboard

A small pipeline that pulls live Cloud Engineer / Cloud Support Engineer /
DevOps Engineer job postings from free public APIs, extracts which skills
and experience levels are most commonly requested, and shows it in a
filterable dashboard.

## Setup (run on your own machine — not this sandbox)

```bash
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt

# Optional: seed with sample data first, just to see the dashboard working
python3 seed_sample_data.py

# Pull real postings (needs internet access — this is the real ingestion step)
python3 fetch_jobs.py

# Start the dashboard
python3 app.py
```

Then open http://127.0.0.1:5000

Re-run `fetch_jobs.py` anytime to pull fresh postings — it won't duplicate
entries (see the `UNIQUE` constraint in `db.py`).

## How it's structured, and why (the part worth being able to explain)

This is a 4-stage pipeline. Each stage does ONE job and doesn't know about
the others' internals — this is the same separation-of-concerns idea
behind any real ETL/data pipeline or microservice architecture.

**1. Ingestion — `fetch_jobs.py`**
Hits Arbeitnow and RemoteOK's public APIs (not scraping — these sites
publish this data via API on purpose, so it's reliable and won't get you
IP-blocked the way scraping LinkedIn/Indeed would). Filters by job title,
saves raw postings.

**2. Storage — `db.py`**
SQLite — a single file, zero setup. Chosen deliberately for this scale
(a few thousand rows, single user); if this were a multi-user production
service you'd reach for Postgres/MySQL instead. Being able to justify
"why this database, at this scale" is a real interview-relevant skill.

**3. Extraction — `extract_skills.py`**
Turns free-text descriptions into structured counts using regex keyword
matching. This is a conscious trade-off: fast and 100% explainable
("why did it flag this posting?" → "because it matched `\bterraform\b`"),
at the cost of missing skills phrased in ways not in the keyword list.
A more advanced version could swap this for an NLP model (spaCy NER) or
an LLM call per posting — worth mentioning as a possible improvement.

**4. Serving — `app.py` + `templates/index.html`**
Flask exposes the processed data as a small JSON REST API
(`/api/skills`, `/api/jobs`, `/api/companies`). The frontend is a static
page that calls those endpoints with `fetch()` and renders results with
Chart.js. This client/server split means the frontend could be swapped
out (React, a CLI, a Slack bot) without touching the backend at all.

## Realtime features

- **Scheduled auto-refresh**: `app.py` runs a background job (APScheduler)
  every 6 hours that re-fetches postings automatically — no manual
  re-run needed once deployed.
- **Live push via WebSockets**: after each scheduled fetch, the server
  pushes a `jobs_updated` event to every open browser tab (Flask-SocketIO),
  which triggers the dashboard to silently refresh its charts — no page
  reload. The green/red dot next to the title shows live connection status.

## Deploying it live

See `DEPLOY.md` for a full first-time walkthrough of deploying this to
an AWS EC2 free-tier instance, behind nginx, kept alive with systemd.

## Extending it

- Add more sources in `fetch_jobs.py` (Adzuna has a free tier but needs
  a free API key — good next step once this baseline works)
- Add more keywords to `SKILL_KEYWORDS` in `extract_skills.py` as you
  notice gaps
- Add a cron job / scheduled task to run `fetch_jobs.py` daily and watch
  trends change over time
- Deploy it (Render, Railway, or a small EC2/VM instance — deploying
  this yourself is good DevOps practice in its own right)
