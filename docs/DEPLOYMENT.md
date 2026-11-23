# Deployment

GitHub Actions runs `30 3 * * *` (09:00 IST) and also offers **Run workflow**. Add one repository secret named `APP_ENV_FILE` whose complete value is the local root `.env`; the workflow recreates it without printing it. Share the target spreadsheet with the service account email embedded in the base64 JSON. The workflow installs Python dependencies, collects boards, updates Sheets, then sends Gmail SMTP digest.

## Safe live validation

Create a separate Google spreadsheet, share it with the service-account email, and add its ID as `TEST_GOOGLE_SHEET_ID` in the existing root `.env` (never replace `GOOGLE_SHEET_ID`). Then explicitly run `python -m job_intelligence.main --test-sheets`. The command refuses to run if the test ID matches the production ID. Send a labelled SMTP check only with `python -m job_intelligence.main --test-email`. Use `--dry-run` for live retrieval without writes and `--mock-dry-run` for a network-free end-to-end test.

No Apify actor is called by this release. Do not enable a paid actor until an adapter and its input/output contract are reviewed.
