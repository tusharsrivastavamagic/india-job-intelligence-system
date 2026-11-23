import asyncio
from job_intelligence.career_discovery import PATTERNS
def test_public_ats_patterns_exist():
    assert "greenhouse" in PATTERNS and "workday" in PATTERNS
