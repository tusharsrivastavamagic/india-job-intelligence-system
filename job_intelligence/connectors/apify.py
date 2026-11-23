"""Optional, capped Apify adapter. Nothing runs unless a matching env flag is true."""
from __future__ import annotations
from threading import Lock
from typing import Callable
from ..models import Job

ACTORS={
 "linkedin":"blackfalcondata/linkedin-job-scraper", "naukri":"valig/naukri-jobs-scraper", "iimjobs":"data_daemon/iimjobs-jobs-scraper",
 "glassdoor":"valig/glassdoor-jobs-scraper", "google_jobs":"belcaidsaad/job-scraper-with-hiring-urgency-company-size-saad-belcaid", "workday":"fantastic-jobs/workday-jobs-api"}

class TokenManager:
    """Thread-safe round-robin selection; unavailable tokens are skipped for this run."""
    def __init__(self, tokens):
        self._tokens=tuple(dict.fromkeys(token.strip() for token in tokens if token and token.strip()))
        self._unavailable=set(); self._index=0; self._lock=Lock()
    @property
    def count(self): return len(self._tokens)
    def acquire(self):
        with self._lock:
            for _ in self._tokens:
                token=self._tokens[self._index%len(self._tokens)]; self._index+=1
                if token not in self._unavailable:return token
        return None
    def mark_unavailable(self, token):
        with self._lock:self._unavailable.add(token)
def _token_failure(exc:Exception)->bool:
    status=getattr(getattr(exc,"response",None),"status_code",None); message=str(exc).lower()
    return status in {401,403,408,429,500,502,503,504} or any(word in message for word in ("rate limit","quota","authentication","unauthorized","temporary","timeout"))

def _pick(item:dict,*names:str)->str:
    for name in names:
        value=item.get(name)
        if value not in (None,""): return str(value)
    return ""

def fetch_apify(settings, client_factory:Callable|None=None) -> tuple[list[Job],list[str]]:
    enabled=[name for name,on in settings.apify_enabled.items() if on]
    if not enabled: return [],[]
    tokens=getattr(settings,"apify_tokens",()) or ((getattr(settings,"apify_token","").strip(),) if getattr(settings,"apify_token","").strip() else ())
    manager=TokenManager(tokens)
    if not manager.count: return [],["Apify enabled but no token is configured; no actor was run."]
    if client_factory is None:
        try:
            from apify_client import ApifyClient
            client_factory=ApifyClient
        except ImportError: return [],["apify-client unavailable; run: python -m pip install -r requirements.txt"]
    jobs=[]; errors=[]
    for name in enabled:
        dataset=None
        for _ in range(manager.count):
            token=manager.acquire()
            if token is None: break
            try:
                client=client_factory(token)
                run=client.actor(ACTORS[name]).call(run_input=settings.apify_actor_inputs.get(name,{}))
                dataset=client.dataset(run["defaultDatasetId"]).list_items(limit=settings.apify_max_items).items
                break
            except Exception as exc:
                if _token_failure(exc): manager.mark_unavailable(token); continue
                errors.append(f"Apify {name}: actor request failed."); break
        if dataset is None:
            errors.append(f"Apify {name}: no available token completed the request.")
            continue
        try:
            for item in dataset:
                title=_pick(item,"title","jobTitle","position"); company=_pick(item,"company","companyName","company_name"); url=_pick(item,"applyUrl","applicationUrl","jobUrl","url","link")
                if title and company and url:
                    jobs.append(Job(_pick(item,"id","jobId","job_id") or url,title,company,f"apify:{name}",url,_pick(item,"location","jobLocation"),_pick(item,"description","jobDescription"),url,_pick(item,"employmentType","jobType"),_pick(item,"postedDate","datePosted"),salary_text=_pick(item,"salary","salaryText","compensation"),raw=item))
        except Exception: errors.append(f"Apify {name}: response normalization failed.")
    return jobs,errors
