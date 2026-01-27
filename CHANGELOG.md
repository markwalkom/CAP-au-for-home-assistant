# Changelog

## v0.1.0 — First public scaffold

## 2026-01-27 — Disclaimer gate, Repairs, feed fail-safes

- Added mandatory legal disclaimer acceptance to Config Flow with scrollable text and link.
- Persist acceptance with `accepted_at_iso`, `user_id`, SHA‑256 of disclaimer, and a signed signature to detect tampering.
- Enforce reacceptance if the disclaimer text changes or stored record is altered; integration remains disabled and raises a Repairs issue.
- Implemented per‑feed failure tracking; after 5 consecutive failures, a feed is disabled, entity marked unavailable, and a Repairs issue is raised with guidance to reset via Options.
- Added Repairs message translations (en, en‑AU, en‑GB).
- Enhanced catalogue normalisation and directory formatting; eliminated remaining “Unknown” countries (e.g., Kosovo mapping).
