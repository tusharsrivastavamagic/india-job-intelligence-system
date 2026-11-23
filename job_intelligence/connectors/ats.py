from __future__ import annotations
import asyncio, re
import httpx
from bs4 import BeautifulSoup
from ..models import Job

def clean(value: str | None) -> str: return BeautifulSoup(value or "", "html.parser").get_text(" ", strip=True)
async def fetch_board(board: dict, timeout: float, cap: int) -> list[Job]:
    ats, company, slug = board.get("ats", "").lower(), board.get("company", ""), board.get("board", "")
    if not all([ats, company, slug]): raise ValueError("Each board needs ats, company and board")
    if ats in {"workable", "recruitee", "breezy", "personio", "workday"}:
        from .additional_ats import fetch_extra
        return await fetch_extra(board, timeout, cap)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers={"User-Agent":"IndiaJobIntelligence/1.0"}) as client:
        if ats == "greenhouse":
            data = (await client.get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true")).json()["jobs"]
            return [Job(str(x["id"]), x["title"], company, ats, x["absolute_url"], x.get("location",{}).get("name", ""), clean(x.get("content")), x["absolute_url"], x.get("metadata",{}).get("employment_type",""), x.get("updated_at", ""), salary_text=clean(x.get("content")), raw=x) for x in data[:cap]]
        if ats == "lever":
            data = (await client.get(f"https://api.lever.co/v0/postings/{slug}?mode=json")).json()
            return [Job(x["id"], x["text"], company, ats, x["hostedUrl"], x.get("categories",{}).get("location", ""), x.get("descriptionPlain", ""), x.get("applyUrl", x["hostedUrl"]), x.get("categories",{}).get("commitment", ""), salary_text=x.get("descriptionPlain", ""), raw=x) for x in data[:cap]]
        if ats == "smartrecruiters":
            out=[]; offset=0
            while len(out) < cap:
                page=(await client.get(f"https://api.smartrecruiters.com/v1/companies/{slug}/postings", params={"limit":100,"offset":offset})).json().get("content",[])
                if not page: break
                for x in page:
                    url=x.get("ref", ""); out.append(Job(x.get("id",url),x.get("name",""),company,ats,url,x.get("location",{}).get("city",""),direct_apply_url=url,employment_type=x.get("typeOfEmployment",""),posted_date=x.get("releasedDate", ""),raw=x))
                offset += len(page)
            return out[:cap]
        if ats == "ashby":
            query="query { jobBoardWithTeams(jobBoardName: \"%s\") { jobs { id title locationName descriptionPlain employmentType publishedAt jobUrl applyUrl } } }" % slug
            data=(await client.post("https://jobs.ashbyhq.com/api/non-user-graphql",json={"query":query})).json()["data"]["jobBoardWithTeams"]["jobs"]
            return [Job(x["id"],x["title"],company,ats,x.get("jobUrl",""),x.get("locationName", ""),x.get("descriptionPlain", ""),x.get("applyUrl",x.get("jobUrl","")),x.get("employmentType", ""),x.get("publishedAt", ""),salary_text=x.get("descriptionPlain", ""),raw=x) for x in data[:cap]]
        raise ValueError(f"Unsupported public connector: {ats}. Supported: greenhouse, lever, ashby, smartrecruiters, workable, recruitee, breezy, personio, workday")

async def fetch_all(boards: list[dict], timeout: float, cap: int) -> tuple[list[Job], list[str]]:
    results = await asyncio.gather(*(fetch_board(b, timeout, cap) for b in boards), return_exceptions=True)
    jobs, errors = [], []
    for b, result in zip(boards, results):
        if isinstance(result, Exception): errors.append(f"{b.get('company','unknown')}/{b.get('ats','unknown')}: {result}")
        else: jobs.extend(result)
    return jobs, errors
