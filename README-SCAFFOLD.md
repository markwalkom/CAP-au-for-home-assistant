# CAP feeds for Home Assistant — Scaffold (Preview)

> This is a **scaffold** for the upcoming multi‑feed CAP integration using a hybrid approach: **Packages + Blueprints + HACS‑installable Python Scripts**. It is designed to support **any number of CAP feeds** via a file‑per‑feed model and a **global aggregator**.

---

## Quick Start (Preview)

1. **Enable Packages** in `configuration.yaml`:

   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```

2. **Copy** the files from `packages/` and `packages/cap_feeds/` into your Home Assistant `/config/packages/` folder.

3. **Add your first feed**:
   - Duplicate `packages/cap_feeds/cap_feed__example_wa.yaml` and rename it (e.g., `cap_feed_nsw.yaml`).
   - Edit the `resource:` URL and the `feed_id` (used in entity names), save.
   - Restart Home Assistant.

4. **Install the Python Scripts** by copying the files under `python_scripts/` into `/config/python_scripts/` and ensuring you have:
   
   ```yaml
   python_script:
   ```

5. **Import the Blueprints** from `blueprints/automation/twcau/` (Blueprint import URLs will be published when the repo is released).

6. **Add the Dashboard cards** from `/dashboards/` (Markdown examples for global and per‑feed views).

7. **(Optional) Feed directory**: See `data/feeds_directory.yaml` for examples of national/state CAP sources.

> A full README with *my.home‑assistant* badges will be provided for one‑click navigation once the repository is live.
