# Connectors

| Connector | State | Retrieval | Pagination |
| Naukri, LinkedIn, Indeed, Google Jobs, Glassdoor | Implemented role-first | MIT `python-jobspy`; query + location `India` | provider-dependent |
|---|---|---|---|
| Greenhouse | Implemented | public Board API with descriptions | API returns full board |
| Lever | Implemented | public postings JSON | API returns full board |
| Ashby | Implemented | public GraphQL board endpoint | API returns board jobs |
| SmartRecruiters | Implemented | public postings API | offset/limit loop |
| Workable | Implemented | public widget API | API returns board jobs |
| Recruitee | Implemented | public offers API | API returns board jobs |
| Breezy HR | Implemented | public JSON board | API returns board jobs |
| Personio | Implemented | public XML feed | feed returns board jobs |
| Workday | Implemented | public CXS endpoint from complete board URL | fixed 20-row pages |
| Oracle, SAP, Teamtailor, Jobvite, iCIMS, Zoho | Not implemented | require separate adapters | n/a |
| Apify Actors | Implemented but disabled by default | runs the six configured actor IDs only with an explicit flag/token/input JSON | `APIFY_MAX_ITEMS_PER_ACTOR` hard result cap |

Role-first use needs no company list: set `ROLE_QUERIES` and `PORTAL_SOURCES` in the one root `.env`. Default queries target management roles and are searched with location `India`. `TARGET_BOARDS_JSON` is optional for employer monitoring, for example: `[ {"ats":"greenhouse","company":"Example","board":"example"} ]`. Only public listings are requested. Portal availability and terms can change; each portal error is isolated and logged.

For Workday, `board` must be the complete `https://tenant.wdN.myworkdayjobs.com/SITE` URL. For Apify, add reviewed actor-specific input objects such as `APIFY_ACTOR_INPUTS_JSON={"naukri":{"searchQueries":["Business Analyst"]}}`; inputs are intentionally not guessed because the actors' schemas can change and some may incur charges.
