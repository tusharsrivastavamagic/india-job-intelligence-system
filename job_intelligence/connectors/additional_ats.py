"""Public ATS adapters kept separate so a failing ATS cannot affect others."""
from __future__ import annotations
import asyncio, re
import xml.etree.ElementTree as ET
import httpx
from .ats import clean
from ..models import Job

def _location(value):
    if isinstance(value, dict): return ", ".join(str(value.get(k,"")) for k in ("city","state","country") if value.get(k))
    return str(value or "")

async def fetch_extra(board: dict, timeout: float, cap: int) -> list[Job]:
    ats, company, token=board["ats"].lower(),board["company"],board["board"]
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True,headers={"User-Agent":"IndiaJobIntelligence/1.0"}) as client:
        if ats=="workable":
            payload=(await client.get(f"https://apply.workable.com/api/v1/widget/accounts/{token.lower()}",params={"details":"true"})).json()
            return [Job(str(x.get("shortcode") or x.get("id")),x.get("title",""),payload.get("name") or company,ats,x.get("url") or x.get("application_url", ""),_location(x),clean(x.get("description")),x.get("application_url") or x.get("url", ""),x.get("employment_type", ""),x.get("published_on") or x.get("created_at", ""),salary_text=clean(x.get("description")),raw=x) for x in payload.get("jobs",[])[:cap]]
        if ats=="recruitee":
            payload=(await client.get(f"https://{token.lower()}.recruitee.com/api/offers/")).json()
            return [Job(str(x.get("id","")),x.get("title") or x.get("position", ""),x.get("company_name") or company,ats,x.get("careers_url") or x.get("careers_apply_url", ""),_location(x) or _location((x.get("locations") or [{}])[0]),clean(x.get("description")),x.get("careers_apply_url") or x.get("careers_url", ""),x.get("employment_type_code", ""),x.get("published_at") or x.get("created_at", ""),salary_text=clean(x.get("description")),raw=x) for x in payload.get("offers",[])[:cap]]
        if ats=="breezy":
            payload=(await client.get(f"https://{token.lower()}.breezy.hr/json")).json()
            return [Job(str(x.get("id") or x.get("friendly_id","")),x.get("name",""),x.get("company",{}).get("name") or company,ats,x.get("url", ""),_location(x.get("location")),clean(x.get("description")),(x.get("url","").rstrip("/")+"/apply"),str(x.get("type",{}).get("name", "")),x.get("published_date", ""),salary_text=str(x.get("salary", "")),raw=x) for x in payload[:cap]]
        if ats=="personio":
            url=token if token.startswith("http") else f"https://{token}.jobs.personio.de/xml"
            root=ET.fromstring((await client.get(url)).text); host=url.split("/xml")[0]
            out=[]
            for pos in root.findall(".//position")[:cap]:
                get=lambda name: (pos.findtext(name) or "").strip()
                identifier=get("id"); descriptions=" ".join((v.text or "") for v in pos.findall(".//jobDescription/value"))
                out.append(Job(identifier,get("name"),get("subcompany") or company,ats,f"{host}/job/{identifier}",get("office"),clean(descriptions),f"{host}/job/{identifier}?display=apply",get("schedule") or get("employmentType"),get("createdAt"),salary_text=clean(descriptions),raw={"personio_id":identifier}))
            return out
        if ats=="workday":
            match=re.search(r"https?://([^.]+)\.(wd\d+)\.myworkdayjobs\.com/([^/?#]+)",token)
            if not match: raise ValueError("Workday board must be its full myworkdayjobs.com careers URL")
            tenant,dc,site=match.groups(); endpoint=f"https://{tenant}.{dc}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"; out=[]; offset=0
            while len(out)<cap:
                page=(await client.post(endpoint,json={"appliedFacets":{},"limit":20,"offset":offset,"searchText":""})).json(); items=page.get("jobPostings",[])
                if not items: break
                for x in items:
                    path=x.get("externalPath",""); url=f"https://{tenant}.{dc}.myworkdayjobs.com/en-US/{site}{path}"
                    out.append(Job(str(x.get("bulletFields",[url])[0]),x.get("title",""),company,ats,url,x.get("locationsText",""),direct_apply_url=url,raw=x))
                offset+=len(items)
                if offset>=page.get("total",0): break
                await asyncio.sleep(.3)
            return out[:cap]
    raise ValueError(f"Unsupported public connector: {ats}")
