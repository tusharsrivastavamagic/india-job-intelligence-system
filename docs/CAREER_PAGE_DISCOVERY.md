# Career-page discovery

`job_intelligence.career_discovery.discover()` is an opt-in, low-rate detector for a career URL you already know is official. It follows redirects once, identifies supported ATS URL patterns, and returns a verified board candidate for manual review before it is added to `TARGET_BOARDS_JSON`. It does not guess employer URLs or crawl the web at scale.

This is deliberately conservative: a detected pattern is useful evidence, not permission to invent a board slug. Companies whose pages use an unsupported/custom ATS remain manual configuration candidates.
