# Driver Leads

Two ways to get CDL-A OTR drivers, no paid tools:

1. **Outbound list** (`scripts/`): new owner-operators from the public FMCSA registry, with phone and email, refreshed daily.
2. **Inbound applications** (`web/`, `apps-script/`): a form where job-seeking drivers apply, written straight into a Google Sheet.

## Step 1: Get the daily lead list

```bash
python scripts/fetch_fmcsa_leads.py --days 30    # last 30 days (~2,800 leads)
python scripts/fetch_fmcsa_leads.py --days 2     # yesterday + today
```

Output goes to `data/` (git-ignored: it holds personal contact data). Import the CSV into Google Sheets with File > Import.

Columns: owner_operator, company, phone, email, city, state, zip, add_date, dot_number, mc_prefix, mc_number, org_type, days_since_registered.

Source and filter: FMCSA Company Census (data.transportation.gov), active, 1 truck, interstate for-hire 100+ miles, general freight, US address. Newly registered carriers are the ones looking for loads and drivers.

## Step 2: Make it run every day

`.github/workflows/daily-leads.yml` runs the script every day and attaches the CSV to the run (Actions tab > run > Artifacts, kept 14 days). You can also run it by hand with "Run workflow".

## Step 3: Collect applications (inbound)

1. Create a Google Sheet for applications.
2. In it: Extensions > Apps Script, paste `apps-script/Code.gs`.
3. Deploy > New deployment > Web app. Execute as: Me. Access: Anyone. Copy the URL.
4. In `web/apply.html` set `FORM_ENDPOINT` to that URL.
5. Host `web/` (GitHub Pages: Settings > Pages > deploy from branch, folder `/web` via a `main` branch, or Netlify drop).

## Step 4: Get traffic

Fill in pay and terms in `docs/ad-copy.md` and post only where the group or board allows job ads. Put the form URL in every post.

## Rules

- Do not scrape LinkedIn, Facebook or resume sites; it breaks their terms and can get accounts banned.
- Only text or auto-dial people who ticked the consent box on the form (US TCPA). Cold calls to registry leads should be made by hand.
- Never commit lead CSVs.
