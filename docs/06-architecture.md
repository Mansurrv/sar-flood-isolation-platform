# DIP-6: System Architecture

## Overview
High-level architecture consisting of GeoSpatial Data Ingestion Pipeline, API Gateway, Tile Server, and Dashboard UI.

## Component Diagram
[User Dashboard] <--> [FastAPI Server] <--> [STAC API / AWS Sentinel-1]
|
[Processing Engine]
