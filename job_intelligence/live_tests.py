"""Explicit live test helpers. Never use production Sheet ID."""
from dataclasses import replace
from .mock_data import jobs
from .sheets import update,_client
def test_sheets(settings):
    if not settings.test_sheet_id: raise ValueError("Set TEST_GOOGLE_SHEET_ID to a separate test spreadsheet; production ID is refused.")
    if settings.test_sheet_id==settings.sheet_id: raise ValueError("TEST_GOOGLE_SHEET_ID must not equal GOOGLE_SHEET_ID.")
    safe=replace(settings,sheet_id=settings.test_sheet_id,send_email=False)
    records=jobs(); records[0].internal_id="live-test-job-1"; records[1].internal_id="live-test-job-2"
    book=_client(safe)
    new=update(safe,records,[],book=book); update(safe,records,[],book=book)
    return {"sheet_id":settings.test_sheet_id,"inserted":len(new),"written":len(records)}
