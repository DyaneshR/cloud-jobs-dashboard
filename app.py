"""
Stage 4: SERVING (now with realtime)
---------------------------------------
Two forms of "realtime" added on top of the original REST API:

1. SCHEDULED REFRESH - APScheduler runs fetch_jobs.run() automatically
   every N hours in the background, inside the same process. This is
   the same pattern as a cron job, just embedded in the app instead of
   the OS scheduler (fine at this scale; a production system would more
   likely use a separate worker + real cron/systemd timer so a crashed
   web process doesn't kill your scheduled jobs).

2. WEBSOCKETS (Flask-SocketIO) - after each scheduled fetch completes,
   the server pushes a "jobs_updated" event to every connected browser.
   The frontend listens for it and re-renders without the user hitting
   refresh. This is the client-server push model behind things like
   live dashboards, chat apps, and monitoring tools.
"""
import logging
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO
from apscheduler.schedulers.background import BackgroundScheduler

from db import init_db, get_all_jobs, get_distinct_companies
from extract_skills import analyze_jobs
import fetch_jobs

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

REFRESH_INTERVAL_HOURS = 6


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/companies")
def api_companies():
    return jsonify(get_distinct_companies())


@app.route("/api/skills")
def api_skills():
    role = request.args.get("role", "").strip()
    company = request.args.get("company", "").strip()
    jobs = get_all_jobs(role_filter=role or None, company_filter=company or None)
    return jsonify(analyze_jobs(jobs))


@app.route("/api/jobs")
def api_jobs():
    role = request.args.get("role", "").strip()
    company = request.args.get("company", "").strip()
    jobs = get_all_jobs(role_filter=role or None, company_filter=company or None)
    for j in jobs:
        j["description"] = (j["description"] or "")[:300]
    return jsonify(jobs)


@socketio.on("connect")
def handle_connect():
    log.info("Client connected")


@app.route("/api/trigger-refresh")
def api_trigger_refresh():
    """
    Manual trigger for testing: runs the same fetch+notify function the
    scheduler calls automatically every 6 hours, but runs it inside THIS
    already-running server process (not a separate one-off script) so it
    actually has access to the real connected WebSocket clients.
    """
    scheduled_fetch_job()
    return jsonify({"status": "triggered"})


def scheduled_fetch_job():
    """Runs in the background on a timer. Fetches new postings, then
    tells every connected browser to refresh via WebSocket."""
    log.info("Running scheduled job fetch...")
    try:
        fetch_jobs.run()
        socketio.emit("jobs_updated", {"message": "New job data available"})
        log.info("Scheduled fetch complete, clients notified.")
    except Exception as e:
        log.error(f"Scheduled fetch failed: {e}")


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        scheduled_fetch_job,
        "interval",
        hours=REFRESH_INTERVAL_HOURS,
    )
    scheduler.start()
    log.info(f"Scheduler started - refetching every {REFRESH_INTERVAL_HOURS}h")


init_db()
start_scheduler()

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000)
