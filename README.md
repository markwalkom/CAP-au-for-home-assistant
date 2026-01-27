<!-- omit from toc -->
# CAP-au ingester for Home Assistant

- [Summary](#summary)
- [Intended key features of future package](#intended-key-features-of-future-package)
	- [What's intended to be included (hybrid model)](#whats-intended-to-be-included-hybrid-model)
	- [Future install process at a glance](#future-install-process-at-a-glance)
- [What is CAP-au](#what-is-cap-au)
- [What CAP-au feeds are available](#what-cap-au-feeds-are-available)
	- [National](#national)
	- [New South Wales](#new-south-wales)
	- [Queensland](#queensland)
	- [South Australia](#south-australia)
	- [Victoria](#victoria)
	- [Western Australia](#western-australia)

## Summary

Repo for future Home Assistant HACS package and associated files, called **CAP-au-for-Home-Assistant**, that is intended to support ingest official CAP (Common Alerting Protocol) feeds into Home Assistant - which users can then turn into actionable, privacy‑preserving automations and UI views.

The package is intended to be **easy to install**, **offer safe defaults**, and provide **multi‑feed*- support.

## Intended key features of future package

When complete, or at least ready for its first release, I am hoping this package will support users of Home Assistant to:

- **Plug‑and‑play CAP ingestion (XML)*- via the Multiscrape integration, with parsing that keeps entity **states short*- and stores long values in **attributes*- (avoids the 255‑char clamp).
- **Unified alerts sensor**: a template aggregator exposes a count plus an `alerts` JSON attribute that dashboards and automations can consume.
- **Blueprints*- for:
  - **Notifications near watchpoints*- (radius for circles + point‑in‑polygon for polygons).
  - **Zones lifecycle*- (create/update/delete dynamic zones from alert geometry).
- **Python Scripts*- (sandbox‑safe; no imports) for geometry:
  - `cap_point_in_polygon.py` → fast point‑in‑polygon test.
  - `cap_polygon_to_zone.py` → centroid + covering radius for zone creation.
- **Dashboard card*- (Markdown) listing alerts with severity, urgency, area, issued time, and links.
- **Multi‑feed ready**: monitor multiple CAP feeds (e.g., state, national, overseas); use per‑feed or combined views.
- **Multi‑location ready**: review the feeds for CAP events impacting one or more locations.
- **Guided setup** with **my.home‑assistant*- deep‑links to the exact screens (Blueprint import, Developer Tools → YAML, Entities, Scripts, Events).

### What's intended to be included (hybrid model)

- **Package*- (`packages/cap_au.yaml`)  
  One drop‑in YAML that declares the CAP feed URL helper(s), Multiscrape sensors, and the template aggregator.
- **Automation Blueprints*-  
  UI‑first configuration of notifications and dynamic zones—no YAML edits required.
- **Python Scripts*- (HACS‑installable)  
  Import‑free helpers that run in Home Assistant’s Python Scripts sandbox.
- **Example Dashboard*-  
  A ready‑to‑paste Markdown card (plus an optional diagnostics card).

### Future install process at a glance

1. **Enable Packages*- in `configuration.yaml`  
   `homeassistant: packages: !include_dir_named packages`
2. **Add the package file*- to `/config/packages/`.
3. **Install Multiscrape*- (via HACS) and **install the Python Scripts*- (via HACS or manual copy).
4. **Import the Blueprints**, then create your automations from the UI.
5. **Add the Markdown card*- to any dashboard.

The full README will intend, wherever possible, to provide **one‑click badges*- (via `my.home-assistant.io`) for each step and a troubleshooting section (including enabling `log_response` in Multiscrape and quick self‑tests for the geometry scripts).

## What is CAP-au

From the [Bureau of Meterology](https://www.bom.gov.au/metadata/CAP-AU/About.shtml):

> CAP (and the Australian Profile of it: CAP-AU-STD) is a standardised data exchange format, using XML, that allows consistent and easy to understand emergency messages to be broadcast across a variety of communication systems. CAP can be used to alert and inform emergency response agencies, media and the general public.
>
> CAP ensures that messages remain consistent and clearly indicate to the recipient the severity of the threat and best response.

More information: [Data.gov.au](https://data.gov.au/data/dataset/cap-au-std)

## What CAP-au feeds are available

> [!NOTE]
> **List still being expanded**
> This list of feeds is still being expanded as they are found (especially since they're hard to find, or some states or agencies don't make these available publically). Please feel welcome to make a commit of you find a new CAP-au feed.

### National

- Geoscience Australia
  - [All Recent](https://earthquakes.ga.gov.au/feeds/all_recent.atom), [More Info](https://earthquakes.ga.gov.au) (tap on Notofications)

### New South Wales

- Rural Fire Service
  - [Alerts and Warnings Polygon Feed](https://www.rfs.nsw.gov.au/feeds/IncidentAlerts.xml)
  - [Current Incidents Feed](https://www.rfs.nsw.gov.au/feeds/majorIncidentsCAP.xml), [More Info](https://data.nsw.gov.au/data/dataset/nsw-rural-fire-service-current-incidents-feed/resource/d5b3ebb0-b73a-4f78-8442-605217b7cdb5).

### Queensland

- [Queensland Fire Deprtment](https://www.fire.qld.gov.au/Current-Incidents)
  - [Bushfire Current Incidents](https://publiccontent-gis-psba-qld-gov-au.s3.amazonaws.com/content/Feeds/BushfireCurrentIncidents/bushfireAlert_capau.xml).
- [Disaster Queensland](https://www.disaster.qld.gov.au/current-warnings).
  - [Severe Weather, Flood, Cyclone Warnings and Emergency Alerts](https://publiccontent-qld-alerts.s3.ap-southeast-2.amazonaws.com/content/Feeds/StormFloodCycloneWarnings/StormWarnings_capau.xml)

### South Australia

- [Country Fire Service](https://data.sa.gov.au/data/dataset/south-australian-country-fire-service-current-incidents-rss-feed/resource/1b30948e-d1f6-4e76-a552-b62ed61afbeb)
  - [Current Incidents](https://data.eso.sa.gov.au/prod/cfs/criimson/cfs_cap_incidents.xml)

### Victoria

- [Emergency Management Victoria](https://www.emv.vic.gov.au/)
Not publically available, [submit a request for access](https://support.emergency.vic.gov.au/hc/en-gb/articles/235717508-How-do-I-access-the-VicEmergency-data-feed).

### Western Australia

- [Emergency WA](https://www.emergency.wa.gov.au/about#rss)
  - [Feed](https://api.emergency.wa.gov.au/v1/capau)
