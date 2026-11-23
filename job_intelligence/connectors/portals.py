"""Role-first portal discovery backed by the MIT-licensed python-jobspy package."""
from __future__ import annotations
from datetime import date, datetime
from typing import Any
from ..models import Job

SUPPORTED_PORTALS={"naukri", "linkedin", "indeed", "google", "glassdoor"}

def _value(row: dict[str, Any], name: str) -> Any:
    value=row.get(name)
    return "" if value is None or str(value)=="nan" else value

def _salary_text(row: dict[str, Any]) -> str:
    currency=str(_value(row,"currency")).upper()
    low, high, interval=_value(row,"min_amount"),_value(row,"max_amount"),_value(row,"interval")
    if currency not in {"INR", "₹"} or not (low or high): return ""
    amounts="–".join(str(int(float(x))) for x in (low,high) if x not in ("",None))
    return f"₹{amounts} {interval or ''}".strip()

def _date(value: Any) -> str:
    if isinstance(value,(date,datetime)): return value.isoformat()
    return str(value or "")

def fetch_roles(roles: list[str], portals: list[str], results_per_query: int, fetch_descriptions: bool) -> tuple[list[Job],list[str]]:
    """Search each role in India. Individual role failures do not stop later roles."""
    requested=[p for p in portals if p in SUPPORTED_PORTALS]
    errors=[f"Unsupported portal skipped: {p}" for p in portals if p not in SUPPORTED_PORTALS]
    if not roles or not requested: return [], errors
    try:
        from jobspy import scrape_jobs
    except ImportError:
        return [], errors+["python-jobspy is unavailable; run: python -m pip install -r requirements.txt"]
    jobs=[]
    for role in roles:
        try:
            frame=scrape_jobs(site_name=requested,search_term=role,location="India",country_indeed="india",is_remote=None,results_wanted=results_per_query,fetch_description=fetch_descriptions,verbose=0)
            for row in frame.to_dict("records"):
                url=str(_value(row,"job_url")); title=str(_value(row,"title")); company=str(_value(row,"company"))
                if not (url and title and company): continue
                source=str(_value(row,"site")); location=str(_value(row,"location")); description=str(_value(row,"description"))
                jobs.append(Job(str(_value(row,"id")) or url,title,company,source,url,location,description,url,str(_value(row,"job_type")),_date(_value(row,"date_posted")),salary_text=_salary_text(row),raw={"role_query":role}))
            for source, message in frame.attrs.get("errors",{}).items(): errors.append(f"{role}/{source}: {message}")
        except Exception as exc:
            errors.append(f"{role}: {exc}")
    return jobs,errors
