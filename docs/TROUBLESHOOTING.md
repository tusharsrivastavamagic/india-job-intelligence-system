# Troubleshooting

If a source fails, inspect the terminal summary and System Logs tab; the remaining sources continue. Check board slug, public board availability, and `TARGET_BOARDS_JSON` validity. If Sheets is skipped, populate both `GOOGLE_SHEET_ID` and base64 service-account configuration and share the spreadsheet with the service account. Gmail requires a Google App Password, not the normal account password. Do not paste secret values into issue reports or logs.
