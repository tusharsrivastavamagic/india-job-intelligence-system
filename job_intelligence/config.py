from __future__ import annotations
import json, os
from dataclasses import dataclass
from dotenv import load_dotenv

def _bool(name: str, default=False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes"}

@dataclass(frozen=True)
class Settings:
    sheet_id: str
    service_account_b64: str
    gmail_address: str
    gmail_password: str
    email_recipient: str
    apify_token: str
    apify_tokens: tuple[str, ...]
    min_ctc_lpa: float
    min_stipend: float
    max_experience: float
    role_queries: list[str]
    portal_sources: list[str]
    portal_results_per_query: int
    portal_fetch_descriptions: bool
    apify_actor_inputs: dict
    apify_max_items: int
    company_evidence: dict
    boards: list[dict]
    timeout: float
    max_connector_jobs: int
    send_email: bool
    apify_enabled: dict[str, bool]
    test_sheet_id: str
    gemini_api_key: str
    gemini_model: str
    gemini_enabled: bool
    gemini_max_jobs: int
    gemini_max_requests: int
    gemini_max_output_tokens: int
    production_enabled: bool

def load_settings() -> Settings:
    load_dotenv()
    raw = os.getenv("TARGET_BOARDS_JSON", "[]")
    try:
        boards = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("TARGET_BOARDS_JSON must be a JSON array") from exc
    if not isinstance(boards, list): raise ValueError("TARGET_BOARDS_JSON must be a JSON array")
    try: actor_inputs=json.loads(os.getenv("APIFY_ACTOR_INPUTS_JSON", "{}"))
    except json.JSONDecodeError as exc: raise ValueError("APIFY_ACTOR_INPUTS_JSON must be a JSON object") from exc
    if not isinstance(actor_inputs, dict): raise ValueError("APIFY_ACTOR_INPUTS_JSON must be a JSON object")
    try: company_evidence=json.loads(os.getenv("COMPANY_EVIDENCE_JSON", "{}"))
    except json.JSONDecodeError as exc: raise ValueError("COMPANY_EVIDENCE_JSON must be a JSON object") from exc
    if not isinstance(company_evidence, dict): raise ValueError("COMPANY_EVIDENCE_JSON must be a JSON object")
    roles = [x.strip() for x in os.getenv("ROLE_QUERIES", "").split(",") if x.strip()]
    portals = [x.strip().lower() for x in os.getenv("PORTAL_SOURCES", "").split(",") if x.strip()]
    configured_tokens=tuple(token.strip() for token in os.getenv("APIFY_TOKENS", "").split(",") if token.strip())
    legacy_token=os.getenv("APIFY_TOKEN", "").strip()
    apify_tokens=configured_tokens or ((legacy_token,) if legacy_token else ())
    return Settings(os.getenv("GOOGLE_SHEET_ID", ""), os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON_BASE64", ""),
        os.getenv("GMAIL_ADDRESS", ""), os.getenv("GMAIL_APP_PASSWORD", ""), os.getenv("EMAIL_RECIPIENT", ""),
        legacy_token, apify_tokens, float(os.getenv("MINIMUM_CTC_LPA", "8")),
        float(os.getenv("MINIMUM_INTERNSHIP_STIPEND_INR_MONTHLY", "10000")), float(os.getenv("MAXIMUM_EXPERIENCE_YEARS", "3")), roles, portals,
        int(os.getenv("PORTAL_RESULTS_PER_QUERY", "25")), _bool("PORTAL_FETCH_DESCRIPTIONS", True), actor_inputs, int(os.getenv("APIFY_MAX_ITEMS_PER_ACTOR", "50")), company_evidence, boards,
        float(os.getenv("REQUEST_TIMEOUT_SECONDS", "25")), int(os.getenv("MAX_CONNECTOR_JOBS", "250")), _bool("SEND_EMAIL", True),
        {k: _bool("APIFY_ENABLE_" + k.upper()) for k in ["linkedin","naukri","iimjobs","glassdoor","google_jobs","workday"]}, os.getenv("TEST_GOOGLE_SHEET_ID", ""), os.getenv("GEMINI_API_KEY", ""), os.getenv("GEMINI_MODEL","gemini-3.1-flash-lite"), _bool("GEMINI_ENABLED",False), int(os.getenv("GEMINI_MAX_JOBS_PER_DIGEST","20")), int(os.getenv("GEMINI_MAX_REQUESTS_PER_RUN","5")), int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS","4000")),_bool("PRODUCTION_ENABLED",False))
