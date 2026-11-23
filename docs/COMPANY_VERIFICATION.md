# Company verification

Manual evidence is supplied in `COMPANY_EVIDENCE_JSON` as a company-keyed object containing classification, founding year, employee count, and an evidence URL. The application calculates age on the run date. Startups require both age ≥5 years and employees ≥90; missing evidence routes jobs to **Company Verification Required** and failed startups are excluded. Non-startup classifications have no age/size threshold.

No paid company-data provider is required or called. This avoids fabricated company facts; automatic public-source collection remains a future integration because evidence quality must be reviewed per source.
