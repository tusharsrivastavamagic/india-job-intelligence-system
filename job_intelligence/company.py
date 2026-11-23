"""Evidence-driven company policy; never infers startup status from company size alone."""
from __future__ import annotations
from datetime import date
from .models import Job

def verify(job: Job, evidence: dict[str, dict]) -> Job:
    record=evidence.get(job.company) or evidence.get(job.company.lower())
    if not isinstance(record,dict):
        job.company_classification="Company Verification Required"; job.startup_status="Company Verification Required"
        if job.eligibility!="Excluded Jobs": job.eligibility="Company Verification Required"
        return job
    kind=str(record.get("classification","Other")); job.company_classification=kind
    year=record.get("founding_year"); people=record.get("employee_count")
    if kind.lower()!="startup": job.startup_status="Not a startup"; return job
    if not isinstance(year,int) or not isinstance(people,(int,float)) or not record.get("source"):
        job.startup_status="Company Verification Required"
        if job.eligibility!="Excluded Jobs": job.eligibility="Company Verification Required"
        return job
    job.startup_status="Eligible" if date.today().year-year >= 5 and people >= 90 else "Ineligible"
    if job.startup_status=="Ineligible": job.eligibility="Excluded Jobs"; job.exclusion_reason="Ineligible startup"
    return job
