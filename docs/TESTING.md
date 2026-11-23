# Testing

Run `pytest -q`. Tests use no network, Google account, Gmail account, or Apify credit. They cover required experience and published salary/stipend threshold examples, company-policy enforcement, cross-source URL and description-similarity deduplication, remote India eligibility, function classification, and career-page ATS pattern detection. Google Sheets and email are integration boundaries and require configured credentials for a manual operational check.

For a safe end-to-end smoke test, run `python -m job_intelligence.main --mock-dry-run`. It uses local fixture records and generates an email MIME payload without contacting a portal, Google Sheets, Gmail, or Apify.
