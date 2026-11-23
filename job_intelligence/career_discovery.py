"""Low-rate, opt-in ATS detection for already known official career URLs."""
from __future__ import annotations
import re, httpx
PATTERNS={"greenhouse":r"boards\.greenhouse\.io/([^/?#]+)","lever":r"jobs\.lever\.co/([^/?#]+)","ashby":r"jobs\.ashbyhq\.com/([^/?#]+)","workable":r"apply\.workable\.com/([^/?#]+)","recruitee":r"([\w-]+)\.recruitee\.com","breezy":r"([\w-]+)\.breezy\.hr","personio":r"([\w-]+)\.jobs\.personio\.(?:de|com)","teamtailor":r"([\w-]+)\.teamtailor\.com","workday":r"https?://[^\"']+\.myworkdayjobs\.com/[^\"'/?#]+"}
async def discover(career_url:str, timeout:float=15)->dict:
    async with httpx.AsyncClient(timeout=timeout,follow_redirects=True,headers={"User-Agent":"IndiaJobIntelligence/1.0"}) as client:
        response=await client.get(career_url); text=str(response.url)+"\n"+response.text
    for ats,pattern in PATTERNS.items():
        match=re.search(pattern,text,re.I)
        if match: return {"career_page_url":str(response.url),"ats":ats,"board":match.group(0) if ats=="workday" else match.group(1),"verified":True}
    return {"career_page_url":str(response.url),"ats":"unknown","board":"","verified":False}
