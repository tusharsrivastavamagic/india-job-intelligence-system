from datetime import date
from job_intelligence.company import verify
from job_intelligence.models import Job

def job(): return Job("1","Business Analyst","Acme","test","https://x",location="India")
def test_eligible_startup():
    result=verify(job(),{"Acme":{"classification":"Startup","founding_year":date.today().year-5,"employee_count":90,"source":"https://example.test"}})
    assert result.startup_status=="Eligible"
def test_failing_startup_excluded():
    result=verify(job(),{"Acme":{"classification":"Startup","founding_year":date.today().year-2,"employee_count":90,"source":"https://example.test"}})
    assert result.eligibility=="Excluded Jobs"
def test_small_established_company_not_excluded():
    result=verify(job(),{"Acme":{"classification":"Established company","founding_year":date.today().year,"employee_count":20,"source":"https://example.test"}})
    assert result.startup_status=="Not a startup"
