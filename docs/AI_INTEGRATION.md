# Gemini AI integration

Gemini is optional and disabled by default. The default model is `gemini-3.1-flash-lite`; current free-tier terms and availability must be reviewed in Google AI Studio before enabling. No Google Search grounding is used. Requests carry only public job data and never configuration secrets, notes, contacts, resumes, or application data.

Set `GEMINI_ENABLED=true` plus `GEMINI_API_KEY` in the existing single root `.env`. Limits cap jobs, requests, and output tokens. JSON responses are validated, cached by listing content hash, and rendered through deterministic email HTML. Gemini can describe a deterministic classification but cannot alter eligibility, compensation, experience, URL, or company verification. Failures return the standard non-AI email.
