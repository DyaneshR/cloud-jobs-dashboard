"""
Stage 3: PROCESSING / EXTRACTION
-----------------------------------
Turns unstructured job description text into structured data: which
skills are mentioned, and how often, across all postings (or a filtered
subset).

Approach: keyword/phrase matching with word boundaries (regex), not a
full NLP model. This is a deliberate, explainable trade-off:
  - Pro: fast, zero dependencies, 100% explainable ("why did it count
    this?" -> "because the string 'terraform' appeared").
  - Con: misses synonyms/phrasing it doesn't know about, so the keyword
    list needs occasional updates.
A fancier version could use spaCy NER or an LLM call per description —
worth mentioning if asked "how would you improve this" in an interview.
"""
import re
from collections import Counter

# Keyword -> canonical display name. Grouped so it's easy to extend.
SKILL_KEYWORDS = {
    # Cloud platforms
    "aws": "AWS", "amazon web services": "AWS",
    "azure": "Azure",
    "gcp": "GCP", "google cloud": "GCP",
    # IaC / automation
    "terraform": "Terraform",
    "ansible": "Ansible",
    "cloudformation": "CloudFormation",
    "pulumi": "Pulumi",
    # Containers / orchestration
    "docker": "Docker",
    "kubernetes": "Kubernetes", "k8s": "Kubernetes",
    "helm": "Helm",
    # CI/CD
    "jenkins": "Jenkins",
    "github actions": "GitHub Actions",
    "gitlab ci": "GitLab CI",
    "ci/cd": "CI/CD",
    "circleci": "CircleCI",
    # Monitoring/observability
    "grafana": "Grafana",
    "prometheus": "Prometheus",
    "datadog": "Datadog",
    "elk": "ELK Stack", "elasticsearch": "ELK Stack",
    "cloudwatch": "CloudWatch",
    "splunk": "Splunk",
    # Scripting/languages
    "python": "Python",
    "bash": "Bash/Shell", "shell script": "Bash/Shell",
    "go\\b": "Go",
    # Networking/linux
    "linux": "Linux",
    "networking": "Networking",
    "dns": "DNS",
    "vpc": "VPC/Networking",
    # Config mgmt / other infra
    "chef\\b": "Chef",
    "puppet": "Puppet",
    # Databases
    "mysql": "MySQL",
    "postgres": "PostgreSQL", "postgresql": "PostgreSQL",
    "mongodb": "MongoDB",
    # Practices
    "agile": "Agile",
    "sre\\b": "SRE practices",
    "incident management": "Incident Management",
    "on-call": "On-call",
    # Certifications
    "aws certified": "AWS Certification",
    "azure certified": "Azure Certification",
    "ckad": "CKA/CKAD",
    "cka\\b": "CKA/CKAD",
}

EXPERIENCE_PATTERN = re.compile(r"(\d+)\+?\s*(?:-\s*\d+\s*)?years?", re.IGNORECASE)


def extract_skills_from_text(text):
    """Returns a set of canonical skill names found in one description."""
    text_lower = text.lower()
    found = set()
    for pattern, canonical in SKILL_KEYWORDS.items():
        if re.search(r"\b" + pattern + r"\b", text_lower):
            found.add(canonical)
    return found


def extract_experience_years(text):
    """Pulls out mentions like '3+ years' -> returns list of ints found."""
    matches = EXPERIENCE_PATTERN.findall(text)
    return [int(m) for m in matches if m.isdigit()]


def analyze_jobs(jobs):
    """
    Given a list of job dicts (with 'description'), returns:
      - skill_counts: Counter of skill -> number of postings mentioning it
      - total_jobs: how many postings were analyzed
      - experience_years: Counter of commonly requested year thresholds
    """
    skill_counts = Counter()
    experience_counts = Counter()

    for job in jobs:
        desc = job.get("description") or ""
        title = job.get("title") or ""
        combined = f"{title} {desc}"

        skills_found = extract_skills_from_text(combined)
        skill_counts.update(skills_found)

        years = extract_experience_years(combined)
        experience_counts.update(years)

    return {
        "total_jobs": len(jobs),
        "skill_counts": skill_counts.most_common(),
        "experience_years": experience_counts.most_common(10),
    }
