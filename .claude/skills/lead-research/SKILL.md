---
name: lead-research
description: Find and qualify B2B leads for our own outbound. Takes an ICP (ideal customer profile), finds matching companies and decision makers, scores them, and outputs a CSV for the CRM. Use when asked to find leads, prospects, or accounts to contact.
---

# Lead research

We use this skill to find leads for our own sales. We do not resell the data.

## Inputs (ask the user if missing)

- **ICP:** industry, company size, location, job titles, and any must-have signals (hiring, recent funding, tech stack).
- **Count:** how many leads to return (default 25).
- **Output path:** where to save the CSV (default `leads/<date>-<segment>.csv`).

Do not start a paid or credit-consuming search until the user confirms the ICP and count.

## Steps

1. **Define the ICP** in one short paragraph and confirm it with the user.
2. **Find companies.** Use the search tools available in this session, in this order:
   - Gojiberry (`search_companies`, `search_leads`) if connected. Searches are free. Revealing leads costs credits, so confirm the count first.
   - Apify Google Search Scraper or Brave Search for public company lists and job boards.
3. **Find decision makers** at each company: job titles from the ICP, plus LinkedIn URL and company website.
4. **Qualify.** Score each lead 0–3 on: ICP fit, a buying signal (hiring, funding, new role, recent post), and reachability (a LinkedIn URL or a verified email). Drop leads scoring 0 or 1 on fit.
5. **Output a CSV** with these columns:
   `company, website, industry, size, location, first_name, last_name, title, linkedin_url, signal, fit_score, signal_score, reach_score, source, found_at`
6. **Report** the count, the score distribution, and any gaps (for example, titles with no matches).

## Rules

- Use only public data. Do not scrape pages behind a login.
- Respect LinkedIn limits: do not automate connection requests or messages from this skill. Outreach is a separate step, done by a person or a tool the user has approved.
- Never invent emails, phone numbers, or titles. If a field is unknown, leave it empty.
- Deduplicate by LinkedIn URL, then by company plus name.
