# Deploying to AWS EC2 (first-time walkthrough)

This deploys the app to a free-tier EC2 instance, running behind nginx,
kept alive by systemd. Total cost: $0 if you stay in the free tier
(t2.micro/t3.micro, 750 hrs/month free for 12 months on a new account).

## Part 1 — Create the EC2 instance (AWS Console)

1. Sign in to https://console.aws.amazon.com — create a free account if
   you don't have one (needs a card for verification, won't be charged
   if you stay in free tier limits).
2. Top-right corner: pick a region close to you (e.g. `ap-south-1` /
   Mumbai for India). **Remember this region** — everything you create
   needs to be in the same one.
3. Search "EC2" in the top search bar → open the EC2 dashboard.
4. Click **Launch Instance**.
5. **Name**: `cloud-jobs-dashboard`
6. **AMI (OS image)**: choose "Ubuntu Server 24.04 LTS" (free tier eligible)
7. **Instance type**: `t2.micro` or `t3.micro` (should say "Free tier eligible")
8. **Key pair**: click "Create new key pair" → name it, keep RSA + .pem
   format → **download it and save it somewhere safe**. This is the
   only way you'll be able to SSH in — AWS won't let you re-download it.
9. **Network settings** → click Edit → under Security group, add these
   inbound rules (this controls what traffic can reach the instance —
   a core AWS networking concept, worth understanding not just clicking):
   - SSH, port 22, source = "My IP" (so only you can SSH in)
   - HTTP, port 80, source = "Anywhere" (0.0.0.0/0) — so the dashboard is public
10. Leave storage at default (8GB is enough).
11. Click **Launch Instance**. Wait ~1 minute, then find its **Public
    IPv4 address** on the instance's detail page — you'll need this.

## Part 2 — Connect and set up the server

From your terminal (Mac/Linux, or WSL/Git Bash on Windows):

```bash
chmod 400 /path/to/your-key.pem
ssh -i /path/to/your-key.pem ubuntu@YOUR_PUBLIC_IP
```

Once connected:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx git
```

## Part 3 — Get your code onto the instance

Easiest: zip your project locally and `scp` it up.

```bash
# From your LOCAL machine, in the folder containing cloud-jobs-dashboard/
scp -i /path/to/your-key.pem -r cloud-jobs-dashboard ubuntu@YOUR_PUBLIC_IP:~/
```

(Or push it to a GitHub repo first and `git clone` it on the instance —
better practice, and gives you a public repo link to put in your resume.)

## Part 4 — Set up the Python environment on the instance

Back in your SSH session:

```bash
cd ~/cloud-jobs-dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 seed_sample_data.py   # or python3 fetch_jobs.py for real data
deactivate
```

## Part 5 — Run it as a proper service (systemd)

This keeps the app running even after you disconnect SSH, and restarts
it automatically if it crashes.

```bash
sudo cp deploy/cloud-jobs-dashboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cloud-jobs-dashboard
sudo systemctl start cloud-jobs-dashboard
sudo systemctl status cloud-jobs-dashboard   # should say "active (running)"
```

## Part 6 — Put nginx in front of it

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/cloud-jobs-dashboard
sudo ln -s /etc/nginx/sites-available/cloud-jobs-dashboard /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default   # remove the default nginx page
sudo nginx -t                               # test config for syntax errors
sudo systemctl restart nginx
```

Now visit `http://YOUR_PUBLIC_IP` in a browser — the dashboard should be live.

## Part 7 (optional but recommended) — a real domain + HTTPS

A free subdomain from something like DuckDNS, or a cheap domain, then:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

Certbot edits your nginx config and sets up auto-renewing free TLS certs
(Let's Encrypt). Now you have `https://yourdomain.com` — a real deployed
project with a real URL and no scary browser warnings, ready for your resume.

## Debugging tips (also good interview material)

- `sudo systemctl status cloud-jobs-dashboard` — is the app running?
- `sudo journalctl -u cloud-jobs-dashboard -f` — live app logs
- `sudo tail -f /var/log/nginx/error.log` — nginx-level errors
- `sudo nginx -t` — check nginx config before restarting it
- If the site loads but WebSockets don't connect (check browser dev
  tools → Network tab), it's almost always the nginx `Upgrade`/`Connection`
  headers missing — double check `deploy/nginx.conf` got copied correctly.

## What to say about this in an interview

"I provisioned an EC2 instance, configured security groups for SSH/HTTP
access, deployed a Flask app behind nginx as a reverse proxy, and ran it
as a systemd service for auto-restart. The app itself does scheduled
background data fetching and pushes live updates to clients over
WebSockets." — that's a real sentence you earned, not a buzzword salad.

## Next step: Terraform (stretch goal)

Once this manual deploy works, redoing the *exact same* EC2 instance +
security group via Terraform (Infrastructure as Code) instead of clicking
through the console is one of the highest-value things you can add — it's
the single most requested skill in the postings your own dashboard will
show you. Ask for a walkthrough once you're ready for that step.
