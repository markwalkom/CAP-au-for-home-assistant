# CAP-au ingester for Home Assistant
Repo for future HACS package, that will enable ingest of Common Alerting Protocol (CAP) feeds following the CAP-au profile specification, to identify alerts relevant to a location for display and notification.

## What is CAP-au

From the [Bureau of Meterology](https://www.bom.gov.au/metadata/CAP-AU/About.shtml):

> CAP (and the Australian Profile of it: CAP-AU-STD) is a standardised data exchange format, using XML, that allows consistent and easy to understand emergency messages to be broadcast across a variety of communication systems. CAP can be used to alert and inform emergency response agencies, media and the general public.
> 
> CAP ensures that messages remain consistent and clearly indicate to the recipient the severity of the threat and best response.

# What CAP-au feeds are available?

This list of feeds is still under development. Please feel welcome to make a commit of you find a new CAP-au feed.

* National
	* [Geoscience Australia](https://earthquakes.ga.gov.au/feeds/all_recent.atom), [More Info](https://earthquakes.ga.gov.au) (tap on Notofications).
* Queensland
	* [Queensland Fire Deprtment](https://publiccontent-gis-psba-qld-gov-au.s3.amazonaws.com/content/Feeds/BushfireCurrentIncidents/bushfireAlert_capau.xml), [More Info](https://www.fire.qld.gov.au/Current-Incidents).
	* [Disaster Queensland](https://publiccontent-qld-alerts.s3.ap-southeast-2.amazonaws.com/content/Feeds/StormFloodCycloneWarnings/StormWarnings_capau.xml) - Severe Weather, Flood, Cyclone Warnings and Emergency Alerts, [More Info](https://www.disaster.qld.gov.au/current-warnings).
* Western Australia
	* [Emergency WA](https://api.emergency.wa.gov.au/v1/capau), [More Info)[https://www.emergency.wa.gov.au/about#rss].
