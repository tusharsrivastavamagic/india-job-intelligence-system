from __future__ import annotations
import re
from .models import Job
from .parsing import parse_experience, parse_compensation

FUNCTIONS = "marketing sales business development finance financial banking fintech human resources hr analytics data analytics business intelligence media advertising public relations communications logistics supply chain procurement operations management strategy consulting project customer success market research growth partnerships".split()
INDIA = re.compile(r"\b(india|bengaluru|bangalore|mumbai|pune|delhi|gurgaon|gurugram|noida|hyderabad|chennai|kolkata|ahmedabad|kochi|remote)\b", re.I)
def classify(job: Job, min_ctc=8, min_stipend=10000, max_exp=3) -> Job:
    parse_experience(job); parse_compensation(job)
    blob = (job.title + " " + job.description).lower(); intern = "intern" in blob
    if not INDIA.search(job.location + " " + blob): job.eligibility, job.exclusion_reason = "Excluded Jobs", "Location restriction"; return job
    if job.experience_status == "Ineligible": job.eligibility, job.exclusion_reason = "Excluded Jobs", "Experience above 3 years"; return job
    if job.salary_status == "Ineligible": job.eligibility, job.exclusion_reason = "Excluded Jobs", "Unpaid internship" if "unpaid" in blob else ("Internship stipend below ₹10,000/month" if intern else "Full-time salary below ₹8 LPA"); return job
    relevant = sum(word in blob for word in FUNCTIONS)
    if not relevant: job.eligibility, job.exclusion_reason = "Excluded Jobs", "Irrelevant position"; return job
    score = min(40, relevant * 8) + (20 if job.experience_status == "Eligible" else 5) + (20 if job.salary_status == "Eligible" else 5) + (10 if job.direct_apply_url else 0) + (10 if job.posted_date else 0)
    job.match_score = score; job.match_explanation = f"function keywords={relevant}; experience={job.experience_status}; pay={job.salary_status}; direct apply={'yes' if job.direct_apply_url else 'no'}"
    if job.experience_status != "Eligible": job.eligibility = "Experience Verification Required"
    elif job.salary_status == "Salary Undisclosed": job.eligibility = "Salary Undisclosed"
    elif job.salary_status == "Salary Verification Required": job.eligibility = "Salary Verification Required"
    elif intern: job.eligibility = "Paid Internships"
    else: job.eligibility = "Strong Matches" if score >= 55 else "Possible Matches"
    return job
