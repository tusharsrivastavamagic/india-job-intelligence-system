from __future__ import annotations
from collections import Counter
from .models import Job
def summary(jobs:list[Job], errors:list[str])->dict:
    return {"by_source":dict(Counter(j.source for j in jobs)),"by_function":dict(Counter(j.raw.get("function_classification","Unclassified") for j in jobs)),"by_location":dict(Counter(j.location or "Unknown" for j in jobs)),"by_category":dict(Counter(j.eligibility for j in jobs)),"connector_errors":len(errors),"salary_disclosed":sum(j.salary_status!="Salary Undisclosed" for j in jobs)}
