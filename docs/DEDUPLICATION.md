# Deduplication and historical handling

Primary matching uses a stable hash of direct application URL/job URL. Source URLs are merged into one master record. A conservative secondary merge requires the same company, title, and location plus at least 90% Jaccard overlap of description tokens; it avoids merging distinct openings with similar titles. First Seen and Last Seen dates are retained in Sheets.

The system does not mark a job closed solely because it is absent from a portal result page. Closure/repost detection requires source-specific reliable evidence and is not currently claimed as implemented.
