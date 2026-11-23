# Google Sheets quota analysis

`--test-sheets` previously ran `update()` twice. Each update read all 14 tabs through `get_all_values()` and then read **All Jobs** again through `get_all_records()`: roughly 15 values reads per update, plus spreadsheet metadata access. Two updates could therefore issue about 30 values reads in a short burst. The relevant quota is the 60 read requests/minute/**per user** limit, not the 300/minute project limit shown in the dashboard.

Authentication is created from `GOOGLE_SERVICE_ACCOUNT_JSON_BASE64`; no `quotaUser` override is sent. Requests are therefore normally attributed to that service-account principal. Other scripts using the same service account can share that per-user limit.

The writer now uses one `values.batchGet` request for the initial values of all tabs per update, avoids a second All Jobs read by reconstructing records from that batch data, and reuses one `Spreadsheet` client during `--test-sheets`. Quota responses receive bounded exponential delays of 1, 2, 4, and 8 seconds before surfacing the error. No quota setting was changed.
