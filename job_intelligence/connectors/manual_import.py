"""Compliant CSV intake for portals without a permitted automated interface."""
from __future__ import annotations
import csv
from pathlib import Path
from ..models import Job
REQUIRED={"title","company","url"}
def load_csv(path:str, source:str)->list[Job]:
    with Path(path).open(encoding="utf-8-sig",newline="") as handle:
        rows=list(csv.DictReader(handle)); missing=REQUIRED-set(rows[0] if rows else [])
    if missing: raise ValueError(f"CSV missing required columns: {', '.join(sorted(missing))}")
    return [Job(r.get("id") or r["url"],r["title"],r["company"],source,r["url"],r.get("location", ""),r.get("description", ""),r.get("apply_url") or r["url"],r.get("employment_type", ""),r.get("posted_date", ""),salary_text=r.get("salary", ""),raw=r) for r in rows]
