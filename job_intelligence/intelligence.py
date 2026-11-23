"""Explainable secondary classifiers for remote eligibility and role relevance."""
from __future__ import annotations
import re
from .models import Job

FUNCTIONS={
 "Marketing":("marketing","brand","seo","content","communications","advertising","public relations"),
 "Sales & Business Development":("sales","business development","partnership","account executive","growth"),
 "Finance":("finance","financial analyst","investment","banking","fintech","corporate finance"),
 "Analytics":("business analyst","data analyst","analytics","business intelligence","market research"),
 "People & Operations":("human resources"," hr ","recruiter","operations","supply chain","procurement","logistics"),
 "Strategy & Consulting":("strategy","consulting","project manager","management trainee","customer success"),}
FOREIGN=re.compile(r"\b(usa|united states|uk only|europe only|canada only|australia only|work authorization in)\b",re.I)
INDIA=re.compile(r"\b(india|indian|ist|bengaluru|bangalore|mumbai|pune|delhi|hyderabad|chennai|kolkata)\b",re.I)
def classify_function(job:Job)->str:
    text=f"{job.title} {job.department} {job.description}".lower(); hits=[name for name,terms in FUNCTIONS.items() if any(t in text for t in terms)]
    return ", ".join(hits) if hits else "Unclassified"
def remote_eligibility(job:Job)->str:
    text=f"{job.location} {job.description}"; lower=text.lower()
    if "remote" not in lower: return "Onsite/Hybrid India" if INDIA.search(text) else "Location Verification Required"
    if FOREIGN.search(text): return "Location Verification Required"
    return "Remote eligible in India" if INDIA.search(text) else "Location Verification Required"
