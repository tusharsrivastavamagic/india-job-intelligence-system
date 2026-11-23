# Downloaded repository audit

All five ZIP files were extracted only into a temporary audit directory outside this project. No upstream source was copied into this repository.

| Repository | What it does / sources | Internal approach | Licence / reuse decision |
|---|---|---|---|
| JobSpy | Python multi-board scraper: LinkedIn, Indeed, Glassdoor, Google, Naukri and others | Per-site modules, pagination/search, common records; descriptions and salary vary by provider | MIT (`LICENSE` present). Not copied; its modular boundary informed the clean-room connector design. Portal terms/rate limits need review before use. |
| Career Page Job Monitor | Apify-oriented ATS monitoring for Greenhouse, Lever, Ashby, Workable, Recruitee, SmartRecruiters, Workday | async HTTP adapters, normalisation, delta state, category signals; SmartRecruiters offset pagination | No licence file found. No code reused. Public endpoint knowledge was independently implemented and attribution is retained here. |
| ATS Jobs Scraper | Greenhouse, Lever, Ashby, SmartRecruiters, Workday company boards | Python HTTP/GraphQL requests; Workday paging/retry notes; standard output | MIT. Not copied; informed testable public-ATS architecture. Its descriptions/salary availability is source-dependent. |
| ATS Job Scraper | 14 ATS platforms including Workday, Oracle, Greenhouse, Lever, Ashby and Teamtailor | Node/Apify actor, adapter isolation, filters, dedupe, state and monitor mode | No licence file found. No code reused. Useful design reference only; claims were not adopted as production guarantees. |
| JobBot | FastAPI/React job tracker, ATS and remote/RSS discovery plus applying | SQLite, scrapers, AI scorer, application routers, form-fill/apply classes | No licence file found. No code reused. Automated application modules are explicitly excluded. |

## Detailed findings

**JobSpy:** dependencies are declared in `pyproject.toml`; dedicated provider packages expose search/pagination and record normalisation. Data commonly includes title, company, location, date, URLs and descriptions, with provider-dependent salary. It has no Google Sheets history system. Use is legally possible under MIT but copying it would create unnecessary provider coupling.

**Career Page Job Monitor:** its root and generated actors share `ats.py`, `delta.py`, `signal.py`, and async `main.py`; it tracks first-seen/closed board records in Apify state and has fixtures/tests. It does not implement India-specific salary, experience or company rules. The absence of a licence prevents source reuse.

**ATS Jobs Scraper:** `src/main.py` detects five ATS types. Greenhouse and Lever supply descriptions; SmartRecruiters loops pages; Workday needs full careers URL and careful pagination. It exposes job/company/location/department/type/date/URL and title guesses. It contains no universal India eligibility policy. MIT permits reuse with notice, but this project uses a smaller independently authored implementation.

**ATS Job Scraper:** `src/sources/` contains 14 adapters, `dedupe.js`, `filters.js`, `state.js`, and `enrich.js`. It has pagination, compensation parsing, monitoring and delivery. It is an Apify product and lacks an included licence; it is not reused.

**JobBot:** backend scrapers cover Greenhouse/Lever/RemoteOK/RSS and custom/playwright paths. Its tracking, filters, AI scoring, and notification ideas are relevant; its `appliers/` and apply router must not be used under the project requirement.

## Comparison and modifications

The final system reuses no source code. It builds independent public Greenhouse, Lever, Ashby and SmartRecruiters connectors, applies India-specific eligibility after normalisation, preserves history in Sheets, batches source failures, and provides a credential-free test suite. Workday, portal connectors, company evidence lookup, and Apify adapters are documented future work—not presented as implemented.
