<!-- omit from toc -->
# Contributing

Thank you for contributing to CAP-au-for-home-assistant. This project welcomes improvements to documentation, ingestion tooling, and the Home Assistant integration. Please keep changes small, well-documented, and accessible.

## Internationalisation (i18n) and Localisation (l10n)

Provide broader language support by adding and maintaining translations for all user-visible strings.

- Files and locations:
  - Source keys: custom_components/cap_alerts/strings.json
  - Locale files: custom_components/cap_alerts/translations/
  - Existing locales: en, en-AU, en-GB

- Locale codes:
  - Use IETF BCP‑47 style (e.g., en-AU, pt-BR, zh-Hans, zh-Hant).
  - Prefer widely used variants where applicable.

- Keys and placeholders:
  - Keep keys identical across all locales.
  - Preserve placeholders such as {link}, {slug}, {url} exactly.
  - Ensure descriptions remain concise, inclusive, and screen‑reader friendly.

- Fallbacks and coverage:
  - Ensure the base `en` locale remains complete.
  - New locales should cover: config flow, options, and Repairs issues.
  - Avoid introducing different punctuation or extra whitespace that may break rendering.

- Testing translations:
  - In Home Assistant, change language in profile settings and review the integration UI.
  - Verify Config Flow, Options, and any Repairs issues render correctly.
  - Confirm no missing‑key warnings appear in logs.

- Submission checklist:
  - [ ] Added/updated the appropriate locale file(s) under translations/.
  - [ ] Verified placeholders and punctuation.
  - [ ] Manually tested in Home Assistant (where feasible).
  - [ ] Updated or referenced the localisation tracking issue for progress.

If unsure about locale naming or scope, please ask in the issue or draft PR before proceeding.

## Development Hygiene

- Keep changes focused and avoid regressions.
- Follow EN‑AU spelling in documentation.
- Ensure Markdown has a blank line below headings and above/below lists for linting.
