# Phase 5 audit

Security checks confirmed one root `.env`, `.env`/ZIP/JSON credential exclusions, one workflow `APP_ENV_FILE`, and no source-controlled key values. Phase 5 adds an explicit Gemini synthetic-test command and a dual production gate: scheduled/local production needs both `PRODUCTION_ENABLED=true` in the single `.env` and `--production`.

Actual validation: 29 automated tests passed; mock end-to-end pipeline passed. Gemini test was safely not run because Gemini is currently disabled. Google Sheets and Gmail live tests were not run because no external user data or mail was modified in this development session.

An explicit `--test-sheets` command confirmed that no `TEST_GOOGLE_SHEET_ID` is configured, so no Sheets connection or write was attempted. An explicit `--test-email` command confirmed that Gmail credentials/recipient are not configured, so no message was sent. A read-only `Business Analyst` pilot capped at two results per source returned two parsed Naukri jobs; Google Jobs returned no job data and was reported as one isolated connector error. No production write, SMTP delivery, Gemini request, or Apify run occurred.

## Sheets header recovery

The Sheets writer now validates every worksheet header before `get_all_records()` is called. Empty sheets receive their expected header. A non-empty headerless or malformed sheet receives a canonical header inserted at row 1, shifting existing values down without clearing or overwriting them. Repaired category/statistics views are not cleared in that run, protecting unrecognised legacy/user data. Regression coverage uses mocks only.

## Sheets read-quota optimisation

The integration previously issued individual reads for every tab on each of two test updates. It now fetches tab values through one batch read per update, reuses the same spreadsheet object through the test, and retries bounded 429 bursts with exponential backoff. See [Sheets quota analysis](SHEETS_QUOTA_ANALYSIS.md).
