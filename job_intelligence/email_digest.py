from __future__ import annotations
import smtplib
from collections import Counter
from email.mime.text import MIMEText
from email.header import Header
from .models import Job
from .analytics import summary
from .gemini import enrich
def build_message(settings, jobs:list[Job], errors:list[str]=[], subject="Daily India job intelligence", test_label=False) -> MIMEText:
    ai,ai_errors=enrich(settings,jobs); report=summary(jobs,errors+ai_errors); counts=Counter(j.eligibility for j in jobs)
    cards="".join(f"<li><b>{j.title}</b> — {j.company} ({j.company_classification}) | {j.location} | {j.employment_type} | {j.experience_text or 'verify experience'} | {j.ctc_lpa or j.monthly_stipend or 'pay undisclosed'} | score {j.match_score}<br><a href='{j.direct_apply_url or j.job_url}'>Apply</a> — {j.match_explanation}{('<br>'+ai[j.internal_id]['summary']) if j.internal_id in ai else ''}</li>" for j in sorted(jobs,key=lambda x:x.match_score,reverse=True)[:30])
    skills=sorted({skill for item in ai.values() for skill in item['skills']})
    body=f"<h2>India Job Intelligence daily digest</h2>{'<p><b>TEST EMAIL — no production jobs were sent.</b></p>' if test_label else ''}<p>New jobs: {len(jobs)} | Connector errors: {report['connector_errors']}</p><h3>Categories</h3><ul>{''.join(f'<li>{k}: {v}</li>' for k,v in counts.items())}</ul><h3>Sources</h3><ul>{''.join(f'<li>{k}: {v}</li>' for k,v in report['by_source'].items())}</ul>{('<h3>Skills Employers Are Looking For Today</h3><p>'+ ', '.join(skills)+'</p>') if skills else ''}<ol>{cards}</ol>"
    msg=MIMEText(body,"html","utf-8"); msg["Subject"]=Header(subject,"utf-8"); msg["From"]=settings.gmail_address; msg["To"]=settings.email_recipient; return msg
def send(settings, jobs: list[Job]) -> None:
    if not (settings.send_email and settings.gmail_address and settings.gmail_password and settings.email_recipient): return
    msg=build_message(settings,jobs)
    with smtplib.SMTP_SSL("smtp.gmail.com",465) as s: s.login(settings.gmail_address,settings.gmail_password); s.send_message(msg)
def send_test(settings) -> None:
    if not (settings.gmail_address and settings.gmail_password and settings.email_recipient): raise ValueError("Gmail test requires GMAIL_ADDRESS, GMAIL_APP_PASSWORD, and EMAIL_RECIPIENT")
    from .mock_data import jobs
    msg=build_message(settings,jobs(),subject="[TEST] Job Intelligence System",test_label=True)
    with smtplib.SMTP_SSL("smtp.gmail.com",465) as s: s.login(settings.gmail_address,settings.gmail_password); s.send_message(msg)
