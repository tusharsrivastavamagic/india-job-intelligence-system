# Production deployment

After reviewing dry runs and test integrations, set `PRODUCTION_ENABLED=true` in the existing root `.env`, update the single GitHub `APP_ENV_FILE` secret with the complete file, and use `python -m job_intelligence.main --production`. GitHub Actions already supplies `--production`; the configuration gate remains authoritative. Keep it false until you intend daily writes and delivery.
