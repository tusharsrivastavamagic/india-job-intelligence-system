# India Job Intelligence System

> A safety-gated job-intelligence pipeline for early-career roles in India. It discovers configured roles, applies transparent eligibility and company checks, removes duplicates, optionally adds Gemini insights, and can publish a curated Google Sheets and Gmail digest.

**Status:** the local mocked workflow is ready; external integrations are opt-in and require operator configuration. Latest local verification: **46 tests passed** (mocked; no live API, email, Sheets, or scraping calls).

> [!WARNING]
> Some commands contact job sites, Apify, Gemini, Google Sheets, or Gmail. Start with the local test suite and mock dry-run; read [Running the system](#running-the-system) before a live command.

## Contents

- [Overview](#overview)
- [Features and delivery status](#features-and-delivery-status)
- [Eligibility and verification rules](#eligibility-and-verification-rules)
- [Data sources](#data-sources)
- [Architecture and repository structure](#architecture-and-repository-structure)
- [Installation and configuration](#installation-and-configuration)
- [Integrations](#integrations)
- [Running the system](#running-the-system)
- [Operations](#operations)
- [Operating safely](#operating-safely)
- [Our Implementation Journey](#our-implementation-journey)
- [Roadmap, quick start, and FAQ](#roadmap-quick-start-and-faq)

## Overview

This system is for an individual job seeker, career team, or small operations team tracking early-career business roles in India. It is **role-led**, not a company-name list: configured role queries and explicitly configured ATS boards supply candidates; employer evidence is used later for verification and startup classification.

It reduces repeated multi-source searching, inconsistent screening, duplicate listings, and fragile manual tracking. The actual pipeline is:

~~~text
Role queries / configured ATS boards / compliant manual CSV
  → source discovery → normalized job records
  → India, function, experience and pay rules
  → company evidence and startup classification
  → deduplication and merged source attribution
  → optional Gemini enrichment
  → production-only Google Sheets and Gmail digest
~~~

## Features and delivery status

| Area | Actual implementation | Status |
|---|---|---|
| Job discovery | JobSpy role searches across configured portals in India. | Implemented; live reliability varies |
| ATS connectors | Greenhouse, Lever, SmartRecruiters, Ashby, Workable, Recruitee, Breezy, Personio, and Workday adapters. | Implemented; requires valid target boards |
| Apify | Optional actors for LinkedIn, Naukri, IIMJobs, Glassdoor, Google Jobs, and Workday. | Implemented; disabled by default |
| Filtering | Location, target function, experience, salary/stipend, and employment checks. | Implemented |
| Company verification | Evidence-driven startup classification and review statuses. | Implemented; manual evidence required |
| Deduplication | Stable ID/URL matching plus conservative content matching; source strings are merged. | Implemented |
| Google Sheets | Header recovery, test/production guard, historical records, user-field preservation, source counts. | Implemented; credentials required |
| Gmail digest | UTF-8 HTML digest and configured-recipient test mail. | Implemented; SMTP required |
| Gemini AI | Optional structured summaries, skills, verification notes, limits, and cache. | Implemented; disabled by default |
| Manual imports | Compliant CSV normalization connector. | Implemented as a module; no main CLI import flag |
| Automation | GitHub Actions scheduled/manual workflow. | Implemented; operator-managed |
| Repost/closure lifecycle | Automatic closure detection and full repost lifecycle. | Pending |

“Implemented” means code exists and applicable local tests use mocks. It does not mean each provider, account, actor, or portal has been live-validated or will always return jobs.

## Eligibility and verification rules

| Rule | Current behavior |
|---|---|
| India and remote | India roles are eligible. Remote roles must be India-compatible; foreign-only restrictions are excluded. Missing/ambiguous remote detail becomes location-verification work. |
| Target domains | Titles/descriptions must match configured target functions, including marketing, sales/BD, finance, analytics, people/operations, and strategy/consulting. |
| Experience | Requirements above MAXIMUM_EXPERIENCE_YEARS (default 3) are excluded. Unclear requirements are retained for experience verification. |
| Full-time pay | Explicit annual CTC below MINIMUM_CTC_LPA (default 8) is excluded. Monthly fixed pay is annualised for review, but is not assumed to be confirmed CTC. |
| Internship pay | Explicit monthly stipend below MINIMUM_INTERNSHIP_STIPEND_INR_MONTHLY (default ₹10,000) is excluded. Unpaid internships are excluded. Ranges/ambiguity require verification. |
| Startups | A startup needs classification, founding year, employee count, and evidence source. It is eligible only at age ≥5 years and ≥90 employees. |
| Established/MNC employers | A verified non-startup is retained as Not a startup; it is not rejected merely for being established. |
| Uncertainty | Missing salary, experience, location, or company evidence is categorized for review rather than guessed. |

Common categories are **Strong Matches**, **Possible Matches**, **Paid Internships**, **Salary Undisclosed**, **Salary Verification Required**, **Company Verification Required**, and **Experience Verification Required**. Individual records can also carry a location-verification status; there is not currently a dedicated Sheets tab for that label.

## Data sources

| Source | Connector | Configuration/status | Credentials | Known limitations |
|---|---|---|---|---|
| Naukri, LinkedIn, Indeed, Google, Glassdoor | portals.py / JobSpy | PORTAL_SOURCES, role queries, India location | None in this path | Public-site blocking, 429s, missing descriptions and empty responses occur. |
| Greenhouse, Lever, SmartRecruiters, Ashby | ats.py | TARGET_BOARDS_JSON | Normally none for public boards | Exact board identifiers are necessary. |
| Workable, Recruitee, Breezy, Personio, Workday | additional_ats.py | TARGET_BOARDS_JSON | Normally none for public boards | Endpoint formats vary; Workday needs correct CXS URL. |
| LinkedIn, Naukri, IIMJobs, Glassdoor, Google Jobs, Workday | apify.py | Per-actor APIFY_ENABLE_* flags | Apify token(s) | Actor cost, account quota, and output quality apply. |
| User-supplied/IIMJobs/Hirist exports | manual_import.py | Controlled manual workflow | None | No site scraping; no built-in import CLI command. |
| Official career pages | career_discovery.py | Opt-in helper | None | Targeted discovery only; not a mass crawler. |

There are no native Oracle, SAP SuccessFactors, iCIMS, Jobvite, Teamtailor, or Zoho connectors at present.

## Architecture and repository structure

~~~mermaid
flowchart LR
  A[Roles / ATS boards / CSV] --> B[Discovery]
  B --> C[Normalization]
  C --> D[Rules and company evidence]
  D --> E[Deduplication / source merge]
  E --> F[Optional Gemini]
  F --> G{Production enabled?}
  G -->|Yes| H[Google Sheets]
  G -->|Yes| I[Gmail digest]
  G -->|No| J[Local result only]
~~~

Gemini does not make eligibility decisions; policy and evidence do. Deduplication first uses stable IDs/apply URLs, then conservative company/title/location plus description-token similarity.

~~~text
india-job-intelligence-system/
├── job_intelligence/
│   ├── main.py                 # CLI, orchestration, production gate
│   ├── config.py               # .env parsing and defaults
│   ├── portals.py, ats.py, additional_ats.py
│   ├── apify.py                # Actors and token manager
│   ├── rules.py, company.py, dedupe.py, intelligence.py
│   ├── sheets.py, email_digest.py, gemini.py
│   └── manual_import.py, career_discovery.py
├── tests/                      # Mocked unit/regression coverage
├── docs/                       # Detailed technical/audit documentation
├── .github/workflows/daily.yml # Scheduled/manual deployment workflow
├── .env.example                # Safe configuration template
├── requirements.txt
└── README.md                   # This combined guide and implementation record
~~~

Technology actually used: Python, python-jobspy, BeautifulSoup4, httpx, apify-client, gspread, google-auth, python-dotenv, Gmail SMTP/MIME email, Gemini REST, pytest, and GitHub Actions. Recorded local setup used Python 3.13; the Actions workflow uses Python 3.12.

## Installation and configuration

### Windows installation

The recorded machine used Windows PowerShell 5.1 and Python 3.13.12. On it, py and python3 were unavailable; python worked.

~~~powershell
cd "C:\path\to\india-job-intelligence-system"
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
~~~

If activation is blocked for this session, use Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass, then activate again. Keep .env private. Reinstall dependencies with python -m pip install -r requirements.txt.

Safe first checks:

~~~powershell
python -m pytest -q
python -m job_intelligence.main --mock-dry-run
~~~

### Configuration reference

The root .env is loaded by python-dotenv. Use placeholders, never real secrets in tracked files.

| Variable | Purpose | Required | Default | Example |
|---|---|---:|---|---|
| **General** |||||
| TIMEZONE | Display/schedule context | No | Asia/Kolkata | Asia/Kolkata |
| DAILY_RUN_TIME | Documented run time | No | 09:00 | 09:00 |
| SEND_EMAIL | Allow digest in production flow | No | true | false |
| PRODUCTION_ENABLED | Second real-run safety gate | Yes for production | false | true |
| **Search and filters** |||||
| ROLE_QUERIES | Comma-separated role searches | No | Built-in early-career list | marketing analyst,consulting analyst |
| PORTAL_SOURCES | JobSpy sources | No | naukri,linkedin,indeed,google,glassdoor | naukri,linkedin |
| PORTAL_RESULTS_PER_QUERY | Requested results per query | No | 25 | 10 |
| PORTAL_FETCH_DESCRIPTIONS | Fetch descriptions where available | No | true | false |
| MINIMUM_CTC_LPA | Annual CTC floor | No | 8 | 8 |
| MINIMUM_INTERNSHIP_STIPEND_INR_MONTHLY | Monthly stipend floor | No | 10000 | 10000 |
| MAXIMUM_EXPERIENCE_YEARS | Required-experience ceiling | No | 3 | 3 |
| TARGET_BOARDS_JSON | ATS board list | No | [] | [{"platform":"greenhouse","board":"example"}] |
| REQUEST_TIMEOUT_SECONDS | Connector timeout | No | 25 | 25 |
| MAX_CONNECTOR_JOBS | Per-connector cap | No | 250 | 100 |
| **Apify** |||||
| APIFY_TOKENS | Preferred comma-separated token list | No | empty | <TOKEN_1>,<TOKEN_2> |
| APIFY_TOKEN | Legacy one-token fallback | No | empty | <TOKEN> |
| APIFY_ENABLE_LINKEDIN / NAUKRI / IIMJOBS / GLASSDOOR / GOOGLE_JOBS / WORKDAY | Per-actor switches | No | false | true |
| APIFY_ACTOR_INPUTS_JSON | Actor overrides | No | {} | {"linkedin":{"maxItems":20}} |
| APIFY_MAX_ITEMS_PER_ACTOR | Actor result cap | No | 50 | 20 |
| **Company evidence** |||||
| COMPANY_EVIDENCE_JSON | Evidence/classification map | No | {} | {"Example Co":{"classification":"startup",...}} |
| **Google Sheets** |||||
| GOOGLE_SHEET_ID | Production spreadsheet | Yes for production Sheets | empty | <PRODUCTION_SHEET_ID> |
| TEST_GOOGLE_SHEET_ID | Isolated test spreadsheet | Yes for Sheets test | empty | <TEST_SHEET_ID> |
| GOOGLE_SERVICE_ACCOUNT_JSON_BASE64 | Base64 service account JSON | Yes for Sheets | empty | <BASE64_JSON> |
| **Gmail** |||||
| GMAIL_ADDRESS | SMTP sender | Yes for email | empty | sender@example.com |
| GMAIL_APP_PASSWORD | Gmail app password | Yes for email | empty | <APP_PASSWORD> |
| EMAIL_RECIPIENT | Digest/test recipient | Yes for email | empty | recipient@example.com |
| **Gemini** |||||
| GEMINI_ENABLED | Enable AI | No | false | true |
| GEMINI_API_KEY | AI credential | Yes when enabled | empty | <GEMINI_API_KEY> |
| GEMINI_MODEL | Model | No | gemini-3.1-flash-lite | gemini-3.1-flash-lite |
| GEMINI_MAX_JOBS_PER_DIGEST | AI job cap | No | 20 | 10 |
| GEMINI_MAX_REQUESTS_PER_RUN | AI request cap | No | 5 | 3 |
| GEMINI_MAX_OUTPUT_TOKENS | Output budget | No | 4000 | 2000 |

## Integrations

### Apify setup

Create an Apify account and configure token(s) locally:

~~~ini
# Preferred. Any number is supported; whitespace and empty items are ignored.
APIFY_TOKENS=<APIFY_TOKEN_1>, <APIFY_TOKEN_2>, <APIFY_TOKEN_3>

# Used only if APIFY_TOKENS is empty.
APIFY_TOKEN=<LEGACY_APIFY_TOKEN>

APIFY_ENABLE_LINKEDIN=false
APIFY_ENABLE_NAUKRI=false
APIFY_ENABLE_IIMJOBS=false
APIFY_ENABLE_GLASSDOOR=false
APIFY_ENABLE_GOOGLE_JOBS=false
APIFY_ENABLE_WORKDAY=false
APIFY_ACTOR_INPUTS_JSON={}
APIFY_MAX_ITEMS_PER_ACTOR=50
~~~

The preferred list overrides the legacy variable. The thread-safe manager uses healthy tokens in round-robin order. Rate limits, quota exhaustion, authentication failures, timeouts, and temporary server errors mark only that token unavailable for the current run; another healthy token can be attempted. Attempts are bounded by the number of configured tokens. Tokens are never deliberately put into error messages or logs. Actor schema, costs and limits depend on the selected actor, so leave actors disabled until their cost/terms are understood.

### Google Sheets setup and workflow

1. Create a Google Cloud project and enable Google Sheets API.
2. Create a service account; securely obtain its JSON, Base64-encode it, and put only the encoded value in GOOGLE_SERVICE_ACCOUNT_JSON_BASE64.
3. Create separate production and test spreadsheets and share each with the service-account email as editor.
4. Put their IDs in GOOGLE_SHEET_ID and TEST_GOOGLE_SHEET_ID.
5. Use --test-sheets only for the isolated test sheet; code rejects a test ID matching production.

Tabs are: All Jobs, New Today, Strong Matches, Possible Matches, Paid Internships, Salary Undisclosed, Salary Verification Required, Company Verification Required, Experience Verification Required, Applied, Rejected and Closed, Source Statistics, and System Logs.

Before records are read, headers are checked. A blank tab receives canonical headers. A tab with existing rows but missing/malformed headers receives an inserted header row, shifting data down—never clearing or overwriting existing rows. Historical jobs and manually maintained application status, notes, saved status, dates, contact, stage, and personal rating are preserved. All Jobs is historical; category tabs are refreshed views. Source statistics are simple counts, not a full analytics warehouse.

For a Sheets HTTP 429, the implementation batches value reads and has bounded exponential backoff. Wait for quota recovery and avoid concurrent tests; attribution can be per service account/user. Never resolve a malformed test tab by clearing production history.

### Gmail setup and email digest

Use Gmail with 2-Step Verification and an app password. Configure sender, app password, and recipient, then deliberately send:

~~~powershell
python -m job_intelligence.main --test-email
~~~

The HTML digest includes categories, job/company/location, compensation and verification context, source attribution, apply links, and optional AI summaries. MIME headers/body explicitly use UTF-8, supporting an em dash, ₹, and other Unicode. Do not use an ordinary Gmail password or paste credentials into a terminal, issue, or screenshot.

### Gemini AI setup

Gemini is optional: collection, rules, verification, and deduplication work without it. When enabled, it produces structured summaries, skills, and verification notes, caches results under ignored cache/, applies job/request/output caps, validates response structure, and falls back cleanly on errors.

~~~ini
GEMINI_ENABLED=true
GEMINI_API_KEY=<GEMINI_API_KEY>
GEMINI_MODEL=gemini-3.1-flash-lite
GEMINI_MAX_JOBS_PER_DIGEST=20
GEMINI_MAX_REQUESTS_PER_RUN=5
GEMINI_MAX_OUTPUT_TOKENS=4000
~~~

~~~powershell
python -m job_intelligence.main --test-ai
~~~

Cost remains provider-dependent. AI output is supplementary, not a rules decision.

> [!CAUTION]
> **Pending security work:** the current Gemini endpoint path uses an API-key query parameter and this repository has no dedicated HTTP URL-redaction layer. Do not enable verbose HTTP/client debug logs where URLs could be captured until redaction is added.

## Running the system

| Command | Purpose | External use | Sheets writes | Email | Live scraping |
|---|---|---|---:|---:|---:|
| python -m pytest -q | Local regression suite | None; mocks | No | No | No |
| python -m job_intelligence.main --mock-dry-run | Synthetic pipeline/digest smoke test | None | No | No | No |
| python -m job_intelligence.main --dry-run | Real discovery, no Sheets/SMTP | Portals/ATS and enabled Apify/Gemini paths | No | No | Yes |
| python -m job_intelligence.main --test-sheets | Dedicated Sheets integration test | Google Sheets | Test sheet only | No | No |
| python -m job_intelligence.main --test-email | Send configured-recipient test email | Gmail SMTP | No | Yes | No |
| python -m job_intelligence.main --test-ai | Synthetic AI request | Gemini | No | No | No |
| python -m job_intelligence.main --production | Full real workflow | Configured services | Yes | If enabled | Yes |
| python -m job_intelligence | Default invocation | Blocked unless production gate is enabled | No | No | No |

--mock-dry-run is the safe end-to-end check. --dry-run is **not** mock mode: it may access portals and enabled paid actors. Production additionally requires PRODUCTION_ENABLED=true.

## Operations

### Manual CSV imports

The manual importer supports lawful user-supplied/exported data and requires:

~~~csv
title,company,url
~~~

Optional fields are id, location, description, apply_url, employment_type, posted_date, and salary.

~~~csv
title,company,url,location,employment_type,salary
Marketing Analyst,Example Company,https://careers.example.com/jobs/123,India,Full-time,₹10 LPA
~~~

It normalizes into the standard pipeline and does not bypass rules. It is a reusable module, not a main CLI import command. Retain source permission/terms evidence.

### GitHub deployment and scheduling

Keep the GitHub repository private. .github/workflows/daily.yml creates .env from one GitHub Secret, APP_ENV_FILE, installs requirements, then runs production. Never commit .env, credentials, Base64 values, tokens, app passwords, cache data, or sensitive screenshots.

~~~text
Workflow cron: 30 3 * * * UTC
India Standard Time: 09:00 daily (UTC+05:30)
~~~

Create a private repository, add APP_ENV_FILE containing the protected full .env, then use Actions → daily-job-intelligence → Run workflow for a deliberate trigger. To change timing, edit the cron in daily.yml; to disable automatic scheduling, remove/comment the schedule trigger or disable the workflow. workflow_dispatch may remain for manual use.

There is no workflow-level concurrency group, so avoid overlapping manual and scheduled production jobs. GitHub cron may run late.

## Operating safely

### Troubleshooting

| Symptom | Likely cause | Safe action |
|---|---|---|
| py/python3 unavailable | Windows launcher/alias absent | Use python --version and python -m commands. |
| Environment value appears missing | Wrong working directory, misspelled variable, stale terminal | Run from root, compare with .env.example, verify presence without printing secret. |
| Gemini disabled/key missing | Flag false, missing key, old settings process | Verify GEMINI_ENABLED, restart terminal, then deliberately use synthetic test. |
| Portal no data/429/blocking | Site controls, query, geography, rate limit | Reduce scope, wait, use approved ATS/manual data; do not bypass controls. |
| Apify rotates/fails | Quota/auth/temporary error | Inspect account health without exposing tokens; retry only intentionally. |
| Sheets duplicate header error | Headerless/malformed sheet | Use test sheet and current recovery code; never clear production data. |
| Sheets 429 | Per-user/service-account quota or overlap | Wait, avoid concurrent tests; batching/backoff are bounded. |
| Gmail error | Wrong app password/configuration | Use app password and current UTF-8 sender code. |
| Production blocked | Safety gate false | Set PRODUCTION_ENABLED=true only after all checks. |

### Security

- .env, virtual environments, caches, and credentials are ignored by Git; inspect status before pushing from a real clone.
- Rotate a Gmail app password, service-account key, Gemini key, or Apify token immediately if exposed.
- Use distinct test/production Sheets; grant only required service-account access.
- Use GitHub Secrets, not repository variables or committed files.
- Treat terminals and screenshots as sensitive. Avoid verbose Gemini HTTP logs until URL-query redaction exists.

### Limitations

- Public portals can block, rate-limit, return stale/no data, or change without notice.
- Search coverage follows configured roles and boards, not the whole market.
- Apify/Gemini have cost and quota constraints; token rotation is resilience, not a guarantee.
- Company evidence can become incomplete or stale and needs human review.
- AI can be wrong or incomplete; it never replaces policy review.
- No automatic closure/repost lifecycle exists; source statistics are basic.

### Tests and maintenance

Tests use mocks and synthetic records, not live Google, Gmail, Apify, or Gemini calls. Current coverage includes rules, deduplication, AI fallback, UTF-8 email, Sheets header/manual-field/429 handling, and Apify multi-token rotation/failure/concurrency. The local run made while preparing this README was **46 passed in 0.86 seconds**.

Maintain the system by upgrading dependencies in the active virtual environment, running pytest, changing filters/source boards only in .env, maintaining company evidence, retesting an integration after credential changes, reviewing source statistics/System Logs, and rotating credentials periodically.

# Our Implementation Journey

This section combines repository evidence with the recorded setup history. Reported live outcomes are not re-run by this README update.

## Phase 1 — Windows environment setup

Windows PowerShell 5.1 and Python 3.13.12 were validated. py and python3 failed on the recorded computer; python worked. A virtual environment was created, pip upgraded, and dependencies installed with the commands in [Windows installation](#windows-installation).

## Phase 2 — Dependencies

The requirements installation brought in JobSpy, BeautifulSoup4, Apify client, Google Sheets/auth libraries, HTTP client, dotenv, and pytest. Reinstall with python -m pip install -r requirements.txt in the activated environment.

## Phase 3 — Initial validation

Historical validation recorded Python, environment, and dependency checks; an early suite result was **29 passed**. A mock dry-run processed synthetic jobs and generated an email payload without Sheets or SMTP actions. That is historical context: the current local suite result is 46 passing tests.

## Phase 4 — Google Sheets setup

Recorded setup created a Google Cloud project, enabled Sheets API, created/downloaded service-account credentials, shared spreadsheets with that account, configured protected values in .env, and created a separate test spreadsheet. Problems included a missing test ID, a quota error, and a blank-header failure. Configuration and code safeguards were corrected; the reported successful test wrote **two rows** to the test sheet. No ID or credential is included here.

## Phase 5 — Gmail setup

Gmail SMTP, an app password, and a recipient were configured. Missing configuration and an ASCII/Unicode encoding failure occurred. UTF-8 MIME handling was added; a test email was reportedly sent and formatting reviewed.

## Phase 6 — Gemini setup

Gemini configuration added the key/model environment fields and optional enable flag. Initial issues were the disabled flag, a key appearing absent, and configuration propagation. Settings loading was corrected and a synthetic structured-response/summary test was reported successful. A prior concern about API-key query parameters appearing in HTTP logging remains pending because dedicated log redaction is not implemented.

## Phase 7 — Apify

Apify actors, enable flags, inputs, and multi-token support were implemented. The current manager accepts unlimited comma-separated tokens, rotates thread-safely, honors legacy compatibility, quarantines failed tokens for a run, tries alternatives when appropriate, and never intentionally logs a token. Validation is mocked; real actor scraping is not claimed as verified.

## Phase 8 — Job sources

The source families above are implemented. A historical live dry-run encountered no-data responses, HTTP 429/blocking, slow execution, and was manually interrupted. Therefore live scraping reliability remains unresolved.

## Phase 9 — Filtering and verification

The implemented policy accepts qualifying India/eligible-remote target roles, rejects unpaid internships and excessive experience/low explicit pay, and marks unclear salary, experience, location, and company evidence for verification.

## Phase 10 — Mock dry-run

~~~powershell
python -m job_intelligence.main --mock-dry-run
~~~

This confirmed synthetic end-to-end processing and digest creation without live discovery, Sheets, or email. It does not prove credentials, deliverability, quota, or portal availability.

## Phase 11 — Tests and CLI

The command table above distinguishes no-network mock tests from commands that contact providers. Treat --test-sheets, --test-email, --test-ai, --dry-run, and --production as intentional external operations.

## Phase 12 — Current project status

| Area | Status | Evidence | Next step |
|---|---|---|---|
| Local setup/dependencies | Ready | Recorded Windows setup | Keep dependencies current |
| Tests | Passing locally | 46 mocked tests passed | Run before deployment |
| Mock workflow | Ready | Synthetic dry-run succeeded | Use as smoke test |
| Google Sheets | Code ready; reported test success | Safeguards/tests; reported two-row write | Reconfirm only on test sheet |
| Gmail | Code ready; reported test success | UTF-8 regression test | Retest after credential changes |
| Gemini | Optional code ready | Settings/tests; reported synthetic validation | Add HTTP log redaction |
| Apify multi-token | Code ready/mocked | Rotation/failure/concurrency tests | Validate selected actors/costs |
| Live portal scraping | Unresolved | Historical blocking/no-data | Pilot narrow approved sources |
| GitHub deployment/schedule | Workflow exists | daily.yml | Add secrets and validate manually |
| Production operation | Not independently verified here | Safety gates exist | Launch only after checks |

## Phase 13 — Problems and fixes

| Issue | What happened | Resolution | Status |
|---|---|---|---|
| Windows command mismatch | py/python3 absent | Standardized on python | Resolved |
| Missing test Sheet ID | Test had no isolated target | Added test configuration and guard | Code resolved |
| Headerless Sheets tab | Blank duplicate header error | Safe header insertion | Regression-tested |
| Sheets 429 | Per-user read quota issue | Batch reads and bounded backoff | Mitigated; quota remains external |
| Unicode email | ASCII codec rejected Unicode | UTF-8 MIME subject/body | Regression-tested |
| Gemini key missing | Settings did not expose loaded key | Configuration settings fixed | Resolved in code |
| Single Apify token | Low resilience | Dynamic token manager | Regression-tested |
| Portal reliability | Blocks/no-data/slow run | Failures isolated, no bypass added | Operationally unresolved |

## Phase 14 — Completed vs pending

**Confirmed completed:** local setup; core discovery/filtering/verification/deduplication; Sheets safeguards; UTF-8 email; optional Gemini fallback; dynamic Apify manager; mock coverage; and workflow definition.

**Pending or operator-dependent:** stable live source performance; repeated live integration validation; Gemini HTTP URL redaction; GitHub secrets/deployment monitoring/concurrency; richer analytics; and automated repost/closure tracking.

## Roadmap, quick start, and FAQ

### Roadmap

| Completed | Recommended next | Pending feature |
|---|---|---|
| Core pipeline, safeguards, mock tests | Add HTTP log redaction and workflow concurrency | Automated closure/repost detection |
| Sheets quota/header protection | Pilot narrow compliant sources | Wider native ATS coverage |
| UTF-8 email and AI fallback | Add monitoring/alerting | Analytics beyond source counts |

### Quick-start checklist

- [ ] Confirm python --version; create and activate .venv.
- [ ] Install requirements.txt; copy .env.example to private .env.
- [ ] Run python -m pytest -q.
- [ ] Run python -m job_intelligence.main --mock-dry-run.
- [ ] Configure only needed integrations.
- [ ] Create a separate test Sheet before --test-sheets.
- [ ] Intentionally test email/AI only when external calls are acceptable.
- [ ] Review costs, permissions, and source behavior.
- [ ] Enable PRODUCTION_ENABLED=true only when ready; then deploy secrets/workflow.

### FAQ

**Do I enter company names?** No. Discovery starts with role queries and configured boards; company data is used later for evidence/classification.

**Can I add many Apify accounts?** Yes. Add any number of comma-separated tokens to APIFY_TOKENS; it takes priority over APIFY_TOKEN.

**Is Gemini required?** No. It is optional enrichment; core collection and policy checks work with it disabled.

**Is --dry-run safe?** It does not write Sheets or send email, but it performs live discovery and can use enabled paid actors. Use --mock-dry-run for no-network validation.

**Will Sheets erase my notes?** The code preserves user-maintained fields and historical records, but always test with a separate spreadsheet first.

For deeper details, see docs/ARCHITECTURE.md, CONFIGURATION.md, FILTERING_LOGIC.md, CONNECTORS.md, TESTING.md, TROUBLESHOOTING.md, SHEETS_QUOTA_ANALYSIS.md, and LIVE_INTEGRATION_TESTING.md. This README is the single technical entry point and consolidated project record.
