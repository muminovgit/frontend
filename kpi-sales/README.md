# KPI.com Uzbekistan lead engine

Pipeline: lead CSV (orginfo/stat.uz/2GIS/Gojiberry exports) -> dedupe by STIR -> sector + score -> KPI.com import CSV -> Eskiz SMS (dry-run by default).

    python3 cli.py data/sample_leads.csv          # report + dry-run SMS
    ESKIZ_EMAIL=.. ESKIZ_PASSWORD=.. python3 cli.py leads.csv --send

Rules baked in: B2B company mobiles only, opt-out list (`data/optout.txt`), phone dedupe, score threshold, STOP text.
Eskiz needs a registered sender name and moderator-approved template before live sending.

## Data sourcing note
Goldenpages.uz and top.uz mask phone numbers behind a "show" control. Do not automate around it. Take company name+website from the listing, then read the phone from the company own site, or buy/export data legitimately.

## Next steps
1. Source adapters -> real leads (needs working Gojiberry key or approved scrape/export of public registries).
2. KPI.com lead import: confirm API/CSV import endpoint with KPI support, then add `kpi_import.push()`.
3. Sector order for launch: manufacturing -> security -> retail -> call centers -> construction.
4. Channel mix: SMS + Telegram + call; SMS alone to cold lists converts poorly, and consent/ad-law rules apply.
