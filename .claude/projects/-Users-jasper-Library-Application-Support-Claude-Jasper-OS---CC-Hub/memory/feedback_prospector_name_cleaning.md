---
name: Prospector name cleaning failures
description: Step 6B personal business detection must check both first AND last name, plus strip personal suffixes. Lemlist update requires campaign-specific endpoint.
type: feedback
---

Step 6B personal business detection MUST check both `first_name` AND `last_name` against the company name, not just first_name. Law firms almost always use the last name ("Gans Law", "Minick Law", "Carr Law Firm"), so checking only first_name missed hundreds of leads.

Personal name suffixes (Esq., Jr., Sr., III, PhD, J.D.) must be stripped from first/last names BEFORE any company-name matching or Lemlist/Instantly loading. Apollo data includes these and they pollute outreach if left in.

**Why:** Criminal defense campaign shipped with 567+ leads where company names contained the person's name but weren't replaced with "your practice", and multiple leads had "Esq" as their entire last name. Required a 313-lead batch fix on live data.

**How to apply:** Every prospector run must execute Step 6B fully. After cleaning, verify: (1) no personal suffixes remain in names, (2) all name-in-company leads have "your practice" as company, (3) all legal suffixes stripped from company names. When scanning for issues, always pull LIVE data from Lemlist rather than relying on source files in .tmp/ which may not cover all leads.