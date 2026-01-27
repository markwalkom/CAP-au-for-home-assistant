<!-- omit from toc -->
# Known Issues & Remediations

This document tracks known issues, root causes, and practical remediations for CAP-au-for-home-assistant.

## OneDrive sync path with spaces causes robocopy failure

- Symptom: robocopy reports `Invalid Parameter #3 : "-"` and truncates destination to `C:\Users\pc\OneDrive`.
- Root cause: Arguments with spaces (e.g., `OneDrive - Crispy Kangaroo`) were not quoted as a single command-line string.
- Fix: [scripts/sync_to_onedrive.ps1](scripts/sync_to_onedrive.ps1) now passes a single, properly quoted argument string to robocopy via `Start-Process`.
- Validation:
  - `pwsh scripts/sync_to_onedrive.ps1 -DryRun` completes without robocopy parse errors.

## Feed country/language enrichment

- Symptom: New feeds showed `country: Unknown`, `countryCode: ""`, `language: "en"` even when identifiers contained location/language hints.
- Root cause: Initial ingestion did not derive ISO codes from URL identifiers or table columns; country inheritance for blank cells was not applied.
- Fix: [scripts/update_feed_catalog.py](scripts/update_feed_catalog.py) now:
  - Parses table rows with country-blank inheritance
  - Derives `(countryCode, language)` from URL identifiers like `aw-gov-nl`
  - Falls back to table language and country name mapping when available
- Validation:
  - `python scripts/update_feed_catalog.py` updates `data/feed_catalog.json` with populated fields.

## Documentation lint

- Symptom: markdownlint errors (headings and list spacing) on contribution templates and docs.
- Fix: Adjusted [HACS-DEFAULT-PR.md](HACS-DEFAULT-PR.md); pending full repo sweep.
- Next: Run a repo-wide lint pass and fix remaining issues.

## Disclaimer acceptance and tamper detection

- Symptom: Integration remains disabled with a Repairs issue indicating disclaimer acceptance is required.
- Root cause: Disclaimer was not accepted, or the packaged disclaimer text changed, or the stored acceptance record was modified (hash/signature mismatch).
- Fix: Reconfigure the integration and accept the disclaimer. Stored record includes timestamp, user ID, text hash, and a signed signature; any mismatch disables the integration until reaccepted.
- Validation:
  - Setup proceeds after acceptance; Repairs issue disappears.

## Feed disabled due to repeated failures

- Symptom: A feed entity shows unavailable; a Repairs issue indicates the feed was disabled after repeated failures.
- Root cause: Upstream endpoint outages or parsing errors caused 5 consecutive fetch failures.
- Fix: Resolve the upstream issue (endpoint or network), then use **Options → Reset failures for feed** to re‑enable querying.
- Validation:
  - After reset and upstream recovery, feed resumes querying and entity becomes available.
