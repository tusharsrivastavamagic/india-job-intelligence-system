from job_intelligence.connectors.portals import fetch_roles

def test_unsupported_portal_is_reported():
    jobs, errors = fetch_roles([], ["unsupported"], 1, False)
    assert jobs == [] and "Unsupported portal" in errors[0]
