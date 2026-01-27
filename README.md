<!-- omit from toc -->
# CAP Alerts (Multi‑Feed) — Custom Integration (HACS)

Integration to turn public **CAP / ATOM / JSON** emergency feeds into actionable sensors, services, and dashboards — **no YAML edits**.

> [!WARNING]
> **DO NOT USE THIS INTEGRATION AS YOUR PRIMARY EMERGENCY INFORMATION SOURCE**
>
> This intergration:
>
> - **Does not take the place of, nor does it suppliment** any official emergency management agencies and their information sources.
> - **Do not rely on it as your sole warning channel for emergency information**. Always check and follow guidance from local emergency authorities.

> [!CAUTION]
> **DISCLAIMER**
> This project is free software under **GPL‑3.0** and is provided **“AS IS”** and **“AS AVAILABLE,” WITHOUT WARRANTIES** of any kind (including **merchantability**, **fitness**, **title**, **non‑infringement**, accuracy, timeliness). It is **not** a primary or official emergency information source. **Always** monitor and act on **official** warnings. **Liability is limited to the maximum extent permitted by law**; you **assume all risk** and must independently verify outputs and maintain separate official channels. See **[LEGAL‑DISCLAIMER.md](LEGAL‑DISCLAIMER.md)** for full terms.

- [Summary](#summary)
- [Intended key features of future package](#intended-key-features-of-future-package)
- [Feeds](#feeds)
  - [What feed types are supported?](#what-feed-types-are-supported)
  - [Where can I find supported feeds?](#where-can-i-find-supported-feeds)
  - [Feed sources and catalogue](#feed-sources-and-catalogue)
    - [Feed sources](#feed-sources)
    - [Feed catalogue](#feed-catalogue)
  - [Understanding feed types](#understanding-feed-types)
    - [Common Alerting Protocol (CAP), and CAP-au specification](#common-alerting-protocol-cap-and-cap-au-specification)
- [Install](#install)
  - [A) HACS (recommended)](#a-hacs-recommended)
  - [B) Manual](#b-manual)
- [First‑time Setup (Config Flow)](#firsttime-setup-config-flow)
  - [Legal Disclaimer Acceptance](#legal-disclaimer-acceptance)
  - [Choosing your watch locations \& radius](#choosing-your-watch-locations--radius)
  - [Entities](#entities)
  - [Services](#services)
- [Using the integration](#using-the-integration)
  - [Example: Dashboards](#example-dashboards)
  - [Example: Automations](#example-automations)
- [Refresh rate \& server load](#refresh-rate--server-load)
- [Limitations \& notes](#limitations--notes)
- [Troubleshooting](#troubleshooting)
  - [Repairs \& Fail‑safes](#repairs--failsafes)
- [Links \& supporting documentation](#links--supporting-documentation)

---

## Summary

Repo for future Home Assistant HACS package and associated files, currently called **CAP-au-for-Home-Assistant**, that is intended to support ingest official CAP (Common Alerting Protocol) and other feeds into Home Assistant - which users can then turn into actionable, privacy‑preserving automations and UI views.

The package is intended to be **easy to install**, **offer safe defaults**, and provide **multi‑feed*- support.

> [!WARNING]
> **Integration only intended as a supporting tool**
> This integration is only intended to help and support you during incidents, including:
>
> - Receive warnings of incidents believed to be impacting the locations you specify,
> - Provide the published text of those warnings from the relevant emergency management authority, and
> - Support you in developing automations that may contribute to preseve life, property, livestock, and services at locations you specify during an emergency.

> [!WARNING]
> **What can impact warnings, warning updates, and warning frequency**
> Warnings, warning updates, and warning frequency, can be impacted by:
>
> - Cooldown periods, to ensure emergency management agency servers are not overloaded with unnecessary requests;
> - Quality, fullness and availbility of information published by emergency management agencies; and/or
> - The continued operation of power, communications, and your HA instance (you won't receive or be able to action alerts if you have no power, no internet or connectivity, your HA instance hardware fails, or other circumstances which causes one or more things needed for this to work not to work).
> - Issues with your installation or configuration, that stops relevant events being identified from the feeds being monitored.

## Intended key features of future package

- **Multiple feeds** per instance (Config Flow + Options Flow)
- **Live feed catalogue** (in this repo) for easy browsing (Country → Region → Source)
- **Per‑feed** alert sensors + a **global** aggregate sensor
- **Geometry services** built‑in: point‑in‑polygon, proximity matching, create zones from polygons/circles
- **Multiple location monitoring** so you can filter alerts that are relevant to one or more locations (along with a radius or distance from border of location) to reduce noise.
- **Unified alerts sensor**: a template aggregator exposes a count plus an `alerts` JSON attribute that dashboards and automations can consume.
- **Blueprints*- for:
  - **Notifications near watchpoints*- (radius for circles + point‑in‑polygon for polygons).
  - **Zones lifecycle*- (create/update/delete dynamic zones from alert geometry).
- Works with dashboards & automations (examples below)

## Feeds

### What feed types are supported?

- Common Alerting Protocol (CAP), focusing on CAP-au at this time
- geoJSON
- XML

When choosing a feed that lacks information to identify where an alert physically relates to, the user will receive a warning that the feed may not be useful or relevant for the purpose of this integration.

### Where can I find supported feeds?

To asssit users, we have made efforts to have and maintain a catalog of known feeds, which we obtain from reliable sources.

When adding a feed using this integration, you will be presented with a navigable list of supported feeds by country and region, and in future - also filtered by language, from this catalog.

### Feed sources and catalogue

#### Feed sources

We query sources including the following, to update the list of supported feeds provided for this integration:

- CAP Alert Hub: [https://cap.alert-hub.org/](https://cap.alert-hub.org/)
- Alert-hub S3 listing: [https://alert-hub.s3.amazonaws.com/cap-sources.html](https://alert-hub.s3.amazonaws.com/cap-sources.html)
- WMO Alerting Authority RSS: [https://alertingauthority.wmo.int/rss.xml](https://alertingauthority.wmo.int/rss.xml)

#### Feed catalogue

- The catalogue lives at `data/feed_catalog.json` in this repository. It is also provided in JSON and YAML formats.
- **Requirements for inclusion:** public & stable URL; reuse permitted; **prefer CAP**; ATOM/JSON must be structured; geometry strongly preferred.  
  - Open a PR adding `{country, region, name, format, url}`.

### Understanding feed types

#### Common Alerting Protocol (CAP), and CAP-au specification

From the [Bureau of Meterology](https://www.bom.gov.au/metadata/CAP-AU/About.shtml):

> CAP (and the Australian Profile of it: CAP-AU-STD) is a standardised data exchange format, using XML, that allows consistent and easy to understand emergency messages to be broadcast across a variety of communication systems. CAP can be used to alert and inform emergency response agencies, media and the general public.
>
> CAP ensures that messages remain consistent and clearly indicate to the recipient the severity of the threat and best response.

More information on CAP-au: [Data.gov.au](https://data.gov.au/data/dataset/cap-au-std)

## Install

### A) HACS (recommended)

1. Install HACS.  
2. HACS → *Integrations* → Search **“CAP Alerts (Multi‑Feed)”** → *Install*.
3. Add the integration:  
   [![Add Integration](https://my.home-assistant.io/badges/integrations.svg)](https://my.home-assistant.io/redirect/integrations/) → **CAP Alerts**.

### B) Manual

1. Copy `custom_components/cap_alerts/` to `/config/custom_components/`.
2. Restart Home Assistant.
3. Add the integration from **Settings → Devices & Services**.

## First‑time Setup (Config Flow)

1. Navigate to *specify location in HA and provide deep link to same if possible*
2. Choose **Browse catalogue** or **Manual URL**:
   - **Browse** uses the live `data/feed_catalog.json` from this repo (no releases needed for updates).
   - **Manual** supports `cap`, `atom`, or `json`.

Add more feeds any time via the integration by going to **Options**.

### Legal Disclaimer Acceptance

During setup, you must accept the **Legal Disclaimer**. The full text is presented in the UI and linked to [LEGAL‑DISCLAIMER.md](LEGAL-DISCLAIMER.md). Your acceptance records the time, your user ID, and a signed hash of the disclaimer text. If the disclaimer changes or the record is altered, the integration will be disabled and a **Repairs** message will be shown until you reaccept.

### Choosing your watch locations & radius

// [ ] FIXME: Add information here on where to specify the watch locations and radiuses

Add information here on where to set and specify the watch locations and radiuses.

Use any of these patterns when calling `cap_alerts.find_matches`:

1. **Home zone**: `lat: {{ state_attr('zone.home','latitude') }}` `lon: {{ state_attr('zone.home','longitude') }}`
2. **A person/device**: `lat: {{ state_attr('person.personname','latitude') }}` `lon: {{ state_attr('person.personname','longitude') }}`
3. **Helpers** (for fixed coordinates): create `input_number.watch_lat_1` and `input_number.watch_lon_1` (or any names) and use their values in templates.

> You can schedule checks (e.g., every 10 minutes) and use the emitted `cap_alerts.matches` **event** as a gate for notifications or actions.

### Entities

- **Per‑feed**: `sensor.cap_<domain_slug>_alert_count`  
  Attributes: `alerts` (normalized list), `features` (`has_polygons`, `has_circles`, `has_points`, optional `warning`).
- **Global**: `sensor.cap_all_alert_count`  
  Attributes: `raw` (array with per‑feed results).

### Services

- `cap_alerts.find_matches`:  
  **Data:** `lat`, `lon`, `radius_km`, optional `feed_slugs` → Event: `cap_alerts.matches` with up to 50 matches.
- `cap_alerts.point_in_polygon`:  
  **Data:** `polygon`, `lat`, `lon` → Event: `cap_alerts.point_in_polygon_result` `{match}`
- `cap_alerts.create_zones_for_feed`:  
  **Data:** `feed_slug`, `max_zones` (default 10), `name_template` (e.g., `CAP {slug} #{n}`), `icon`, `include_circles` (bool).  
  Creates zones for latest **polygons** (and optionally **circles**) in a feed.
- `cap_alerts.create_zone_from_polygon`:  
  **Data:** `polygon`, `name`, `icon` → Creates a HA zone from polygon centroid/radius.

## Using the integration

### Example: Dashboards

Paste into a **Markdown** card:

```yaml
{% set raw = state_attr('sensor.cap_all_alert_count','raw') or [] %}
## ⚠️ CAP Alerts (all feeds): {{ states('sensor.cap_all_alert_count') | int(0) }} total
{% for feed in raw %}
- **{{ feed.feed.name if feed.feed else 'Feed' }}** — {{ (feed.alerts | count) if feed.alerts is iterable else 0 }} items
{% endfor %}
```

### Example: Automations

- **Every 10 minutes**, check proximity to **Home zone**:

```yaml
alias: Notify on local CAP matches (Home zone)
mode: single
trigger: [{ platform: time_pattern, minutes: "/10" }]
action:
  - service: cap_alerts.find_matches
    data:
      lat: "{{ state_attr('zone.home','latitude') }}"
      lon: "{{ state_attr('zone.home','longitude') }}"
      radius_km: 15
  - wait_for_trigger:
      - platform: event
        event_type: cap_alerts.matches
    timeout: "00:00:10"
  - choose:
      - conditions: "{{ trigger.event.data.count | int(0) > 0 }}"
        sequence:
          - service: persistent_notification.create
            data:
              title: "CAP Matches near home"
              message: >-
                {{ trigger.event.data.count }} match(es) within 15 km. First: 
                {{ (trigger.event.data.matches[0].alert.headline or 'n/a') }}
```

- **Person** location (replace `person.personname`):

```yaml
alias: Notify on local CAP matches (Person)
mode: single
trigger: [{ platform: time_pattern, minutes: "/10" }]
action:
  - service: cap_alerts.find_matches
    data:
      lat: "{{ state_attr('person.personname','latitude') }}"
      lon: "{{ state_attr('person.personname','longitude') }}"
      radius_km: 10
  - wait_for_trigger: [{ platform: event, event_type: cap_alerts.matches }]
  - choose:
      - conditions: "{{ trigger.event.data.count | int(0) > 0 }}"
        sequence:
          - service: notify.mobile_app_pixel
            data:
              title: "CAP alert near Michael"
              message: >-
                {{ (trigger.event.data.matches[0].alert.headline or 'n/a') }}
```

- **Helpers** (fixed coordinates): create two helpers and reference them:

```yaml
alias: Notify on local CAP matches (Helpers)
mode: single
trigger: [{ platform: time_pattern, minutes: "/15" }]
action:
  - service: cap_alerts.find_matches
    data:
      lat: "{{ states('input_number.watch_lat_1') }}"
      lon: "{{ states('input_number.watch_lon_1') }}"
      radius_km: 25
  - wait_for_trigger: [{ platform: event, event_type: cap_alerts.matches }]
  - choose:
      - conditions: "{{ trigger.event.data.count | int(0) > 0 }}"
        sequence:
          - service: persistent_notification.create
            data:
              title: "CAP Matches near Watchpoint 1"
              message: >-
                {{ trigger.event.data.count }} match(es).
```

## Refresh rate & server load

- Default polling is **every 5 minutes** (integration coordinator).  
  This balances reasonable freshness with responsible load on public endpoints.  
- Avoid aggressive polling; many authorities cache results and may throttle.  

## Limitations & notes

- Producers vary; geometry may be absent → the integration flags such feeds via `features.warning`.
- Parsing is best‑effort (no scraping of HTML). ATOM is minimal (title/updated/link + `georss` if present).
- This project **does not replace** official warning channels.

## Troubleshooting

- **No entities?** Confirm the integration resides at `custom_components/cap_alerts/`; restart HA.
- **Counts but no geometry?** See `features.warning`; some feeds do not publish polygons/circles/points.
- **Catalogue not loading?** Ensure GitHub raw is reachable and JSON is valid.

### Repairs & Fail‑safes

- **Disclaimer required**: If the disclaimer isn’t accepted or has changed, CAP Alerts remains disabled and a **Repairs** issue explains how to reaccept.
- **Feed disabled**: A feed that repeatedly fails (default 5 consecutive failures) is temporarily disabled. Use **Options → Reset failures for feed** after resolving the underlying issue to re‑enable.

## Links & supporting documentation

- HA Disclaimer Gate & Repairs (developer): [.github/instructions/ha-disclaimer-gate-and-repairs.md](.github/instructions/ha-disclaimer-gate-and-repairs.md)
- Project Copilot Instructions (developer): [.github/instructions/copilot.instructions.md](.github/instructions/copilot.instructions.md)

- HACS Integration publishing: [https://hacs.xyz/docs/publish/integration)](https://hacs.xyz/docs/publish/integration/)  
- HACS general requirements: [https://hacs.xyz/docs/publish/start/](https://hacs.xyz/docs/publish/start/)
- HA Config Flow & Options Flow: [https://developers.home-assistant.io/docs/config_entries_config_flow_handler/](https://developers.home-assistant.io/docs/config_entries_config_flow_handler/), [https://developers.home-assistant.io/docs/config_entries_options_flow_handler/](https://developers.home-assistant.io/docs/config_entries_options_flow_handler/)
