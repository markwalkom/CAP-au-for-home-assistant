"""
Update and enrich data/feed_catalog.json, then synchronise feeds_directory.json/yaml.

What this does:
- Ensures every feed has `language` (ISO 639-1) and `countryCode` (ISO 3166-1 alpha-2).
- Adds provenance metadata: `provenance`, `firstAdded`, `lastChecked` (ISO dates).
- Ingests new CAP sources from:
    * https://alert-hub.s3.amazonaws.com/cap-sources.html
    * https://cap.alert-hub.org/
    * https://alertingauthority.wmo.int/rss.xml (CAP-only links if present)
- Rebuilds data/feeds_directory.json and data/feeds_directory.yaml from the catalogue.

Parsing:
- Uses BeautifulSoup (bs4) when available for robust HTML parsing; falls back to regex scanning if bs4 is not installed.

Run:
    python scripts/update_feed_catalog.py

Install optional parser dependency:
    pip install beautifulsoup4 lxml
"""
from __future__ import annotations
import json
import os
import re
import urllib.request
from datetime import date
import tempfile
from typing import Dict

# Minimal self-contained ISO 3166-1 alpha-2 mapping to country names.
# Note: Some sources may use non-standard codes (e.g., UK). Include practical aliases.
ISO3166_ALPHA2_TO_NAME: Dict[str, str] = {
    "AF": "Afghanistan", "AX": "Åland Islands", "AL": "Albania", "DZ": "Algeria",
    "AS": "American Samoa", "AD": "Andorra", "AO": "Angola", "AI": "Anguilla",
    "AQ": "Antarctica", "AG": "Antigua and Barbuda", "AR": "Argentina", "AM": "Armenia",
    "AW": "Aruba", "AU": "Australia", "AT": "Austria", "AZ": "Azerbaijan",
    "BS": "Bahamas", "BH": "Bahrain", "BD": "Bangladesh", "BB": "Barbados",
    "BY": "Belarus", "BE": "Belgium", "BZ": "Belize", "BJ": "Benin",
    "BM": "Bermuda", "BT": "Bhutan", "BO": "Bolivia", "BQ": "Bonaire, Sint Eustatius and Saba",
    "BA": "Bosnia and Herzegovina", "BW": "Botswana", "BV": "Bouvet Island", "BR": "Brazil",
    "IO": "British Indian Ocean Territory", "BN": "Brunei Darussalam", "BG": "Bulgaria", "BF": "Burkina Faso",
    "BI": "Burundi", "CV": "Cabo Verde", "KH": "Cambodia", "CM": "Cameroon",
    "CA": "Canada", "KY": "Cayman Islands", "CF": "Central African Republic", "TD": "Chad",
    "CL": "Chile", "CN": "China", "CX": "Christmas Island", "CC": "Cocos (Keeling) Islands",
    "CO": "Colombia", "KM": "Comoros", "CG": "Congo", "CD": "Congo (Democratic Republic of the)",
    "CK": "Cook Islands", "CR": "Costa Rica", "CI": "Côte d’Ivoire", "HR": "Croatia",
    "CU": "Cuba", "CW": "Curaçao", "CY": "Cyprus", "CZ": "Czechia",
    "DK": "Denmark", "DJ": "Djibouti", "DM": "Dominica", "DO": "Dominican Republic",
    "EC": "Ecuador", "EG": "Egypt", "SV": "El Salvador", "GQ": "Equatorial Guinea",
    "ER": "Eritrea", "EE": "Estonia", "SZ": "Eswatini", "ET": "Ethiopia",
    "FK": "Falkland Islands (Malvinas)", "FO": "Faroe Islands", "FJ": "Fiji", "FI": "Finland",
    "FR": "France", "GF": "French Guiana", "PF": "French Polynesia", "TF": "French Southern Territories",
    "GA": "Gabon", "GM": "Gambia", "GE": "Georgia", "DE": "Germany",
    "GH": "Ghana", "GI": "Gibraltar", "GR": "Greece", "GL": "Greenland",
    "GD": "Grenada", "GP": "Guadeloupe", "GU": "Guam", "GT": "Guatemala",
    "GG": "Guernsey", "GN": "Guinea", "GW": "Guinea-Bissau", "GY": "Guyana",
    "HT": "Haiti", "HM": "Heard Island and McDonald Islands", "VA": "Holy See",
    "HN": "Honduras", "HK": "Hong Kong", "HU": "Hungary",
    "IS": "Iceland", "IN": "India", "ID": "Indonesia", "IR": "Iran", "IQ": "Iraq",
    "IE": "Ireland", "IM": "Isle of Man", "IL": "Israel", "IT": "Italy",
    "JM": "Jamaica", "JP": "Japan", "JE": "Jersey", "JO": "Jordan",
    "KZ": "Kazakhstan", "KE": "Kenya", "KI": "Kiribati", "KP": "Korea (Democratic People's Republic of)",
    "KR": "Korea (Republic of)", "KW": "Kuwait", "KG": "Kyrgyzstan",
    "LA": "Lao People’s Democratic Republic", "LV": "Latvia", "LB": "Lebanon", "LS": "Lesotho",
    "LR": "Liberia", "LY": "Libya", "LI": "Liechtenstein", "LT": "Lithuania",
    "LU": "Luxembourg", "MO": "Macao", "MG": "Madagascar", "MW": "Malawi",
    "MY": "Malaysia", "MV": "Maldives", "ML": "Mali", "MT": "Malta",
    "MH": "Marshall Islands", "MQ": "Martinique", "MR": "Mauritania", "MU": "Mauritius",
    "YT": "Mayotte", "MX": "Mexico", "FM": "Micronesia (Federated States of)", "MD": "Moldova",
    "MC": "Monaco", "MN": "Mongolia", "ME": "Montenegro", "MS": "Montserrat",
    "MA": "Morocco", "MZ": "Mozambique", "MM": "Myanmar", "NA": "Namibia",
    "NR": "Nauru", "NP": "Nepal", "NL": "Netherlands", "NC": "New Caledonia",
    "NZ": "New Zealand", "NI": "Nicaragua", "NE": "Niger", "NG": "Nigeria",
    "NU": "Niue", "NF": "Norfolk Island", "MK": "North Macedonia", "MP": "Northern Mariana Islands",
    "NO": "Norway", "OM": "Oman", "PK": "Pakistan", "PW": "Palau",
    "PS": "Palestine, State of", "PA": "Panama", "PG": "Papua New Guinea", "PY": "Paraguay",
    "PE": "Peru", "PH": "Philippines", "PN": "Pitcairn", "PL": "Poland",
    "PT": "Portugal", "PR": "Puerto Rico", "QA": "Qatar", "RE": "Réunion",
    "RO": "Romania", "RU": "Russian Federation", "RW": "Rwanda",
    "BL": "Saint Barthélemy", "SH": "Saint Helena, Ascension and Tristan da Cunha", "KN": "Saint Kitts and Nevis",
    "LC": "Saint Lucia", "MF": "Saint Martin (French part)", "PM": "Saint Pierre and Miquelon",
    "VC": "Saint Vincent and the Grenadines", "WS": "Samoa", "SM": "San Marino", "ST": "Sao Tome and Principe",
    "SA": "Saudi Arabia", "SN": "Senegal", "RS": "Serbia", "SC": "Seychelles",
    "SL": "Sierra Leone", "SG": "Singapore", "SX": "Sint Maarten (Dutch part)", "SK": "Slovakia",
    "SI": "Slovenia", "SB": "Solomon Islands", "SO": "Somalia", "ZA": "South Africa",
    "GS": "South Georgia and the South Sandwich Islands", "SS": "South Sudan", "ES": "Spain", "LK": "Sri Lanka",
    "SD": "Sudan", "SR": "Suriname", "SJ": "Svalbard and Jan Mayen", "SE": "Sweden",
    "CH": "Switzerland", "SY": "Syrian Arab Republic", "TW": "Taiwan", "TJ": "Tajikistan",
    "TZ": "Tanzania, United Republic of", "TH": "Thailand", "TL": "Timor-Leste", "TG": "Togo",
    "TK": "Tokelau", "TO": "Tonga", "TT": "Trinidad and Tobago", "TN": "Tunisia",
    "TR": "Türkiye", "TM": "Turkmenistan", "TC": "Turks and Caicos Islands", "TV": "Tuvalu",
    "UG": "Uganda", "UA": "Ukraine", "AE": "United Arab Emirates", "GB": "United Kingdom",
    "UK": "United Kingdom", "US": "United States", "UM": "United States Minor Outlying Islands",
    "UY": "Uruguay", "UZ": "Uzbekistan", "VU": "Vanuatu", "VE": "Venezuela",
    "VN": "Viet Nam", "VG": "Virgin Islands (British)", "VI": "Virgin Islands (U.S.)",
    "WF": "Wallis and Futuna", "EH": "Western Sahara", "YE": "Yemen", "ZM": "Zambia", "ZW": "Zimbabwe",
    "XK": "Kosovo",
}

try:
    from bs4 import BeautifulSoup  # type: ignore
except Exception:  # pragma: no cover
    BeautifulSoup = None  # will use regex fallback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.join(ROOT, "data", "feed_catalog.json")
DIR_JSON_PATH = os.path.join(ROOT, "data", "feeds_directory.json")
DIR_YAML_PATH = os.path.join(ROOT, "data", "feeds_directory.yaml")

def load_catalog() -> dict:
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_catalog(data: dict) -> None:
    os.makedirs(os.path.dirname(CATALOG_PATH), exist_ok=True)
    tmp_path = CATALOG_PATH + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, CATALOG_PATH)
    except (FileNotFoundError, PermissionError, OSError) as exc:
        # Fallback to system temp to distinguish environment write issues
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json", encoding="utf-8") as tf:
            json.dump(data, tf, ensure_ascii=False, indent=2)
            temp_out = tf.name
        try:
            os.replace(temp_out, CATALOG_PATH)
        except Exception as exc2:
            print(
                "ERROR: Unable to write catalogue to target path.\n"
                f"Target: {CATALOG_PATH}\n"
                f"Original error: {exc!r}\n"
                f"Replace-from-temp failed: {exc2!r}\n"
                "Suggestion: Move the repo to a non-OneDrive folder or adjust permissions, then rerun.\n"
                f"Catalogue content was written to temporary file: {temp_out}"
            )

def ensure_defaults(feed: dict) -> dict:
    """Normalise fields and migrate legacy keys.

    - language: ISO 639-1, defaults to 'en'
    - countryCode: ISO 3166-1 alpha-2 inferred from country when missing
    - provenance/firstAdded/lastChecked: ensure present; migrate older 'source'/'added'
    """
    # Default/derive language
    if not feed.get("language"):
        feed["language"] = "en"
    else:
        # If URL indicates a specific language, prefer it over a generic default
        url = feed.get("url") or ""
        _, lang_from_url = extract_cc_lang_from_url(url)
        if lang_from_url and feed["language"] == "en" and lang_from_url != "en":
            feed["language"] = lang_from_url
    # Country code inference and normalisation
    cc_existing = (feed.get("countryCode") or "").upper()
    if cc_existing == "KO":
        # Normalise non-standard KO to XK (Kosovo)
        feed["countryCode"] = "XK"
        cc_existing = "XK"
    if not cc_existing:
        # Try infer from existing country name
        cc = guess_country_code(feed.get("country", ""))
        # Or derive from URL identifier
        if not cc:
            url = feed.get("url") or ""
            cc, _ = extract_cc_lang_from_url(url)
        if cc:
            # Apply alias if needed
            feed["countryCode"] = "XK" if cc.upper() == "KO" else cc
            # If country name is unknown or 2-letter code, fill from code
            if not feed.get("country") or (feed.get("country") == "Unknown") or is_iso2(feed.get("country")):
                feed["country"] = country_name_from_code(feed["countryCode"])
    else:
        # If we already have a code but the country name is missing/Unknown, backfill from code
        if (not feed.get("country") or feed.get("country") == "Unknown"):
            feed["country"] = country_name_from_code(cc_existing)

    # Normalise country field if it contains a 2-letter code
    if feed.get("country") and is_iso2(feed["country"]):
        feed["country"] = country_name_from_code(feed["country"]) or feed["country"]

    # AU-specific normalisation: ensure states nest under Australia
    au_states = {
        "New South Wales",
        "Queensland",
        "South Australia",
        "Tasmania",
        "Victoria",
        "Western Australia",
        "Australian Capital Territory",
        "Northern Territory",
    }
    if (feed.get("countryCode") == "AU") and (feed.get("country") in au_states):
        state = feed["country"]
        provider = feed.get("region") or "General"
        feed["region"] = f"{state} / {provider}"
        feed["country"] = "Australia"
    # Migrate legacy provenance keys
    if feed.get("source") and not feed.get("provenance"):
        feed["provenance"] = feed.pop("source")
    if feed.get("added") and not feed.get("firstAdded"):
        feed["firstAdded"] = feed.pop("added")
    # Ensure provenance defaults
    today = date.today().isoformat()
    if not feed.get("provenance"):
        feed["provenance"] = "package developer"
    if not feed.get("firstAdded"):
        feed["firstAdded"] = today
    # Always bump lastChecked
    feed["lastChecked"] = today
    return feed

def guess_country_code(country: str) -> str | None:
    mapping = {
        "Australia": "AU",
        "United States": "US",
        "New South Wales": "AU",
        "Queensland": "AU",
        "South Australia": "AU",
        "Western Australia": "AU",
        "Victoria": "AU",
    }
    return mapping.get(country)

def try_fetch(url: str) -> str:
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return ""

def ingest_alert_hub_sources(catalog: dict) -> None:
    """Parse alert-hub S3 and cap.alert-hub.org to discover CAP feed URLs.

    Strategy:
    - Parse tables for rows; capture language, source name, and any http links.
    - When only an identifier like "us-noaa-nws-en" is present, attempt to find a matching link
      on cap.alert-hub.org and retain http(s) URLs ending with .xml or containing '/cap'.
    """
    html_s3 = try_fetch("https://alert-hub.s3.amazonaws.com/cap-sources.html")
    if not html_s3:
        return
    discovered: list[dict] = []
    if BeautifulSoup:
        soup = BeautifulSoup(html_s3, "lxml") if "lxml" in globals() else BeautifulSoup(html_s3, "html.parser")
        # Track previous non-blank country for rows that inherit
        prev_country_name = None
        for row in soup.select("table tr"):
            cells = row.find_all(["td", "th"]) or []
            if not cells:
                continue
            cols = [c.get_text(strip=True) for c in cells]
            # Heuristic: many tables have Country in col 0, Language in col 1, Name in col 2
            country_name = cols[0] if len(cols) > 0 else None
            language_name = cols[1] if len(cols) > 1 else None
            source_name = cols[2] if len(cols) > 2 else None
            if not country_name:
                country_name = prev_country_name
            else:
                prev_country_name = country_name
            lang = derive_language(language_name)
            # Extract links in the row
            links = [a.get("href") for a in row.find_all("a") if a.get("href")]
            cap_links = [u for u in links if u.startswith("http") and (u.endswith(".xml") or "/cap" in u.lower())]
            for url in cap_links:
                cc_from_url, lang_from_url = extract_cc_lang_from_url(url)
                if lang_from_url:
                    lang = lang_from_url
                cc = cc_from_url or guess_country_code(country_name or "")
                cname = country_name_from_code(cc) if cc else (country_name or "Unknown")
                feed = make_feed_from_url(url, source_name or "CAP Feed", lang, country_override=cname, cc_override=cc)
                discovered.append(feed)
    else:
        # Fallback: regex scan for http...xml patterns
        for url in re.findall(r"https?://[^\s'\"]+\.xml", html_s3):
            feed = make_feed_from_url(url, "CAP Source", "en")
            discovered.append(feed)
    merge_discovered(catalog, discovered, source_label="alert-hub")

    # cap.alert-hub.org index page for additional links
    html_idx = try_fetch("https://cap.alert-hub.org/")
    if html_idx:
        disc2: list[dict] = []
        if BeautifulSoup:
            soup2 = BeautifulSoup(html_idx, "lxml") if "lxml" in globals() else BeautifulSoup(html_idx, "html.parser")
            prev_country = None
            rows = soup2.select("table tr") or []
            if rows:
                for row in rows:
                    cells = row.find_all(["td", "th"]) or []
                    if not cells:
                        continue
                    cols = [c.get_text(strip=True) for c in cells]
                    country = cols[0] if len(cols) > 0 else None
                    if not country:
                        country = prev_country
                    else:
                        prev_country = country
                    language_name = cols[1] if len(cols) > 1 else None
                    link_el = row.find("a")
                    href = link_el.get("href") if link_el else ""
                    text = link_el.get_text(strip=True) if link_el else ""
                    if href and href.startswith("http") and (href.endswith(".xml") or "/cap" in href.lower()):
                        lang = derive_language(language_name)
                        cc_from_url, lang_from_url = extract_cc_lang_from_url(href)
                        if lang_from_url:
                            lang = lang_from_url
                        cc = cc_from_url or guess_country_code(country or "")
                        cname = country_name_from_code(cc) if cc else (country or "Unknown")
                        disc2.append(make_feed_from_url(href, text or "Authority feed", lang, country_override=cname, cc_override=cc))
            else:
                for a in soup2.find_all("a"):
                    href = a.get("href") or ""
                    text = a.get_text(strip=True)
                    if href.startswith("http") and (href.endswith(".xml") or "/cap" in href.lower()):
                        cc_from_url, lang_from_url = extract_cc_lang_from_url(href)
                        disc2.append(make_feed_from_url(href, text or "Authority feed", lang_from_url or "en", cc_override=cc_from_url, country_override=None))
        else:
            for url in re.findall(r"https?://[^\s'\"]+\.xml", html_idx):
                disc2.append(make_feed_from_url(url, "Authority feed", "en"))
        merge_discovered(catalog, disc2, source_label="cap.alert-hub.org")

def ingest_wmo_rss(catalog: dict) -> None:
    """Parse WMO Alerting Authority RSS to discover CAP feed URLs.

    Strategy:
    - Fetch RSS XML and extract absolute URLs that look like CAP endpoints
      (end with .xml or contain '/cap').
    - Use entry titles when present as feed name.
    """
    rss = try_fetch("https://alertingauthority.wmo.int/rss.xml")
    if not rss:
        return
    discovered: list[dict] = []
    # Try BeautifulSoup XML parsing first
    if BeautifulSoup:
        soup = BeautifulSoup(rss, "xml")
        for item in soup.find_all("item"):
            title = (item.find_text("title") or "WMO Authority").strip()
            # Collect all links-like elements
            hrefs: list[str] = []
            link_el = item.find("link")
            if link_el and link_el.get_text():
                hrefs.append(link_el.get_text().strip())
            # Also scan description for URLs
            desc = item.find("description")
            text = desc.get_text() if desc and desc.get_text() else ""
            hrefs += re.findall(r"https?://[^\s'\"]+", text)
            for href in hrefs:
                if href.startswith("http") and (href.endswith(".xml") or "/cap" in href.lower()):
                    discovered.append(make_feed_from_url(href, title, "en"))
    else:
        # Regex-only fallback
        for href in re.findall(r"https?://[^\s'\"]+", rss):
            if href.endswith(".xml") or "/cap" in href.lower():
                discovered.append(make_feed_from_url(href, "WMO Authority", "en"))
    merge_discovered(catalog, discovered, source_label="wmo.alertingauthority")

def guess_language_code(language_name: str) -> str:
    s = (language_name or "").strip().lower()
    if re.fullmatch(r"[a-z]{2}", s):
        return s
    mapping = {
        "english": "en",
        "french": "fr",
        "spanish": "es",
        "german": "de",
        "portuguese": "pt",
        "arabic": "ar",
        "russian": "ru",
        "chinese": "zh",
        "japanese": "ja",
        "korean": "ko",
        "swedish": "sv",
        "norwegian": "no",
        "dutch": "nl",
        "italian": "it",
        "finnish": "fi",
        "polish": "pl",
        "czech": "cs",
        "hungarian": "hu",
        "slovak": "sk",
        "slovenian": "sl",
        "thai": "th",
        "indonesian": "id",
        "malay": "ms",
        "vietnamese": "vi",
    }
    return mapping.get(s, "en")

def derive_language(language_name: str | None) -> str:
    return guess_language_code(language_name) if language_name else "en"

def extract_cc_lang_from_url(url: str) -> tuple[str | None, str | None]:
    """Infer ISO 3166-1 alpha-2 country code and language code from common patterns.

    Supports two- or three-letter language codes (e.g., nl, pap, tet, kmr, ckb).

    Example: https://cap-sources.s3.amazonaws.com/aw-gov-nl/rss.xml -> (AW, nl)
             https://cap-sources.s3.amazonaws.com/ir-irimo-ckb/rss.xml -> (IR, ckb)
    """
    m = re.search(r"/([a-z]{2})-[^/]*-([a-z]{2,3})/(?:rss\\.xml|[^/]*)$", url, re.I)
    if m:
        cc = m.group(1).upper()
        lang = m.group(2).lower()
        # Alias non-standard country codes used by sources
        if cc == "KO":
            cc = "XK"  # Kosovo (commonly represented as XK)
        return cc, lang
    return None, None

def make_feed_from_url(url: str, name: str, language: str, *, country_override: str | None = None, cc_override: str | None = None) -> dict:
    cc = None
    # Prefer explicit override
    if cc_override:
        cc = cc_override
    # Rough country inference from domain path if present (e.g., alerts.weather.gov/us.php)
    m = re.search(r"https?://([a-z0-9.-]+)/", url, re.I)
    host = m.group(1) if m else ""
    if host.endswith(".gov.au"):
        cc = "AU"
    elif host.endswith("weather.gov"):
        cc = "US"
    if not cc:
        cc_from_url, lang_from_url = extract_cc_lang_from_url(url)
        if cc_from_url:
            cc = cc_from_url
        if lang_from_url and not language:
            language = lang_from_url
    fmt = "cap"
    return {
        "country": country_override or (country_name_from_code(cc) if cc else "Unknown"),
        "countryCode": cc or "",
        "region": "Authority",
        "name": name or "CAP Feed",
        "format": fmt,
        "url": url,
        "language": language or "en",
        "provenance": "discovered",
        "firstAdded": date.today().isoformat(),
        "lastChecked": date.today().isoformat(),
    }

def country_name_from_code(cc: str | None) -> str:
    code = (cc or "").upper()
    return ISO3166_ALPHA2_TO_NAME.get(code, "Unknown")

def is_iso2(val: str | None) -> bool:
    return bool(val) and bool(re.fullmatch(r"[A-Z]{2}", str(val)))

def merge_discovered(catalog: dict, discovered: list[dict], source_label: str) -> None:
    if not discovered:
        return
    existing_urls = { (f.get("url") or "").strip() for f in (catalog.get("feeds") or []) }
    for feed in discovered:
        url = (feed.get("url") or "").strip()
        if not url or url in existing_urls:
            continue
        feed["provenance"] = source_label
        catalog.setdefault("feeds", []).append(feed)
        existing_urls.add(url)

def build_directories(catalog: dict) -> tuple[dict, str]:
    # Build a nested dict by country -> region -> {name: url}
    dj: dict = {}
    for feed in catalog.get("feeds", []):
        # Normalise country to human name
        country_raw = (feed.get("country") or "").strip()
        if is_iso2(country_raw):
            country = country_name_from_code(country_raw)
        else:
            cc = (feed.get("countryCode") or "").strip()
            country = (country_name_from_code(cc) if (country_raw in ("", "Unknown") and cc) else (country_raw or (country_name_from_code(cc) if cc else "Unknown")))
        region = feed.get("region") or "General"
        base_name = feed.get("name") or "Feed"
        url = feed.get("url") or ""
        fmt = (feed.get("format") or "").upper()
        # Build display name: Country - FMT Name - LanguageNative
        lang_code = (feed.get("language") or "en").lower()
        country_code = (feed.get("countryCode") or "").upper()
        country_display = localize_country_name(country_code, lang_code, fallback=country)
        language_display = language_native_name(lang_code)
        display_name = f"{country_display} - {fmt} {base_name} - {language_display}" if fmt else f"{country_display} - {base_name} - {language_display}"
        dj.setdefault(country, {}).setdefault(region, {})[display_name] = url
    # Build YAML plaintext with indentation
    lines = ["# data/feeds_directory.yaml", "# Auto-generated from feed_catalog.json"]
    for country in sorted(dj.keys()):
        lines.append(f"{country}:")
        for region in sorted(dj[country].keys()):
            lines.append(f"  {region}:")
            for name, url in dj[country][region].items():
                lines.append(f"    {name}: {url}")
    yaml_text = "\n".join(lines) + "\n"
    return dj, yaml_text

def language_native_name(code: str) -> str:
    mapping = {
        "en": "English",
        "nl": "Nederlands",
        "ha": "Hausa",
        "pap": "Papiamentu",
        "tet": "Tetun",
        "kmr": "Kurmancî",
        "ckb": "کوردیی ناوەندی",
        "ar": "العربية",
        "fr": "Français",
        "es": "Español",
        "de": "Deutsch",
        "it": "Italiano",
        "pt": "Português",
        "sw": "Kiswahili",
        "ru": "Русский",
    }
    return mapping.get(code, code)

def localize_country_name(cc: str, lang_code: str, fallback: str) -> str:
    # Best-effort localisation; fallback to English name if specific localisation is unavailable
    en_name = country_name_from_code(cc) if cc else fallback
    if not cc:
        return fallback
    # Specific cases where a widely-used local name differs
    if cc == "CW" and lang_code == "pap":
        return "Kòrsou"
    if cc == "TR" and lang_code in {"kmr", "ckb"}:
        return "Tirkiye"
    if cc == "IR" and lang_code == "ckb":
        return "ئێران"
    if cc == "IQ" and lang_code == "ckb":
        return "ئێراق"
    # Default: English name
    return en_name

def main() -> None:
    catalog = load_catalog()
    # Ensure defaults for all existing feeds
    catalog["feeds"] = [ensure_defaults(f) for f in (catalog.get("feeds") or [])]
    # Attempt ingestion from external sources (non-destructive)
    ingest_alert_hub_sources(catalog)
    ingest_wmo_rss(catalog)
    # Save catalog back
    save_catalog(catalog)
    # Rebuild directories
    dj, yaml_text = build_directories(catalog)
    # Write atomically to avoid sync interference, with robust fallbacks
    tmp_json = DIR_JSON_PATH + ".tmp"
    tmp_yaml = DIR_YAML_PATH + ".tmp"
    try:
        with open(tmp_json, "w", encoding="utf-8") as f:
            json.dump(dj, f, ensure_ascii=False, indent=2)
        with open(tmp_yaml, "w", encoding="utf-8") as f:
            f.write(yaml_text)
        os.replace(tmp_json, DIR_JSON_PATH)
        os.replace(tmp_yaml, DIR_YAML_PATH)
    except (FileNotFoundError, PermissionError, OSError) as exc:
        # Fallback via system temp and report clearly
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json", encoding="utf-8") as tfj:
            json.dump(dj, tfj, ensure_ascii=False, indent=2)
            temp_json_out = tfj.name
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".yaml", encoding="utf-8") as tfy:
            tfy.write(yaml_text)
            temp_yaml_out = tfy.name
        try:
            os.replace(temp_json_out, DIR_JSON_PATH)
            os.replace(temp_yaml_out, DIR_YAML_PATH)
        except Exception as exc2:
            print(
                "ERROR: Unable to write feeds_directory outputs to target path.\n"
                f"JSON Target: {DIR_JSON_PATH}\nYAML Target: {DIR_YAML_PATH}\n"
                f"Original error: {exc!r}\n"
                f"Replace-from-temp failed: {exc2!r}\n"
                "Suggestion: Move the repo to a non-OneDrive folder or adjust permissions, then rerun.\n"
                f"Directory JSON written to temporary file: {temp_json_out}\n"
                f"Directory YAML written to temporary file: {temp_yaml_out}"
            )
    print("Updated feed_catalog.json and synchronised feeds_directory.{json,yaml}.")

if __name__ == "__main__":
    main()
