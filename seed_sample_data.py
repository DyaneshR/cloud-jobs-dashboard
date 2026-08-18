"""
Seeds the DB with a few sample postings so you can verify the dashboard
works before running the real fetch (useful since the real APIs need
outbound internet access to job-board domains, which this sandbox
doesn't have — but your own machine will).
"""
from db import init_db, insert_job

SAMPLE_JOBS = [
    {
        "source": "sample", "title": "Cloud Engineer", "company": "Acme Corp",
        "description": "Looking for a Cloud Engineer with 3+ years experience in AWS, "
                        "Terraform, and Docker. Experience with Kubernetes and CI/CD "
                        "pipelines (Jenkins or GitHub Actions) required. Linux and Python "
                        "scripting a plus. AWS Certified Solutions Architect preferred.",
        "url": "#", "location": "Remote",
    },
    {
        "source": "sample", "title": "DevOps Engineer", "company": "TechNova",
        "description": "5+ years in DevOps. Must know Terraform, Ansible, Kubernetes, "
                        "and Docker. Strong Linux fundamentals. Experience with Grafana "
                        "and Prometheus for monitoring. Python and Bash scripting required. "
                        "On-call rotation experience needed.",
        "url": "#", "location": "Bangalore",
    },
    {
        "source": "sample", "title": "Cloud Support Engineer", "company": "Acme Corp",
        "description": "2+ years supporting AWS or Azure environments. Troubleshooting "
                        "networking and VPC issues. Familiarity with CloudWatch, Linux, "
                        "and basic Python scripting. ITIL/incident management experience "
                        "a plus.",
        "url": "#", "location": "Hybrid",
    },
    {
        "source": "sample", "title": "DevOps Engineer", "company": "CloudWorks",
        "description": "4+ years experience. GCP or AWS. Kubernetes and Helm required. "
                        "CI/CD with GitLab CI. Datadog for observability. Go or Python "
                        "for tooling. Agile team environment.",
        "url": "#", "location": "Remote",
    },
]

if __name__ == "__main__":
    init_db()
    for job in SAMPLE_JOBS:
        insert_job(job)
    print(f"Seeded {len(SAMPLE_JOBS)} sample jobs.")
