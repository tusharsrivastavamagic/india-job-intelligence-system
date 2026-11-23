from job_intelligence.models import Job
from job_intelligence.intelligence import classify_function,remote_eligibility
def test_remote_india(): assert remote_eligibility(Job("1","Analyst","Co","x","u",location="Remote, India"))=="Remote eligible in India"
def test_remote_foreign_requires_review(): assert remote_eligibility(Job("1","Analyst","Co","x","u",location="Remote",description="US work authorization required"))=="Location Verification Required"
def test_function_uses_description(): assert "Finance" in classify_function(Job("1","Associate","Co","x","u",description="financial analysis and corporate finance"))
