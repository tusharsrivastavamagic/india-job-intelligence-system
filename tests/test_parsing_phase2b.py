from job_intelligence.models import Job
from job_intelligence.parsing import parse_compensation,parse_experience
def test_preferred_experience_does_not_exclude():
 j=Job("1","Analyst","Co","x","u",description="0-2 years required; preferred 3-5 years"); parse_experience(j); assert j.experience_status=="Eligible"
def test_monthly_full_time_normalizes():
 j=Job("1","Analyst","Co","x","u",salary_text="₹ 100,000/month"); parse_compensation(j); assert j.ctc_lpa is None and j.annualised_fixed_salary==1200000 and j.salary_status=="Salary Verification Required"
def test_weekly_stipend_normalizes():
 j=Job("1","Intern","Co","x","u",salary_text="₹ 3,000 weekly"); parse_compensation(j); assert j.monthly_stipend==13000
