import pytest
from job_intelligence.models import Job
from job_intelligence.rules import classify
def make(description, salary="", title="Business Analyst", location="India"):
    return classify(Job("1",title,"Acme","test","https://x",location,description,salary_text=salary))
@pytest.mark.parametrize("description,expected",[("Fresher role in India","Eligible"),("0-3 years experience India","Eligible"),("2-4 years experience India","Excluded Jobs"),("3-5 years experience India","Excluded Jobs")])
def test_experience(description,expected): assert make(description).eligibility == expected or (expected=="Eligible" and make(description).experience_status=="Eligible")
@pytest.mark.parametrize("description,salary,expected",[("0-2 years India","₹7 LPA","Excluded Jobs"),("0-2 years India","₹8 LPA","Strong Matches"),("0-2 years India","₹6-10 LPA","Salary Verification Required"),("intern 0-1 years India","₹8,000/month","Excluded Jobs"),("intern 0-1 years India","₹9,999/month","Excluded Jobs"),("intern 0-1 years India","₹10,000/month","Paid Internships"),("intern 0-1 years India","₹15,000/month","Paid Internships"),("unpaid intern 0-1 years India","","Excluded Jobs"),("intern 0-1 years India","₹8,000-12,000/month","Salary Verification Required")])
def test_pay(description,salary,expected): assert make(description,salary).eligibility==expected
