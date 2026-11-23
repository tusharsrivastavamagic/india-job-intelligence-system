# Phase 2B audit

The latest Phase 2 ZIP exists and was reconciled without reading or altering `.env`; it is a packaged snapshot of the established Phase 2 implementation. Phase 2B preserves the public connector set and adds compliant manual CSV ingestion for IIMJobs/Hirist exports or user-supplied public job URLs. No CAPTCHA, login wall, private endpoint, or bot protection is bypassed.

Implemented and tested: required-versus-preferred experience context, monthly full-time INR normalisation, weekly internship stipend normalisation, and manual CSV validation. Native IIMJobs/Hirist automation remains unavailable without a documented permitted API.
