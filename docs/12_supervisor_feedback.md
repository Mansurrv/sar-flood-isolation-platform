# Supervisor Feedback

**Supervisor:** Alua Myrzakerimova
**Project:** SAR Flood Mapping Platform
**Team:** Nurdaulet Aitynbek, Mansur Serikbai

## Overall Assessment and Progress

The team has done good work on the new version of the platform. The comprehensive approach is encouraging: the team did not simply implement the basic algorithms, but also integrated graph analysis (OSMnx/NetworkX) to assess settlement isolation (DIP-19). This is a very strong practical case for the examination committee. The architecture, with an asynchronous backend and a run history stored in SQLite, looks reliable and professional.

## What Has Been Done Well

- **Choice of algorithms (DIP-14 – DIP-18):** Using classical and adaptive Otsu thresholding together with change detection is the de facto standard for Sentinel-1 radar data. The logic is built correctly.
- **Organisation of work:** It is good that each task is handled in a separate branch and linked to YouTrack; the code is clean and tests have been prepared.
- **Interface:** GeoJSON upload and status indicators for asynchronous tasks make the interface intuitive.

## Current Status of Google Earth Engine

I understand the situation with the pending authorisation of the Google Cloud project. At this stage it is not critical: the main point is that the software pipeline is ready to accept real data. As soon as access is granted, the first run on real data should be carried out.

## Recommendations for the Next Version (for the Defence)

- Add tooltips to the interface with a short description of each algorithm, so that the committee immediately understands the difference between the methods during the defence.
- When displaying results on the map, show brief statistics: the flooded area (in km²) and the number of blocked road segments.

## Summary

A good interim result. The team should proceed to the final tests as soon as Google Earth Engine access is granted.
