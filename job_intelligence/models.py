from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import date
from typing import Any

@dataclass
class Job:
    original_id: str; title: str; company: str; source: str; job_url: str
    location: str = ""; description: str = ""; direct_apply_url: str = ""; employment_type: str = ""
    posted_date: str = ""; department: str = ""; salary_text: str = ""; work_arrangement: str = ""
    raw: dict[str, Any] = field(default_factory=dict)
    internal_id: str = ""; country: str = ""; experience_min: float | None = None; experience_max: float | None = None
    experience_text: str = ""; experience_status: str = "Experience Verification Required"; salary_min: float | None = None
    salary_max: float | None = None; salary_period: str = ""; ctc_lpa: float | None = None; monthly_stipend: float | None = None
    monthly_fixed_salary: float | None = None; annualised_fixed_salary: float | None = None; salary_currency: str = "INR"; compensation_type: str = ""; extraction_confidence: str = "Low"
    salary_status: str = "Salary Undisclosed"; eligibility: str = "Possible Matches"; exclusion_reason: str = ""
    company_classification: str = "Company Verification Required"; startup_status: str = "Company Verification Required"
    match_score: int = 0; match_explanation: str = ""; first_seen_date: str = ""; last_seen_date: str = ""; job_status: str = "Active"; duplicate_group_id: str = ""
    def row(self) -> dict[str, Any]: return asdict(self) | {"date_discovered": date.today().isoformat()}
