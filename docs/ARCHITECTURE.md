# Architecture

`connectors → normalisation → deduplication → deterministic eligibility → scoring → Google Sheets → email`.

Each board executes independently with `asyncio.gather(return_exceptions=True)`; one failed source is logged and never stops the others. The persistent system of record is the **All Jobs** Google Sheet. The integration only writes owned fields and preserves application status, notes, saved status, application date and personal rating.

Public HTTP adapters currently implement Greenhouse, Lever, Ashby, and SmartRecruiters. The connector boundary makes further ATS adapters independent additions. Company startup verification is deliberately a review queue until credible source data is connected; it never assumes that a small company is a startup.
