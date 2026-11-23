from __future__ import annotations
import hashlib, re
from .models import Job
def key(job: Job) -> str:
    raw = job.direct_apply_url or job.job_url or f"{job.company}|{job.title}|{job.location}"
    return hashlib.sha256(raw.lower().strip().encode()).hexdigest()[:16]
def deduplicate(jobs: list[Job]) -> list[Job]:
    out={}
    for job in jobs:
        job.internal_id=key(job); job.duplicate_group_id=job.internal_id
        existing=out.get(job.internal_id)
        if not existing:
            # Conservative fallback: same employer/title/location plus 90% token overlap.
            for candidate in out.values():
                if candidate.company.lower()!=job.company.lower() or candidate.title.lower()!=job.title.lower() or candidate.location.lower()!=job.location.lower(): continue
                a=set(re.findall(r"[a-z0-9]{3,}",candidate.description.lower())); b=set(re.findall(r"[a-z0-9]{3,}",job.description.lower()))
                if a and b and len(a & b)/len(a | b) >= .90:
                    existing=candidate; job.duplicate_group_id=candidate.duplicate_group_id; break
        if existing:
            if job.source not in existing.source.split(";"): existing.source += ";" + job.source
            continue
        out[job.internal_id]=job
    return list(out.values())
