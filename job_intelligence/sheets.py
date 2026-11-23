from __future__ import annotations
import base64, json, time
from datetime import date
from typing import Iterable
from .models import Job
TABS=["All Jobs","New Today","Strong Matches","Possible Matches","Paid Internships","Salary Undisclosed","Salary Verification Required","Company Verification Required","Experience Verification Required","Applied","Rejected and Closed","Source Statistics","System Logs"]
USER_FIELDS={"Application Status","Notes","Saved Status","Application Date","Follow-up Date","Contact Person","Current Stage","Personal Rating"}
def headers(): return ["Internal Job ID","Original Job ID","Job Title","Company","Company Classification","Founding Year","Company Age","Employee Count","Startup Verification Status","Company Verification Source","Source","Location","Country","Work Arrangement","India Remote Eligibility","Experience Minimum","Experience Maximum","Experience Text","Experience Verification Status","Employment Type","CTC LPA","Monthly Stipend INR","Salary Disclosure Status","Posted Date","Date Discovered","Job URL","Direct Apply URL","Match Score","Match Explanation","Job Status","First Seen Date","Last Seen Date","Duplicate Group ID","Application Status","Notes","Saved Status","Application Date","Follow-up Date","Contact Person","Current Stage","Personal Rating"]
def _is_429(exc: Exception) -> bool:
    response=getattr(exc,"response",None)
    return getattr(response,"status_code",None)==429 or "429" in str(exc) or "quota exceeded" in str(exc).lower()
def api_call(operation, attempts: int=4):
    """Retry short quota bursts without hiding non-quota API errors."""
    for attempt in range(attempts):
        try:return operation()
        except Exception as exc:
            if not _is_429(exc) or attempt==attempts-1: raise
            time.sleep(min(8,2**attempt))
def ensure_headers(ws, header: list[str], values=None) -> str:
    """Make row 1 safe for get_all_records without deleting existing worksheet data."""
    values=values if values is not None else api_call(ws.get_all_values)
    if not values:
        api_call(lambda:ws.append_row(header))
        return "empty"
    first=values[0]
    # Only an exact schema match is trusted. Blank/duplicate/mismatched headers are unsafe.
    if first==header:
        return "valid"
    # Insert rather than update/clear: preserves every pre-existing cell by shifting it down.
    api_call(lambda:ws.insert_row(header,1))
    return "repaired"
def tab_header(name: str, master_header: list[str]) -> list[str]:
    if name=="Source Statistics": return ["Source","Jobs discovered"]
    if name=="System Logs": return ["Run Date","Event","Details"]
    return master_header
def _client(settings):
    import gspread
    from google.oauth2.service_account import Credentials
    info=json.loads(base64.b64decode(settings.service_account_b64)); creds=Credentials.from_service_account_info(info,scopes=["https://www.googleapis.com/auth/spreadsheets"])
    return gspread.authorize(creds).open_by_key(settings.sheet_id)
def _batch_values(book, names: list[str]) -> dict[str,list[list[str]]]:
    """One Sheets values.batchGet request instead of one read per worksheet."""
    if hasattr(book,"values_batch_get"):
        response=api_call(lambda:book.values_batch_get([f"'{name}'!A:AO" for name in names]))
        result={name:[] for name in names}
        for name,entry in zip(names,response.get("valueRanges",[])):
            result[name]=entry.get("values",[])
        return result
    # Test doubles and older gspread compatibility.
    return {name:api_call(book.worksheet(name).get_all_values) for name in names}
def update(settings, jobs: list[Job], errors: list[str], book=None) -> set[str]:
    if not settings.sheet_id or not settings.service_account_b64: return {job.internal_id for job in jobs}
    book=book or _client(settings); header=headers()
    header_state={}
    for name in TABS:
        try: ws=book.worksheet(name)
        except Exception: ws=api_call(lambda:book.add_worksheet(name, rows=1000, cols=len(header)))
    values_by_tab=_batch_values(book,TABS)
    for name in TABS: header_state[name]=ensure_headers(book.worksheet(name),tab_header(name,header),values_by_tab[name])
    master=book.worksheet("All Jobs"); master_values=values_by_tab["All Jobs"]
    # Header was just inserted above legacy values, so reconstruct records directly without another read.
    if header_state["All Jobs"]=="repaired": master_values=[header]+master_values
    rows=[dict(zip(header,row)) for row in master_values[1:]] if master_values else []
    existing={r.get("Internal Job ID"):r for r in rows}
    current_values=[]; new_ids=set()
    for job in jobs:
        old=existing.get(job.internal_id,{})
        if old: job.first_seen_date=old.get("First Seen Date") or date.today().isoformat()
        else: job.first_seen_date=date.today().isoformat(); new_ids.add(job.internal_id)
        job.last_seen_date=date.today().isoformat(); r=job.row()
        evidence=settings.company_evidence.get(job.company) or settings.company_evidence.get(job.company.lower()) or {}
        founding=evidence.get("founding_year",""); age=date.today().year-founding if isinstance(founding,int) else ""
        mapped={"Internal Job ID":job.internal_id,"Original Job ID":job.original_id,"Job Title":job.title,"Company":job.company,"Company Classification":job.company_classification,"Founding Year":founding,"Company Age":age,"Employee Count":evidence.get("employee_count",""),"Startup Verification Status":job.startup_status,"Company Verification Source":evidence.get("source",""),"Source":job.source,"Location":job.location,"Country":job.country,"Work Arrangement":job.work_arrangement,"India Remote Eligibility":job.raw.get("india_remote_eligibility","Location Verification Required"),"Experience Minimum":job.experience_min,"Experience Maximum":job.experience_max,"Experience Text":job.experience_text,"Experience Verification Status":job.experience_status,"Employment Type":job.employment_type,"CTC LPA":job.ctc_lpa,"Monthly Stipend INR":job.monthly_stipend,"Salary Disclosure Status":job.salary_status,"Posted Date":job.posted_date,"Date Discovered":r["date_discovered"],"Job URL":job.job_url,"Direct Apply URL":job.direct_apply_url,"Match Score":job.match_score,"Match Explanation":job.match_explanation,"Job Status":job.job_status,"First Seen Date":job.first_seen_date,"Last Seen Date":job.last_seen_date,"Duplicate Group ID":job.duplicate_group_id}
        current_values.append([mapped.get(h, old.get(h, "")) if h not in USER_FIELDS else old.get(h, "") for h in header])
    # Preserve every historical row, including records no source returned today.
    current_ids={job.internal_id for job in jobs}
    historical_values=[[row.get(h, "") for h in header] for row in rows if row.get("Internal Job ID") not in current_ids]
    values=current_values + historical_values
    if values: api_call(lambda:master.update("A2", values))
    for category in TABS[1:10]:
        if header_state[category]=="repaired":
            # A user/legacy data sheet was repaired non-destructively; do not clear it.
            continue
        ws=book.worksheet(category); selected=[v for j,v in zip(jobs,current_values) if j.eligibility==category]
        ws.clear(); ws.append_row(header)
        if selected: ws.append_rows(selected)
    new_today=book.worksheet("New Today")
    new_rows=[v for j,v in zip(jobs,current_values) if j.first_seen_date == date.today().isoformat()]
    if header_state["New Today"]!="repaired":
        new_today.clear(); new_today.append_row(header)
        if new_rows: new_today.append_rows(new_rows)
    stats=book.worksheet("Source Statistics")
    counts={}
    for job in jobs: counts[job.source]=counts.get(job.source,0)+1
    if header_state["Source Statistics"]!="repaired":
        stats.clear(); stats.append_row(tab_header("Source Statistics",header))
        if counts: stats.append_rows([[source,count] for source,count in sorted(counts.items())])
    book.worksheet("System Logs").append_row([date.today().isoformat(), "run", f"jobs={len(jobs)} errors={'; '.join(errors)}"])
    return new_ids
