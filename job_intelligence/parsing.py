from __future__ import annotations
import re
from .models import Job

def text(job: Job) -> str: return " ".join([job.title, job.description, job.salary_text, job.employment_type]).lower()
def parse_experience(job: Job) -> None:
    blob = text(job); job.experience_text = ""
    # Prefer mandatory context; "preferred" ranges must not reject an otherwise eligible job.
    required = re.split(r"\b(preferred|nice to have|desired)\b", blob, maxsplit=1)[0]
    if re.search(r"\b(fresher|no experience required|graduate trainee|management trainee|entry[ -]?level)\b", required): job.experience_min, job.experience_max, job.experience_status, job.experience_text = 0, 0, "Eligible", "Entry-level / fresher"
    else:
        ranges = re.findall(r"\b(\d+(?:\.\d+)?)\s*(?:-|to|–)\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\b", required)
        plus = re.findall(r"\b(\d+(?:\.\d+)?)\s*\+\s*(?:years?|yrs?)\b", required)
        if ranges:
            lo, hi = map(float, ranges[0]); job.experience_min, job.experience_max, job.experience_text = lo, hi, f"{lo:g}-{hi:g} years"; job.experience_status = "Eligible" if hi <= 3 else "Ineligible"
        elif plus:
            lo = float(plus[0]); job.experience_min, job.experience_max, job.experience_text, job.experience_status = lo, lo + 0.1, f"{lo:g}+ years", "Ineligible" if lo >= 3 else "Experience Verification Required"

def parse_compensation(job: Job) -> None:
    blob = text(job); intern = bool(re.search(r"\b(intern|internship)\b", blob))
    if re.search(r"\bunpaid\b", blob) and intern: job.salary_status = "Ineligible"; return
    money_source = job.salary_text or job.description
    # A range commonly prints its currency only once: "₹8,000–12,000/month".
    nums = [float(x.replace(",", "")) for x in re.findall(r"(?<![A-Za-z])([\d,]+(?:\.\d+)?)", money_source)] if ("₹" in money_source or re.search(r"\b(?:inr|rs\.?|lpa|lakhs?)\b", money_source,re.I)) else []
    if not nums: return
    low, high = min(nums), max(nums); monthly = bool(re.search(r"\b(month|monthly|per month|/month)\b", job.salary_text.lower()))
    if intern and monthly:
        job.monthly_stipend, job.salary_min, job.salary_max, job.salary_period = low, low, high, "monthly"
        job.salary_status = "Eligible" if low >= 10000 else ("Salary Verification Required" if high >= 10000 else "Ineligible")
    elif not intern and ("lpa" in money_source.lower() or "lakhs" in money_source.lower()):
        job.ctc_lpa, job.salary_min, job.salary_max, job.salary_period = low, low, high, "annual LPA"
        job.salary_status = "Eligible" if low >= 8 else ("Salary Verification Required" if high >= 8 else "Ineligible")
    elif not intern and monthly:
        # Fixed monthly pay can be annualised, but it is not proof of a CTC offer.
        job.salary_min,job.salary_max,job.salary_period=low,high,"monthly INR"; job.monthly_fixed_salary=low; job.annualised_fixed_salary=low*12; job.compensation_type="fixed salary"; job.extraction_confidence="Medium"
        job.salary_status="Salary Verification Required" if high*12/100000>=8 else "Ineligible"
    elif intern and re.search(r"\bweek(?:ly)?\b",money_source,re.I):
        job.monthly_stipend=low*52/12; job.salary_period="weekly"; job.salary_status="Eligible" if job.monthly_stipend>=10000 else "Ineligible"
