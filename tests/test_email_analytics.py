from types import SimpleNamespace
from job_intelligence.models import Job
from job_intelligence.email_digest import build_message
def test_digest_includes_card():
 s=SimpleNamespace(gmail_address="a@b.test",email_recipient="c@d.test")
 msg=build_message(s,[Job("1","Business Analyst","Co","naukri","https://x",location="India",direct_apply_url="https://x")])
 body=msg.get_payload(decode=True).decode()
 assert "Business Analyst" in body and "Sources" in body
def test_unicode_email_is_utf8_serializable():
 s=SimpleNamespace(gmail_address="a@b.test",email_recipient="c@d.test")
 job=Job("1","Marketing Analyst — APAC","Co ₹","naukri","https://x",location="Pune, India",salary_text="₹10 LPA",direct_apply_url="https://x")
 msg=build_message(s,[job],subject="Daily digest — ₹ opportunities")
 assert msg.get_content_charset()=="utf-8"
 assert "₹" in msg.get_payload(decode=True).decode("utf-8")
 assert b"Content-Type: text/html; charset=\"utf-8\"" in msg.as_bytes()
 assert b"=?utf-8?" in msg.as_bytes().lower()
