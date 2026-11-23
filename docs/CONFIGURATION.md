# Configuration

Create exactly one file: copy `.env.example` to root `.env`. It contains all credentials, limits, board targets and feature switches. Google service-account JSON is base64 encoded in `GOOGLE_SERVICE_ACCOUNT_JSON_BASE64`; no service-account file is read. `APIFY_ENABLE_*` switches default to false and this release does not call any paid actor.

## Apify token rotation

Set `APIFY_TOKENS` to a comma-separated list of one or more tokens. Whitespace and empty items are ignored; there is no fixed limit. This setting takes priority over legacy `APIFY_TOKEN`, which remains supported as a one-token fallback. Tokens are never logged. The connector round-robins tokens, marks tokens unavailable for the current run after rate-limit, quota, authentication, timeout, or temporary-server failures, and tries another configured token at most once per actor request.

Validate configuration locally with `python -m job_intelligence.main --dry-run`. A missing Sheets or Gmail credential makes that output mode useful and skips external writes.
