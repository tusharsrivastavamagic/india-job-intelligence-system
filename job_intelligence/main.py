from __future__ import annotations
import argparse, asyncio, logging
from .config import load_settings
from .connectors.ats import fetch_all
from .connectors.portals import fetch_roles
from .connectors.apify import fetch_apify
from .company import verify
from .intelligence import classify_function, remote_eligibility
from .dedupe import deduplicate
from .rules import classify
from .sheets import update
from .email_digest import send
from .email_digest import build_message
from .email_digest import send_test
from .mock_data import jobs as mock_jobs
from .live_tests import test_sheets
from .gemini import test_ai
def run(dry_run=False, mock_dry_run=False, test_email=False, test_sheets=False, ai_test=False, production=False):
    settings=load_settings(); logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(message)s")
    if test_email:
        try: send_test(settings); print("Test email sent to configured recipient only.")
        except Exception as exc: print(f"Test email not completed: {exc}")
        return
    if test_sheets:
        try: print(f"Test spreadsheet result: {test_sheets_fn(settings)}")
        except Exception as exc: print(f"Test spreadsheet not completed: {exc}")
        return
    if ai_test:
        try: print(f"Gemini synthetic test result: {test_ai(settings)}")
        except Exception as exc: print(f"Gemini test not completed: {exc}")
        return
    if not (dry_run or mock_dry_run) and not (production and settings.production_enabled):
        print("Production run blocked. Use --dry-run, or explicitly set PRODUCTION_ENABLED=true and pass --production."); return
    if mock_dry_run: jobs,errors=mock_jobs(),[]
    else:
        portal_jobs, errors=fetch_roles(settings.role_queries,settings.portal_sources,settings.portal_results_per_query,settings.portal_fetch_descriptions)
        apify_jobs, apify_errors=fetch_apify(settings); board_jobs, board_errors=asyncio.run(fetch_all(settings.boards, settings.timeout, settings.max_connector_jobs)); jobs=portal_jobs+apify_jobs+board_jobs; errors.extend(apify_errors); errors.extend(board_errors)
    jobs=[verify(classify(j,settings.min_ctc_lpa,settings.min_stipend,settings.max_experience),settings.company_evidence) for j in deduplicate(jobs)]
    for job in jobs:
        job.raw["function_classification"]=classify_function(job)
        job.raw["india_remote_eligibility"]=remote_eligibility(job)
        if job.raw["india_remote_eligibility"]=="Location Verification Required" and job.eligibility!="Excluded Jobs": job.eligibility="Location Verification Required"
    if dry_run or mock_dry_run:
        print(f"Fetched {len(jobs)} unique jobs; connector errors: {len(errors)}")
        for j in jobs: print(f"{j.eligibility}: {j.title} — {j.company}")
        if mock_dry_run: print(f"Generated email payload: {len(build_message(settings,jobs,errors).as_string())} bytes; no Sheets or SMTP calls made.")
        return
    new_ids=update(settings,jobs,errors); send(settings,[j for j in jobs if j.internal_id in new_ids]); print(f"Completed: {len(jobs)} jobs; {len(new_ids)} new jobs; {len(errors)} source failures.")
test_sheets_fn=test_sheets
if __name__ == "__main__":
    parser=argparse.ArgumentParser(); parser.add_argument("--dry-run",action="store_true"); parser.add_argument("--mock-dry-run",action="store_true"); parser.add_argument("--test-email",action="store_true"); parser.add_argument("--test-sheets",action="store_true"); parser.add_argument("--test-ai",action="store_true"); parser.add_argument("--production",action="store_true"); args=parser.parse_args(); run(args.dry_run,args.mock_dry_run,args.test_email,args.test_sheets,args.test_ai,args.production)
